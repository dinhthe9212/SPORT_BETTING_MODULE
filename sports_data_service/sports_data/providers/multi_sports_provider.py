"""
Multi-Provider Sports Data Service
Tích hợp API-Sports, The-Odds-API, OpenLigaDB, TheSportsDB
Rotation system để tối ưu free tiers
Circuit Breaker Pattern để xử lý lỗi và failover
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import random

from .circuit_breaker import circuit_breaker, circuit_breaker_manager

logger = logging.getLogger(__name__)

class MultiSportsDataProvider:
    """
    Multi-provider sports data service with intelligent rotation
    Tự động chuyển đổi giữa các providers để tối ưu free credits
    """
    
    def __init__(self):
        self.providers = {
            'api_sports': APISportsProvider(),
            'odds_api': TheOddsAPIProvider(), 
            'openliga': OpenLigaDBProvider(),
            'thesportsdb': TheSportsDBProvider()
        }
        
        # Rotation weights (higher = higher priority)
        self.provider_weights = {
            'api_sports': 40,    # 100 requests/day free
            'odds_api': 30,      # 500 credits/month free  
            'openliga': 20,      # Unlimited but German only
            'thesportsdb': 10    # Limited data but unlimited
        }
        
        # Đăng ký Circuit Breakers cho tất cả providers
        self._register_circuit_breakers()
    
    def _register_circuit_breakers(self):
        """Đăng ký Circuit Breakers cho tất cả providers"""
        for provider_name, provider in self.providers.items():
            # Tạo Circuit Breaker cho mỗi provider
            cb = circuit_breaker(
                failure_threshold=3,  # Mở circuit sau 3 lần lỗi
                recovery_timeout=120,  # Thử khôi phục sau 2 phút
                name=f"sports_provider_{provider_name}"
            )
            
            # Áp dụng Circuit Breaker cho các methods chính
            provider.get_live_scores = cb(provider.get_live_scores)
            provider.get_odds = cb(provider.get_odds)
            provider.get_fixtures = cb(provider.get_fixtures)
            
            # Đăng ký với Circuit Breaker Manager
            circuit_breaker_manager.add_circuit_breaker(
                f"sports_provider_{provider_name}",
                provider.get_live_scores.circuit_breaker
            )
    
    def get_best_provider(self, data_type: str, sport: str = None) -> str:
        """
        Chọn provider tốt nhất dựa trên:
        - Số lượng requests còn lại
        - Loại dữ liệu cần
        - Môn thể thao
        - Trạng thái Circuit Breaker
        """
        available_providers = []
        
        for provider_name, provider in self.providers.items():
            # Kiểm tra Circuit Breaker status
            cb_name = f"sports_provider_{provider_name}"
            circuit_breaker = circuit_breaker_manager.get_circuit_breaker(cb_name)
            
            if circuit_breaker and circuit_breaker.state.value == 'OPEN':
                logger.warning(f"Provider {provider_name} circuit breaker is OPEN, skipping")
                continue
            
            if provider.is_available() and provider.supports_data_type(data_type, sport):
                remaining_quota = provider.get_remaining_quota()
                weight = self.provider_weights[provider_name]
                
                # Adjust weight based on remaining quota
                if remaining_quota > 0.8:  # >80% quota remaining
                    weight *= 1.5
                elif remaining_quota < 0.2:  # <20% quota remaining
                    weight *= 0.3
                
                # Adjust weight based on Circuit Breaker health
                if circuit_breaker:
                    if circuit_breaker.state.value == 'HALF_OPEN':
                        weight *= 0.5  # Giảm priority cho HALF_OPEN
                    elif circuit_breaker.failure_count > 0:
                        weight *= (1 - circuit_breaker.failure_count * 0.1)  # Giảm weight theo số lần lỗi
                    
                available_providers.append((provider_name, weight))
        
        if not available_providers:
            logger.warning("No providers available for data type: %s", data_type)
            return 'api_sports'  # fallback
            
        # Weighted random selection
        total_weight = sum(weight for _, weight in available_providers)
        random_weight = random.uniform(0, total_weight)
        
        current_weight = 0
        for provider_name, weight in available_providers:
            current_weight += weight
            if random_weight <= current_weight:
                return provider_name
                
        return available_providers[0][0]  # fallback
    
    def get_live_scores(self, sport: str) -> Dict[str, Any]:
        """Lấy tỷ số trực tiếp"""
        provider_name = self.get_best_provider('live_scores', sport)
        provider = self.providers[provider_name]
        
        try:
            data = provider.get_live_scores(sport)
            logger.info(f"Got live scores from {provider_name} for {sport}")
            return {
                'provider': provider_name,
                'data': data,
                'cached_at': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting live scores from {provider_name}: {e}")
            return self._fallback_request('live_scores', sport, exclude=[provider_name])
    
    def get_odds(self, sport: str, market: str = 'h2h') -> Dict[str, Any]:
        """Lấy tỷ lệ cược"""
        provider_name = self.get_best_provider('odds', sport)
        provider = self.providers[provider_name]
        
        try:
            data = provider.get_odds(sport, market)
            logger.info(f"Got odds from {provider_name} for {sport}/{market}")
            return {
                'provider': provider_name,
                'data': data,
                'cached_at': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting odds from {provider_name}: {e}")
            return self._fallback_request('odds', sport, exclude=[provider_name], market=market)
    
    def get_fixtures(self, sport: str, date: str = None) -> Dict[str, Any]:
        """Lấy lịch thi đấu"""
        provider_name = self.get_best_provider('fixtures', sport)
        provider = self.providers[provider_name]
        
        try:
            data = provider.get_fixtures(sport, date)
            logger.info(f"Got fixtures from {provider_name} for {sport}")
            return {
                'provider': provider_name,
                'data': data,
                'cached_at': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting fixtures from {provider_name}: {e}")
            return self._fallback_request('fixtures', sport, exclude=[provider_name], date=date)
    
    def _fallback_request(self, data_type: str, sport: str, exclude: List[str] = None, **kwargs):
        """Fallback khi provider chính fail"""
        exclude = exclude or []
        
        for provider_name, provider in self.providers.items():
            if provider_name in exclude:
                continue
                
            if provider.supports_data_type(data_type, sport):
                try:
                    if data_type == 'live_scores':
                        data = provider.get_live_scores(sport)
                    elif data_type == 'odds':
                        data = provider.get_odds(sport, kwargs.get('market', 'h2h'))
                    elif data_type == 'fixtures':
                        data = provider.get_fixtures(sport, kwargs.get('date'))
                    
                    logger.info(f"Fallback successful with {provider_name}")
                    return {
                        'provider': provider_name,
                        'data': data,
                        'cached_at': timezone.now().isoformat(),
                        'is_fallback': True
                    }
                except Exception as e:
                    logger.error(f"Fallback failed with {provider_name}: {e}")
                    continue
        
        logger.error(f"All providers failed for {data_type}/{sport}")
        return {'error': 'All providers failed', 'provider': None, 'data': None}
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Lấy trạng thái Circuit Breaker của tất cả providers"""
        return circuit_breaker_manager.get_all_health_status()
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Lấy tổng quan sức khỏe hệ thống"""
        return circuit_breaker_manager.get_system_health_summary()
    
    def force_reset_all_circuit_breakers(self):
        """Buộc reset tất cả Circuit Breakers"""
        circuit_breaker_manager.reset_all()
        logger.info("All Circuit Breakers have been reset")


class APISportsProvider:
    """
    API-Sports.io Provider
    Free: 100 requests/day per API
    Paid: $10/month for more requests
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'API_SPORTS_KEY', None)
        self.base_url = "https://v3.football.api-sports.io"
        self.daily_limit = 100  # Free tier
        
        # PAID OPTIONS - Uncomment khi upgrade
        # self.api_key = getattr(settings, 'API_SPORTS_PAID_KEY', None)
        # self.daily_limit = 1000  # Paid tier
    
    def is_available(self) -> bool:
        """Kiểm tra API key và quota"""
        if not self.api_key:
            return False
            
        # Check daily usage from cache
        cache_key = f"api_sports_usage_{datetime.now().strftime('%Y%m%d')}"
        current_usage = cache.get(cache_key, 0)
        return current_usage < self.daily_limit
    
    def get_remaining_quota(self) -> float:
        """Trả về % quota còn lại (0.0-1.0)"""
        cache_key = f"api_sports_usage_{datetime.now().strftime('%Y%m%d')}"
        current_usage = cache.get(cache_key, 0)
        return max(0, (self.daily_limit - current_usage) / self.daily_limit)
    
    def supports_data_type(self, data_type: str, sport: str = None) -> bool:
        """Kiểm tra hỗ trợ loại dữ liệu"""
        supported_types = ['live_scores', 'fixtures', 'odds', 'statistics']
        supported_sports = ['football', 'basketball', 'hockey', 'handball', 'volleyball']
        
        return (data_type in supported_types and 
                (sport is None or sport.lower() in supported_sports))
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Thực hiện API request"""
        headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        }
        
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            # Update usage counter
            cache_key = f"api_sports_usage_{datetime.now().strftime('%Y%m%d')}"
            current_usage = cache.get(cache_key, 0)
            cache.set(cache_key, current_usage + 1, 86400)  # 24 hours
            
            return response.json()
        else:
            raise Exception(f"API Sports error: {response.status_code} - {response.text}")
    
    def get_live_scores(self, sport: str) -> List[Dict]:
        """Lấy tỷ số trực tiếp"""
        endpoint = "/fixtures"
        params = {'live': 'all'}
        
        result = self._make_request(endpoint, params)
        return result.get('response', [])
    
    def get_fixtures(self, sport: str, date: str = None) -> List[Dict]:
        """Lấy lịch thi đấu"""
        endpoint = "/fixtures"
        params = {}
        
        if date:
            params['date'] = date
        else:
            params['next'] = '10'  # Next 10 fixtures
            
        result = self._make_request(endpoint, params)
        return result.get('response', [])
    
    def get_odds(self, sport: str, market: str = 'h2h') -> List[Dict]:
        """Lấy tỷ lệ cược"""
        # API-Sports không có odds data trong free tier
        # Trả về empty để fallback sang provider khác
        return []
    
    def get_markets(self, sport: str) -> List[Dict]:
        """Lấy danh sách các loại cược (markets) cho môn thể thao"""
        try:
            # Lấy fixtures để có match IDs
            fixtures = self.get_fixtures(sport)
            markets = []
            
            for fixture in fixtures[:5]:  # Giới hạn 5 fixtures để tiết kiệm API calls
                match_id = fixture.get('fixture', {}).get('id')
                if match_id:
                    # Lấy markets cho từng match
                    match_markets = self._get_match_markets(match_id, sport)
                    markets.extend(match_markets)
            
            return markets
            
        except Exception as e:
            logger.error(f"Error getting markets for {sport}: {str(e)}")
            return []
    
    def _get_match_markets(self, match_id: int, sport: str) -> List[Dict]:
        """Lấy markets cho một trận đấu cụ thể"""
        try:
            # Trong free tier, trả về markets cơ bản
            basic_markets = [
                {
                    'id': f"{match_id}_1x2",
                    'name': 'Match Result',
                    'type': '1X2',
                    'options': ['1', 'X', '2'],
                    'match_id': match_id,
                    'sport': sport
                },
                {
                    'id': f"{match_id}_over_under",
                    'name': 'Over/Under',
                    'type': 'TOTALS',
                    'options': ['Over', 'Under'],
                    'match_id': match_id,
                    'sport': sport
                }
            ]
            
            # Thêm markets theo môn thể thao
            if sport.lower() == 'football':
                basic_markets.extend([
                    {
                        'id': f"{match_id}_both_teams_score",
                        'name': 'Both Teams Score',
                        'type': 'BTTS',
                        'options': ['Yes', 'No'],
                        'match_id': match_id,
                        'sport': sport
                    },
                    {
                        'id': f"{match_id}_double_chance",
                        'name': 'Double Chance',
                        'type': 'DOUBLE_CHANCE',
                        'options': ['1X', '12', 'X2'],
                        'match_id': match_id,
                        'sport': sport
                    }
                ])
            
            return basic_markets
            
        except Exception as e:
            logger.error(f"Error getting markets for match {match_id}: {str(e)}")
            return []
    
    def get_team_info(self, team_id: int) -> Dict[str, Any]:
        """Lấy thông tin chi tiết về đội bóng"""
        try:
            endpoint = f"/teams?id={team_id}"
            result = self._make_request(endpoint)
            
            if result.get('response'):
                team_data = result['response'][0]
                return {
                    'id': team_data.get('team', {}).get('id'),
                    'name': team_data.get('team', {}).get('name'),
                    'country': team_data.get('team', {}).get('country'),
                    'founded': team_data.get('team', {}).get('founded'),
                    'national': team_data.get('team', {}).get('national'),
                    'logo': team_data.get('team', {}).get('logo'),
                    'venue': team_data.get('venue', {}).get('name') if team_data.get('venue') else None
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting team info for {team_id}: {str(e)}")
            return {}
    
    def get_league_info(self, league_id: int) -> Dict[str, Any]:
        """Lấy thông tin về giải đấu"""
        try:
            endpoint = f"/leagues?id={league_id}"
            result = self._make_request(endpoint)
            
            if result.get('response'):
                league_data = result['response'][0]
                return {
                    'id': league_data.get('league', {}).get('id'),
                    'name': league_data.get('league', {}).get('name'),
                    'country': league_data.get('country', {}).get('name'),
                    'type': league_data.get('league', {}).get('type'),
                    'logo': league_data.get('league', {}).get('logo'),
                    'flag': league_data.get('country', {}).get('flag')
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting league info for {league_id}: {str(e)}")
            return {}


class TheOddsAPIProvider:
    """
    The-Odds-API Provider  
    Free: 500 credits/month
    Paid: $30/month for 20K credits
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'ODDS_API_KEY', None)
        self.base_url = "https://api.the-odds-api.com/v4"
        self.monthly_limit = 500  # Free tier
        
        # PAID OPTIONS - Uncomment khi upgrade
        # self.api_key = getattr(settings, 'ODDS_API_PAID_KEY', None)
        # self.monthly_limit = 20000  # $30/month tier
    
    def is_available(self) -> bool:
        """Kiểm tra API key và quota"""
        if not self.api_key:
            return False
            
        # Check monthly usage from cache  
        cache_key = f"odds_api_usage_{datetime.now().strftime('%Y%m')}"
        current_usage = cache.get(cache_key, 0)
        return current_usage < self.monthly_limit
    
    def get_remaining_quota(self) -> float:
        """Trả về % quota còn lại"""
        cache_key = f"odds_api_usage_{datetime.now().strftime('%Y%m')}"
        current_usage = cache.get(cache_key, 0)
        return max(0, (self.monthly_limit - current_usage) / self.monthly_limit)
    
    def supports_data_type(self, data_type: str, sport: str = None) -> bool:
        """Kiểm tra hỗ trợ loại dữ liệu"""
        # The Odds API chủ yếu về odds data
        return data_type in ['odds']
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Thực hiện API request"""
        params = params or {}
        params['apiKey'] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            # Update usage counter
            cache_key = f"odds_api_usage_{datetime.now().strftime('%Y%m')}"
            current_usage = cache.get(cache_key, 0)
            cache.set(cache_key, current_usage + 1, 86400 * 30)  # 30 days
            
            return response.json()
        else:
            raise Exception(f"Odds API error: {response.status_code} - {response.text}")
    
    def get_odds(self, sport: str, market: str = 'h2h') -> List[Dict]:
        """Lấy tỷ lệ cược"""
        # Map sports to Odds API format
        sport_mapping = {
            'football': 'soccer_epl',  # English Premier League
            'basketball': 'basketball_nba',
            'american_football': 'americanfootball_nfl'
        }
        
        api_sport = sport_mapping.get(sport.lower(), sport)
        endpoint = f"/sports/{api_sport}/odds"
        
        params = {
            'regions': 'us,uk,eu',
            'markets': market,
            'oddsFormat': 'decimal'
        }
        
        return self._make_request(endpoint, params)
    
    def get_live_scores(self, sport: str) -> List[Dict]:
        """The Odds API không có live scores, return empty"""
        return []
    
    def get_fixtures(self, sport: str, date: str = None) -> List[Dict]:
        """The Odds API không có fixtures riêng, return empty"""
        return []
    
    def get_reference_odds(self, sport: str, match_id: str = None) -> Dict[str, Any]:
        """
        Lấy tỷ lệ cược tham khảo cho Admin Panel
        Không hiển thị cho người dùng cuối
        """
        try:
            odds_data = self.get_odds(sport, 'h2h')
            
            if not odds_data:
                return {}
            
            # Xử lý và chuẩn hóa dữ liệu odds
            reference_odds = {
                'sport': sport,
                'match_id': match_id,
                'timestamp': timezone.now().isoformat(),
                'source': 'the_odds_api',
                'markets': {}
            }
            
            for match_odds in odds_data:
                match_id = match_odds.get('id')
                if match_id:
                    reference_odds['markets'][match_id] = {
                        'home_team': match_odds.get('home_team'),
                        'away_team': match_odds.get('away_team'),
                        'commence_time': match_odds.get('commence_time'),
                        'bookmakers': {}
                    }
                    
                    # Xử lý bookmakers
                    for bookmaker in match_odds.get('bookmakers', []):
                        bookmaker_name = bookmaker.get('title')
                        markets = bookmaker.get('markets', [])
                        
                        for market in markets:
                            market_key = market.get('key')
                            if market_key == 'h2h':
                                reference_odds['markets'][match_id]['bookmakers'][bookmaker_name] = {
                                    'home_odds': None,
                                    'away_odds': None,
                                    'draw_odds': None
                                }
                                
                                for outcome in market.get('outcomes', []):
                                    if outcome.get('name') == match_odds.get('home_team'):
                                        reference_odds['markets'][match_id]['bookmakers'][bookmaker_name]['home_odds'] = outcome.get('price')
                                    elif outcome.get('name') == match_odds.get('away_team'):
                                        reference_odds['markets'][match_id]['bookmakers'][bookmaker_name]['away_odds'] = outcome.get('price')
                                    else:
                                        reference_odds['markets'][match_id]['bookmakers'][bookmaker_name]['draw_odds'] = outcome.get('price')
            
            return reference_odds
            
        except Exception as e:
            logger.error(f"Error getting reference odds for {sport}: {str(e)}")
            return {}
    
    def get_market_analysis(self, sport: str) -> Dict[str, Any]:
        """
        Phân tích thị trường cược cho Admin
        Cung cấp insights về tỷ lệ cược
        """
        try:
            # Lấy odds cho các markets khác nhau
            markets = ['h2h', 'spreads', 'totals']
            market_analysis = {
                'sport': sport,
                'timestamp': timezone.now().isoformat(),
                'market_insights': {},
                'bookmaker_comparison': {},
                'trends': {}
            }
            
            for market in markets:
                try:
                    odds_data = self.get_odds(sport, market)
                    if odds_data:
                        market_analysis['market_insights'][market] = {
                            'total_matches': len(odds_data),
                            'average_odds': self._calculate_average_odds(odds_data, market),
                            'odds_range': self._calculate_odds_range(odds_data, market)
                        }
                except Exception as e:
                    logger.warning(f"Could not get {market} data for {sport}: {str(e)}")
                    continue
            
            return market_analysis
            
        except Exception as e:
            logger.error(f"Error getting market analysis for {sport}: {str(e)}")
            return {}
    
    def _calculate_average_odds(self, odds_data: List[Dict], market: str) -> float:
        """Tính tỷ lệ cược trung bình"""
        try:
            total_odds = 0
            count = 0
            
            for match in odds_data:
                for bookmaker in match.get('bookmakers', []):
                    for market_data in bookmaker.get('markets', []):
                        if market_data.get('key') == market:
                            for outcome in market_data.get('outcomes', []):
                                odds = outcome.get('price')
                                if odds and isinstance(odds, (int, float)):
                                    total_odds += odds
                                    count += 1
            
            return round(total_odds / count, 2) if count > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average odds: {str(e)}")
            return 0.0
    
    def _calculate_odds_range(self, odds_data: List[Dict], market: str) -> Dict[str, float]:
        """Tính khoảng tỷ lệ cược (min, max)"""
        try:
            all_odds = []
            
            for match in odds_data:
                for bookmaker in match.get('bookmakers', []):
                    for market_data in bookmaker.get('markets', []):
                        if market_data.get('key') == market:
                            for outcome in market_data.get('outcomes', []):
                                odds = outcome.get('price')
                                if odds and isinstance(odds, (int, float)):
                                    all_odds.append(odds)
            
            if all_odds:
                return {
                    'min': min(all_odds),
                    'max': max(all_odds)
                }
            
            return {'min': 0.0, 'max': 0.0}
            
        except Exception as e:
            logger.error(f"Error calculating odds range: {str(e)}")
            return {'min': 0.0, 'max': 0.0}


class OpenLigaDBProvider:
    """
    OpenLigaDB Provider
    Free: Unlimited requests
    Coverage: German leagues only
    """
    
    def __init__(self):
        self.base_url = "https://api.openligadb.de"
        # No API key required
    
    def is_available(self) -> bool:
        """Always available"""
        return True
    
    def get_remaining_quota(self) -> float:
        """Unlimited quota"""
        return 1.0
    
    def supports_data_type(self, data_type: str, sport: str = None) -> bool:
        """Chỉ hỗ trợ German football"""
        return (data_type in ['live_scores', 'fixtures'] and
                sport and 'german' in sport.lower())
    
    def _make_request(self, endpoint: str) -> Dict:
        """Thực hiện API request"""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"OpenLigaDB error: {response.status_code}")
    
    def get_live_scores(self, sport: str) -> List[Dict]:
        """Lấy tỷ số trực tiếp Bundesliga"""
        endpoint = "/getmatchdata/bl1/2024"  # Bundesliga 2024
        return self._make_request(endpoint)
    
    def get_fixtures(self, sport: str, date: str = None) -> List[Dict]:
        """Lấy lịch thi đấu Bundesliga"""
        endpoint = "/getmatchdata/bl1/2024"
        return self._make_request(endpoint)
    
    def get_odds(self, sport: str, market: str = 'h2h') -> List[Dict]:
        """OpenLigaDB không có odds data"""
        return []


class TheSportsDBProvider:
    """
    TheSportsDB Provider
    Free: Unlimited requests
    Coverage: Limited data, good for basic info
    """
    
    def __init__(self):
        self.base_url = "https://www.thesportsdb.com/api/v1/json"
        self.api_key = "3"  # Free tier key
        
        # PAID OPTIONS - Uncomment khi có Patreon subscription
        # self.api_key = getattr(settings, 'THESPORTSDB_PAID_KEY', "3")
    
    def is_available(self) -> bool:
        """Always available"""
        return True
    
    def get_remaining_quota(self) -> float:
        """Unlimited quota"""
        return 1.0
    
    def supports_data_type(self, data_type: str, sport: str = None) -> bool:
        """Hỗ trợ basic data cho nhiều sports"""
        return data_type in ['fixtures', 'live_scores']
    
    def _make_request(self, endpoint: str) -> Dict:
        """Thực hiện API request"""
        url = f"{self.base_url}/{self.api_key}{endpoint}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"TheSportsDB error: {response.status_code}")
    
    def get_live_scores(self, sport: str) -> List[Dict]:
        """Lấy tỷ số trực tiếp"""
        endpoint = "/livescore.php"
        result = self._make_request(endpoint)
        return result.get('events', [])
    
    def get_fixtures(self, sport: str, date: str = None) -> List[Dict]:
        """Lấy lịch thi đấu"""
        if date:
            endpoint = f"/eventsday.php?d={date}&s={sport}"
        else:
            endpoint = f"/eventsnext.php?id=4328"  # Premier League ID
            
        result = self._make_request(endpoint)
        return result.get('events', [])
    
    def get_odds(self, sport: str, market: str = 'h2h') -> List[Dict]:
        """TheSportsDB không có odds data"""
        return []


# Usage Example:
"""
# Initialize multi-provider service
sports_service = MultiSportsDataProvider()

# Get live scores - automatically chooses best provider
live_data = sports_service.get_live_scores('football')

# Get odds - uses providers that support odds
odds_data = sports_service.get_odds('football', 'h2h')

# Get fixtures
fixtures_data = sports_service.get_fixtures('football', '2024-12-20')
"""

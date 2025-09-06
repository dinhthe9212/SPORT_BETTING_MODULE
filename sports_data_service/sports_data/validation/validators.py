from django.utils.translation import gettext_lazy as _
import re
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class SportsDataValidator:
    """Validator chính cho dữ liệu thể thao"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_match_data(self, data: Dict[str, Any]) -> bool:
        """Validate dữ liệu trận đấu"""
        self.errors = []
        self.warnings = []
        
        # Required fields
        required_fields = ['home_team', 'away_team', 'sport', 'start_time']
        for field in required_fields:
            if field not in data or not data[field]:
                self.errors.append(f"Field '{field}' is required")
        
        if self.errors:
            return False
        
        # Validate team names
        if not self._validate_team_name(data.get('home_team', '')):
            self.errors.append("Invalid home team name format")
        
        if not self._validate_team_name(data.get('away_team', '')):
            self.errors.append("Invalid away team name format")
        
        # Validate sport
        if not self._validate_sport(data.get('sport', '')):
            self.errors.append("Invalid sport type")
        
        # Validate start time
        if not self._validate_start_time(data.get('start_time')):
            self.errors.append("Invalid start time")
        
        # Validate scores
        if 'home_score' in data and not self._validate_score(data['home_score']):
            self.errors.append("Invalid home score")
        
        if 'away_score' in data and not self._validate_score(data['away_score']):
            self.errors.append("Invalid away score")
        
        # Validate match status
        if 'status' in data and not self._validate_match_status(data['status']):
            self.errors.append("Invalid match status")
        
        # Validate odds data if present
        if 'odds' in data:
            self._validate_odds_data(data['odds'])
        
        return len(self.errors) == 0
    
    def validate_odds_data(self, data: Dict[str, Any]) -> bool:
        """Validate dữ liệu tỷ lệ cược"""
        self.errors = []
        self.warnings = []
        
        # Required fields
        required_fields = ['match_id', 'provider', 'odds_type']
        for field in required_fields:
            if field not in data or not data[field]:
                self.errors.append(f"Field '{field}' is required")
        
        if self.errors:
            return False
        
        # Validate odds values
        if 'home_odds' in data and not self._validate_odds_value(data['home_odds']):
            self.errors.append("Invalid home odds value")
        
        if 'away_odds' in data and not self._validate_odds_value(data['away_odds']):
            self.errors.append("Invalid away odds value")
        
        if 'draw_odds' in data and not self._validate_odds_value(data['draw_odds']):
            self.errors.append("Invalid draw odds value")
        
        # Validate provider
        if not self._validate_provider(data.get('provider', '')):
            self.errors.append("Invalid provider name")
        
        # Validate odds type
        if not self._validate_odds_type(data.get('odds_type', '')):
            self.errors.append("Invalid odds type")
        
        return len(self.errors) == 0
    
    def validate_team_data(self, data: Dict[str, Any]) -> bool:
        """Validate dữ liệu đội bóng"""
        self.errors = []
        self.warnings = []
        
        # Required fields
        required_fields = ['name', 'sport', 'country']
        for field in required_fields:
            if field not in data or not data[field]:
                self.errors.append(f"Field '{field}' is required")
        
        if self.errors:
            return False
        
        # Validate team name
        if not self._validate_team_name(data.get('name', '')):
            self.errors.append("Invalid team name format")
        
        # Validate sport
        if not self._validate_sport(data.get('sport', '')):
            self.errors.append("Invalid sport type")
        
        # Validate country
        if not self._validate_country(data.get('country', '')):
            self.errors.append("Invalid country name")
        
        # Validate league if present
        if 'league' in data and not self._validate_league_name(data['league']):
            self.warnings.append("League name format could be improved")
        
        return len(self.errors) == 0
    
    def validate_league_data(self, data: Dict[str, Any]) -> bool:
        """Validate dữ liệu giải đấu"""
        self.errors = []
        self.warnings = []
        
        # Required fields
        required_fields = ['name', 'sport', 'country']
        for field in required_fields:
            if field not in data or not data[field]:
                self.errors.append(f"Field '{field}' is required")
        
        if self.errors:
            return False
        
        # Validate league name
        if not self._validate_league_name(data.get('name', '')):
            self.errors.append("Invalid league name format")
        
        # Validate sport
        if not self._validate_sport(data.get('sport', '')):
            self.errors.append("Invalid sport type")
        
        # Validate country
        if not self._validate_country(data.get('country', '')):
            self.errors.append("Invalid country name")
        
        # Validate season format if present
        if 'season' in data and not self._validate_season_format(data['season']):
            self.warnings.append("Season format could be improved")
        
        return len(self.errors) == 0
    
    def _validate_team_name(self, name: str) -> bool:
        """Validate tên đội bóng"""
        if not name or len(name.strip()) < 2:
            return False
        
        # Kiểm tra ký tự đặc biệt không hợp lệ
        invalid_chars = re.findall(r'[<>{}[\]\\|`~!@#$%^&*+=]', name)
        if invalid_chars:
            return False
        
        # Kiểm tra độ dài tối đa
        if len(name.strip()) > 100:
            return False
        
        return True
    
    def _validate_sport(self, sport: str) -> bool:
        """Validate loại thể thao"""
        valid_sports = [
            'football', 'basketball', 'tennis', 'baseball', 'hockey',
            'volleyball', 'rugby', 'cricket', 'golf', 'boxing',
            'mma', 'ufc', 'formula1', 'motogp', 'cycling'
        ]
        
        return sport.lower() in valid_sports
    
    def _validate_start_time(self, start_time) -> bool:
        """Validate thời gian bắt đầu trận đấu"""
        try:
            if isinstance(start_time, str):
                # Parse string to datetime
                datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            elif isinstance(start_time, datetime):
                # Already a datetime object
                pass
            else:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def _validate_score(self, score) -> bool:
        """Validate điểm số"""
        try:
            score_int = int(score)
            return 0 <= score_int <= 999  # Giới hạn hợp lý
        except (ValueError, TypeError):
            return False
    
    def _validate_match_status(self, status: str) -> bool:
        """Validate trạng thái trận đấu"""
        valid_statuses = [
            'scheduled', 'live', 'finished', 'cancelled', 'postponed',
            'suspended', 'abandoned', 'half_time', 'full_time'
        ]
        
        return status.lower() in valid_statuses
    
    def _validate_odds_value(self, odds) -> bool:
        """Validate giá trị tỷ lệ cược"""
        try:
            odds_float = float(odds)
            return 1.0 <= odds_float <= 1000.0  # Giới hạn hợp lý
        except (ValueError, TypeError):
            return False
    
    def _validate_provider(self, provider: str) -> bool:
        """Validate tên provider"""
        valid_providers = [
            'api-sports', 'the-odds-api', 'openligadb', 'thesportsdb'
        ]
        
        return provider.lower() in valid_providers
    
    def _validate_odds_type(self, odds_type: str) -> bool:
        """Validate loại tỷ lệ cược"""
        valid_types = [
            '1x2', 'over_under', 'handicap', 'both_teams_score',
            'correct_score', 'first_goal_scorer', 'corner_kicks'
        ]
        
        return odds_type.lower() in valid_types
    
    def _validate_country(self, country: str) -> bool:
        """Validate tên quốc gia"""
        if not country or len(country.strip()) < 2:
            return False
        
        # Kiểm tra ký tự đặc biệt
        invalid_chars = re.findall(r'[<>{}[\]\\|`~!@#$%^&*+=]', country)
        if invalid_chars:
            return False
        
        return len(country.strip()) <= 50
    
    def _validate_league_name(self, name: str) -> bool:
        """Validate tên giải đấu"""
        if not name or len(name.strip()) < 3:
            return False
        
        # Kiểm tra ký tự đặc biệt
        invalid_chars = re.findall(r'[<>{}[\]\\|`~!@#$%^&*+=]', name)
        if invalid_chars:
            return False
        
        return len(name.strip()) <= 100
    
    def _validate_season_format(self, season: str) -> bool:
        """Validate định dạng mùa giải"""
        # Kiểm tra format: 2023/2024 hoặc 2023-2024
        season_pattern = r'^\d{4}[/-]\d{4}$'
        return bool(re.match(season_pattern, season))
    
    def _validate_odds_data(self, odds_data: Dict[str, Any]):
        """Validate dữ liệu odds (internal method)"""
        if not isinstance(odds_data, dict):
            self.warnings.append("Odds data should be a dictionary")
            return
        
        # Kiểm tra các trường cơ bản
        if 'home_odds' in odds_data and not self._validate_odds_value(odds_data['home_odds']):
            self.warnings.append("Home odds value format could be improved")
        
        if 'away_odds' in odds_data and not self._validate_odds_value(odds_data['away_odds']):
            self.warnings.append("Away odds value format could be improved")
    
    def get_errors(self) -> List[str]:
        """Lấy danh sách lỗi"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Lấy danh sách cảnh báo"""
        return self.warnings
    
    def has_errors(self) -> bool:
        """Kiểm tra có lỗi không"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Kiểm tra có cảnh báo không"""
        return len(self.warnings) > 0
    
    def clear(self):
        """Xóa tất cả lỗi và cảnh báo"""
        self.errors = []
        self.warnings = []

class DataQualityChecker:
    """Kiểm tra chất lượng dữ liệu"""
    
    @staticmethod
    def check_data_completeness(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Kiểm tra tính đầy đủ của dữ liệu"""
        missing_fields = []
        present_fields = []
        
        for field in required_fields:
            if field in data and data[field] is not None:
                present_fields.append(field)
            else:
                missing_fields.append(field)
        
        completeness_rate = len(present_fields) / len(required_fields) * 100
        
        return {
            'completeness_rate': completeness_rate,
            'missing_fields': missing_fields,
            'present_fields': present_fields,
            'total_fields': len(required_fields),
            'is_complete': completeness_rate == 100
        }
    
    @staticmethod
    def check_data_consistency(data: Dict[str, Any]) -> Dict[str, Any]:
        """Kiểm tra tính nhất quán của dữ liệu"""
        inconsistencies = []
        
        # Kiểm tra tính nhất quán của scores
        if 'home_score' in data and 'away_score' in data:
            home_score = data['home_score']
            away_score = data['away_score']
            
            if isinstance(home_score, (int, float)) and isinstance(away_score, (int, float)):
                if home_score < 0 or away_score < 0:
                    inconsistencies.append("Negative scores are not valid")
        
        # Kiểm tra tính nhất quán của odds
        if 'home_odds' in data and 'away_odds' in data:
            home_odds = data['home_odds']
            away_odds = data['away_odds']
            
            if isinstance(home_odds, (int, float)) and isinstance(away_odds, (int, float)):
                if home_odds <= 1.0 or away_odds <= 1.0:
                    inconsistencies.append("Odds values should be greater than 1.0")
        
        # Kiểm tra tính nhất quán của thời gian
        if 'start_time' in data and 'end_time' in data:
            try:
                start_time = data['start_time']
                end_time = data['end_time']
                
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                if start_time >= end_time:
                    inconsistencies.append("Start time should be before end time")
                    
            except (ValueError, TypeError):
                inconsistencies.append("Invalid time format")
        
        return {
            'has_inconsistencies': len(inconsistencies) > 0,
            'inconsistencies': inconsistencies,
            'consistency_score': max(0, 100 - len(inconsistencies) * 20)  # Trừ 20 điểm cho mỗi inconsistency
        }
    
    @staticmethod
    def check_data_freshness(data: Dict[str, Any], max_age_hours: int = 24) -> Dict[str, Any]:
        """Kiểm tra tính mới của dữ liệu"""
        if 'last_updated' not in data:
            return {
                'is_fresh': False,
                'age_hours': None,
                'status': 'unknown'
            }
        
        try:
            last_updated = data['last_updated']
            if isinstance(last_updated, str):
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            
            now = datetime.utcnow()
            age_hours = (now - last_updated).total_seconds() / 3600
            
            is_fresh = age_hours <= max_age_hours
            
            if age_hours <= 1:
                status = 'very_fresh'
            elif age_hours <= 6:
                status = 'fresh'
            elif age_hours <= 24:
                status = 'recent'
            else:
                status = 'stale'
            
            return {
                'is_fresh': is_fresh,
                'age_hours': age_hours,
                'status': status,
                'max_age_hours': max_age_hours
            }
            
        except (ValueError, TypeError):
            return {
                'is_fresh': False,
                'age_hours': None,
                'status': 'error'
            }

# Global instances
sports_data_validator = SportsDataValidator()
data_quality_checker = DataQualityChecker()

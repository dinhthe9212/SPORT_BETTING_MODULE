"""
Advanced Analytics Service for Carousel - Rule-based (NO AI/ML)
Sử dụng statistical methods và business rules thay vì machine learning
Cost: $0 (Pure Python statistical analysis)
"""

import statistics
from datetime import timedelta
from typing import Dict, List, Any, Optional
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from .models import FeaturedEvent, UserProductPurchase
from collections import defaultdict, Counter
import logging

logger = logging.getLogger('carousel')


class CarouselAnalyticsService:
    """
    Rule-based analytics service cho carousel
    Không sử dụng AI/ML - chỉ statistical analysis
    """
    
    @staticmethod
    def get_trending_items(hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Tìm trending items dựa trên statistical patterns
        
        Args:
            hours: Số giờ để phân tích (default: 24h)
            limit: Số lượng items trả về
            
        Returns:
            List các items đang trending với trend score
        """
        try:
            since = timezone.now() - timedelta(hours=hours)
            
            # Get purchase data cho period
            recent_purchases = UserProductPurchase.objects.filter(
                purchased_at__gte=since
            ).values('featured_event').annotate(
                purchase_count=Count('id'),
                unique_users=Count('user', distinct=True),
                total_stake=Sum('stake_amount'),
                avg_stake=Avg('stake_amount')
            )
            
            # Calculate trend score dựa trên multiple factors
            trending_items = []
            
            for purchase_data in recent_purchases:
                event_id = purchase_data['featured_event']
                
                try:
                    item = FeaturedEvent.objects.get(id=event_id, is_active=True)
                except FeaturedEvent.DoesNotExist:
                    continue
                
                # Rule-based scoring (không phải ML)
                trend_score = CarouselAnalyticsService._calculate_trend_score(
                    purchase_count=purchase_data['purchase_count'],
                    unique_users=purchase_data['unique_users'],
                    total_stake=float(purchase_data['total_stake'] or 0),
                    avg_stake=float(purchase_data['avg_stake'] or 0),
                    item_popularity=item.popularity_score,
                    hours=hours
                )
                
                trending_items.append({
                    'item_id': item.id,
                    'title': item.title,
                    'trend_score': trend_score,
                    'purchase_count': purchase_data['purchase_count'],
                    'unique_users': purchase_data['unique_users'],
                    'total_stake': float(purchase_data['total_stake'] or 0),
                    'avg_stake': float(purchase_data['avg_stake'] or 0),
                    'current_odds': float(item.current_odds),
                    'popularity_score': item.popularity_score
                })
            
            # Sort by trend score và return top items
            trending_items.sort(key=lambda x: x['trend_score'], reverse=True)
            return trending_items[:limit]
            
        except Exception as e:
            logger.error(f"Error calculating trending items: {e}")
            return []
    
    @staticmethod
    def _calculate_trend_score(purchase_count: int, unique_users: int, 
                             total_stake: float, avg_stake: float,
                             item_popularity: int, hours: int) -> float:
        """
        Calculate trend score using business rules (không phải ML)
        
        Formula: Weighted combination của các factors
        """
        # Normalize các metrics
        purchase_velocity = purchase_count / hours  # purchases per hour
        user_diversity = unique_users / max(purchase_count, 1)  # unique users ratio
        stake_intensity = avg_stake / 1000  # normalized stake intensity
        popularity_factor = item_popularity / 100  # normalized popularity
        
        # Weighted scoring (business rules)
        trend_score = (
            purchase_velocity * 0.4 +      # 40% weight on velocity
            user_diversity * 0.3 +         # 30% weight on user diversity  
            stake_intensity * 0.2 +        # 20% weight on stake intensity
            popularity_factor * 0.1        # 10% weight on base popularity
        )
        
        return round(trend_score, 2)
    
    @staticmethod
    def get_user_behavior_patterns(user_id: Optional[int] = None, 
                                 days: int = 30) -> Dict[str, Any]:
        """
        Phân tích behavior patterns của users bằng statistical methods
        
        Args:
            user_id: ID của user cụ thể (None = all users)
            days: Số ngày để phân tích
            
        Returns:
            Dict chứa behavior analytics
        """
        try:
            since = timezone.now() - timedelta(days=days)
            
            # Base queryset
            purchases_qs = UserProductPurchase.objects.filter(purchased_at__gte=since)
            
            if user_id:
                purchases_qs = purchases_qs.filter(user_id=user_id)
            
            # Basic statistics
            total_purchases = purchases_qs.count()
            if total_purchases == 0:
                return {'no_data': True}
            
            # Time-based patterns
            time_patterns = CarouselAnalyticsService._analyze_time_patterns(purchases_qs)
            
            # Stake patterns
            stake_patterns = CarouselAnalyticsService._analyze_stake_patterns(purchases_qs)
            
            # Event preferences
            event_patterns = CarouselAnalyticsService._analyze_event_preferences(purchases_qs)
            
            return {
                'period_days': days,
                'total_purchases': total_purchases,
                'time_patterns': time_patterns,
                'stake_patterns': stake_patterns,
                'event_patterns': event_patterns,
                'summary': CarouselAnalyticsService._generate_behavior_summary(
                    time_patterns, stake_patterns, event_patterns, total_purchases
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def _analyze_time_patterns(purchases_qs) -> Dict[str, Any]:
        """Phân tích time-based patterns"""
        purchases = list(purchases_qs.values('purchased_at'))
        
        if not purchases:
            return {}
        
        # Hour distribution
        hours = [p['purchased_at'].hour for p in purchases]
        hour_distribution = Counter(hours)
        peak_hour = hour_distribution.most_common(1)[0][0]
        
        # Day of week distribution
        weekdays = [p['purchased_at'].weekday() for p in purchases]
        weekday_distribution = Counter(weekdays)
        peak_day = weekday_distribution.most_common(1)[0][0]
        
        # Session patterns (purchases within 2 hours = same session)
        sessions = []
        sorted_purchases = sorted(purchases, key=lambda x: x['purchased_at'])
        
        current_session = []
        for purchase in sorted_purchases:
            if not current_session:
                current_session.append(purchase)
            else:
                time_diff = purchase['purchased_at'] - current_session[-1]['purchased_at']
                if time_diff.total_seconds() <= 7200:  # 2 hours
                    current_session.append(purchase)
                else:
                    if current_session:
                        sessions.append(len(current_session))
                    current_session = [purchase]
        
        if current_session:
            sessions.append(len(current_session))
        
        return {
            'peak_hour': peak_hour,
            'hour_distribution': dict(hour_distribution),
            'peak_day': peak_day,  # 0=Monday, 6=Sunday
            'weekday_distribution': dict(weekday_distribution),
            'avg_session_length': statistics.mean(sessions) if sessions else 0,
            'total_sessions': len(sessions)
        }
    
    @staticmethod
    def _analyze_stake_patterns(purchases_qs) -> Dict[str, Any]:
        """Phân tích stake patterns"""
        stakes = list(purchases_qs.values_list('stake_amount', flat=True))
        
        if not stakes:
            return {}
        
        stakes_float = [float(s) for s in stakes]
        
        return {
            'avg_stake': round(statistics.mean(stakes_float), 2),
            'median_stake': round(statistics.median(stakes_float), 2),
            'min_stake': round(min(stakes_float), 2),
            'max_stake': round(max(stakes_float), 2),
            'std_deviation': round(statistics.stdev(stakes_float) if len(stakes_float) > 1 else 0, 2),
            'stake_consistency': CarouselAnalyticsService._calculate_consistency(stakes_float),
            'stake_trend': CarouselAnalyticsService._calculate_stake_trend(stakes_float)
        }
    
    @staticmethod
    def _analyze_event_preferences(purchases_qs) -> Dict[str, Any]:
        """Phân tích event preferences"""
        events = purchases_qs.values('featured_event__title').annotate(
            count=Count('id'),
            avg_stake=Avg('stake_amount'),
            total_stake=Sum('stake_amount')
        ).order_by('-count')
        
        if not events:
            return {}
        
        top_events = list(events[:5])
        total_purchases = sum(e['count'] for e in events)
        
        return {
            'top_events': top_events,
            'event_diversity': len(events),
            'concentration_ratio': top_events[0]['count'] / total_purchases if top_events else 0,
            'preferred_categories': CarouselAnalyticsService._categorize_events(top_events)
        }
    
    @staticmethod
    def _calculate_consistency(values: List[float]) -> str:
        """Calculate consistency score cho values"""
        if len(values) <= 1:
            return 'insufficient_data'
        
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values)
        coefficient_of_variation = std_dev / abs(mean_val) if mean_val != 0 else float('inf')
        
        if coefficient_of_variation < 0.2:
            return 'very_consistent'
        elif coefficient_of_variation < 0.5:
            return 'consistent'
        elif coefficient_of_variation < 1.0:
            return 'moderate'
        else:
            return 'inconsistent'
    
    @staticmethod
    def _calculate_stake_trend(stakes: List[float]) -> str:
        """Calculate trend direction cho stakes over time"""
        if len(stakes) < 3:
            return 'insufficient_data'
        
        # Simple trend analysis - compare first half vs second half
        mid_point = len(stakes) // 2
        first_half_avg = statistics.mean(stakes[:mid_point])
        second_half_avg = statistics.mean(stakes[mid_point:])
        
        change_ratio = (second_half_avg - first_half_avg) / first_half_avg
        
        if change_ratio > 0.1:
            return 'increasing'
        elif change_ratio < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    @staticmethod
    def _categorize_events(events: List[Dict]) -> Dict[str, int]:
        """Categorize events by simple keyword matching"""
        categories = defaultdict(int)
        
        for event in events:
            title = event['featured_event__title'].lower()
            count = event['count']
            
            # Simple keyword-based categorization
            if any(keyword in title for keyword in ['football', 'soccer', 'bóng đá']):
                categories['football'] += count
            elif any(keyword in title for keyword in ['basketball', 'bóng rổ']):
                categories['basketball'] += count
            elif any(keyword in title for keyword in ['tennis']):
                categories['tennis'] += count
            elif any(keyword in title for keyword in ['boxing', 'mma', 'fight']):
                categories['combat_sports'] += count
            else:
                categories['other'] += count
        
        return dict(categories)
    
    @staticmethod
    def _generate_behavior_summary(time_patterns: Dict, stake_patterns: Dict, 
                                 event_patterns: Dict, total_purchases: int) -> List[str]:
        """Generate human-readable behavior summary"""
        summary = []
        
        # Time-based insights
        if 'peak_hour' in time_patterns:
            hour = time_patterns['peak_hour']
            if 6 <= hour <= 11:
                summary.append("User is a morning bettor")
            elif 12 <= hour <= 17:
                summary.append("User prefers afternoon betting")
            elif 18 <= hour <= 23:
                summary.append("User is an evening bettor")
            else:
                summary.append("User bets during off-peak hours")
        
        # Stake-based insights
        if 'stake_consistency' in stake_patterns:
            consistency = stake_patterns['stake_consistency']
            if consistency in ['very_consistent', 'consistent']:
                summary.append("User has consistent betting patterns")
            elif consistency == 'inconsistent':
                summary.append("User has varied betting patterns")
        
        if 'avg_stake' in stake_patterns:
            avg_stake = stake_patterns['avg_stake']
            if avg_stake > 500000:  # 500k VND
                summary.append("High-value bettor")
            elif avg_stake > 100000:  # 100k VND
                summary.append("Medium-value bettor")
            else:
                summary.append("Conservative bettor")
        
        # Activity insights
        if total_purchases > 50:
            summary.append("Highly active user")
        elif total_purchases > 10:
            summary.append("Regular user")
        else:
            summary.append("Casual user")
        
        return summary
    
    @staticmethod
    def get_conversion_analytics(days: int = 7) -> Dict[str, Any]:
        """
        Phân tích conversion funnel bằng statistical methods
        
        Args:
            days: Số ngày để phân tích
            
        Returns:
            Dict chứa conversion analytics
        """
        try:
            since = timezone.now() - timedelta(days=days)
            
            # Get all views/interactions (từ cache hoặc logs)
            # Ở đây chúng ta sẽ estimate từ purchase data
            
            purchases = UserProductPurchase.objects.filter(purchased_at__gte=since)
            total_purchases = purchases.count()
            
            if total_purchases == 0:
                return {'no_data': True}
            
            # Status distribution
            status_distribution = purchases.values('status').annotate(
                count=Count('id')
            )
            
            # Device type patterns (estimate từ creation time patterns)
            hourly_distribution = purchases.extra(
                select={'hour': 'EXTRACT(hour FROM purchased_at)'}
            ).values('hour').annotate(count=Count('id'))
            
            # Calculate estimated conversion rates
            confirmed_purchases = purchases.filter(status='CONFIRMED').count()
            conversion_rate = (confirmed_purchases / total_purchases) * 100 if total_purchases > 0 else 0
            
            return {
                'period_days': days,
                'total_purchases': total_purchases,
                'conversion_rate': round(conversion_rate, 2),
                'status_distribution': {item['status']: item['count'] for item in status_distribution},
                'hourly_activity': {item['hour']: item['count'] for item in hourly_distribution},
                'insights': CarouselAnalyticsService._generate_conversion_insights(
                    conversion_rate, status_distribution, total_purchases
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating conversion analytics: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def _generate_conversion_insights(conversion_rate: float, status_dist: List[Dict], 
                                    total_purchases: int) -> List[str]:
        """Generate conversion insights"""
        insights = []
        
        if conversion_rate > 80:
            insights.append("Excellent conversion rate")
        elif conversion_rate > 60:
            insights.append("Good conversion rate")
        elif conversion_rate > 40:
            insights.append("Average conversion rate")
        else:
            insights.append("Low conversion rate - needs optimization")
        
        # Analyze pending purchases
        pending_count = sum(item['count'] for item in status_dist if item['status'] == 'PENDING')
        pending_rate = (pending_count / total_purchases) * 100 if total_purchases > 0 else 0
        
        if pending_rate > 20:
            insights.append("High pending rate - payment flow needs optimization")
        
        return insights

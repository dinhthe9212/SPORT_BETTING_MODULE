import logging
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    IndividualBookmaker, RiskEducationTutorial, TutorialProgress,
    RiskAlert, BookmakerPerformance
)

logger = logging.getLogger(__name__)


class BookmakerDashboardService:
    """Service cho Dashboard của Individual Bookmaker"""
    
    def get_dashboard_data(self, user_id):
        """Lấy dữ liệu dashboard cho user"""
        try:
            # Lấy thông tin bookmaker
            bookmaker = IndividualBookmaker.objects.filter(user_id=user_id).first()
            if not bookmaker:
                return self._create_default_dashboard(user_id)
            
            # Lấy alerts gần đây
            recent_alerts = RiskAlert.objects.filter(
                user_id=user_id,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).order_by('-created_at')[:5]
            
            # Lấy tiến độ tutorial
            tutorial_progress = TutorialProgress.objects.filter(
                user_id=user_id
            ).select_related('tutorial')[:5]
            
            # Tính toán performance summary
            performance_summary = self._calculate_performance_summary(user_id)
            
            # Tính toán risk overview
            risk_overview = self._calculate_risk_overview(bookmaker)
            
            return {
                'user_info': {
                    'id': bookmaker.id,
                    'user_id': bookmaker.user_id,
                    'status': bookmaker.status,
                    'risk_level': bookmaker.risk_level,
                    'risk_score': bookmaker.risk_score,
                    'performance_score': bookmaker.performance_score,
                    'total_bets': bookmaker.total_bets,
                    'win_rate': bookmaker.win_rate,
                    'total_profit': bookmaker.total_profit
                },
                'recent_alerts': [
                    {
                        'id': alert.id,
                        'alert_type': alert.alert_type,
                        'severity': alert.severity,
                        'title': alert.title,
                        'message': alert.message,
                        'is_read': alert.is_read,
                        'created_at': alert.created_at
                    } for alert in recent_alerts
                ],
                'tutorial_progress': [
                    {
                        'id': progress.id,
                        'tutorial': {
                            'id': progress.tutorial.id,
                            'title': progress.tutorial.title,
                            'category': progress.tutorial.category
                        },
                        'progress_percentage': progress.progress_percentage,
                        'is_completed': progress.is_completed
                    } for progress in tutorial_progress
                ],
                'performance_summary': performance_summary,
                'risk_overview': risk_overview
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data for user {user_id}: {str(e)}")
            raise
    
    def _create_default_dashboard(self, user_id):
        """Tạo dashboard mặc định cho user mới"""
        return {
            'user_info': {
                'user_id': user_id,
                'status': 'ACTIVE',
                'risk_level': 'LOW',
                'risk_score': 0.0,
                'performance_score': 0.0,
                'total_bets': 0,
                'win_rate': 0.0,
                'total_profit': 0.0
            },
            'recent_alerts': [],
            'tutorial_progress': [],
            'performance_summary': {
                'total_bets': 0,
                'win_rate': 0.0,
                'profit_trend': 'stable',
                'risk_trend': 'stable'
            },
            'risk_overview': {
                'current_level': 'LOW',
                'trend': 'stable',
                'recommendations': ['Bắt đầu với tutorials cơ bản']
            }
        }
    
    def _calculate_performance_summary(self, user_id):
        """Tính toán performance summary"""
        try:
            # Lấy dữ liệu performance gần đây
            recent_performance = BookmakerPerformance.objects.filter(
                user_id=user_id,
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            
            if not recent_performance.exists():
                return {
                    'total_bets': 0,
                    'win_rate': 0.0,
                    'profit_trend': 'stable',
                    'risk_trend': 'stable'
                }
            
            # Tính toán trends
            avg_score = recent_performance.aggregate(Avg('performance_score'))['performance_score__avg']
            
            return {
                'total_bets': recent_performance.count(),
                'win_rate': avg_score or 0.0,
                'profit_trend': 'increasing' if avg_score > 50 else 'decreasing',
                'risk_trend': 'stable'
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance summary: {str(e)}")
            return {
                'total_bets': 0,
                'win_rate': 0.0,
                'profit_trend': 'stable',
                'risk_trend': 'stable'
            }
    
    def _calculate_risk_overview(self, bookmaker):
        """Tính toán risk overview"""
        try:
            risk_level = bookmaker.risk_level
            risk_score = bookmaker.risk_score
            
            # Xác định trend dựa trên risk score
            if risk_score < 30:
                trend = 'decreasing'
            elif risk_score > 70:
                trend = 'increasing'
            else:
                trend = 'stable'
            
            # Tạo recommendations dựa trên risk level
            recommendations = self._get_risk_recommendations(risk_level)
            
            return {
                'current_level': risk_level,
                'trend': trend,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk overview: {str(e)}")
            return {
                'current_level': 'LOW',
                'trend': 'stable',
                'recommendations': ['Không thể tính toán risk overview']
            }
    
    def _get_risk_recommendations(self, risk_level):
        """Lấy recommendations dựa trên risk level"""
        recommendations_map = {
            'LOW': [
                'Tiếp tục duy trì chiến lược hiện tại',
                'Tham gia tutorials nâng cao',
                'Theo dõi performance metrics'
            ],
            'MEDIUM': [
                'Xem xét lại chiến lược cá cược',
                'Hoàn thành tutorials về quản lý rủi ro',
                'Giảm kích thước cược'
            ],
            'HIGH': [
                'Tạm dừng cá cược mới',
                'Hoàn thành tutorials cơ bản',
                'Liên hệ support team'
            ],
            'CRITICAL': [
                'Dừng tất cả hoạt động cá cược',
                'Liên hệ support team ngay lập tức',
                'Xem xét tài khoản'
            ]
        }
        
        return recommendations_map.get(risk_level, ['Không có recommendations'])


class RiskEducationService:
    """Service cho Risk Education System"""
    
    def get_user_tutorials(self, user_id):
        """Lấy tutorials cho user"""
        try:
            # Lấy tất cả tutorials active
            all_tutorials = RiskEducationTutorial.objects.filter(is_active=True)
            
            # Lấy tiến độ của user
            user_progress = TutorialProgress.objects.filter(user_id=user_id)
            progress_dict = {p.tutorial_id: p for p in user_progress}
            
            # Tạo danh sách tutorials với tiến độ
            tutorials_data = []
            for tutorial in all_tutorials:
                progress = progress_dict.get(tutorial.id)
                if progress:
                    tutorials_data.append({
                        'id': tutorial.id,
                        'title': tutorial.title,
                        'description': tutorial.description,
                        'category': tutorial.category,
                        'difficulty_level': tutorial.difficulty_level,
                        'duration_minutes': tutorial.duration_minutes,
                        'progress_percentage': progress.progress_percentage,
                        'is_completed': progress.is_completed,
                        'completed_at': progress.completed_at
                    })
                else:
                    # Tạo progress mới cho tutorial chưa học
                    tutorials_data.append({
                        'id': tutorial.id,
                        'title': tutorial.title,
                        'description': tutorial.description,
                        'category': tutorial.category,
                        'difficulty_level': tutorial.difficulty_level,
                        'duration_minutes': tutorial.duration_minutes,
                        'progress_percentage': 0,
                        'is_completed': False,
                        'completed_at': None
                    })
            
            return tutorials_data
            
        except Exception as e:
            logger.error(f"Error getting user tutorials for user {user_id}: {str(e)}")
            raise
    
    def mark_tutorial_completed(self, user_id, tutorial_id):
        """Đánh dấu tutorial hoàn thành"""
        try:
            # Lấy hoặc tạo progress
            progress, created = TutorialProgress.objects.get_or_create(
                user_id=user_id,
                tutorial_id=tutorial_id,
                defaults={
                    'progress_percentage': 100,
                    'is_completed': True,
                    'completed_at': timezone.now()
                }
            )
            
            if not created:
                # Cập nhật progress hiện tại
                progress.progress_percentage = 100
                progress.is_completed = True
                progress.completed_at = timezone.now()
                progress.save()
            
            # Cập nhật performance score
            self._update_education_performance(user_id)
            
            return {
                'success': True,
                'message': 'Tutorial marked as completed',
                'progress': {
                    'id': progress.id,
                    'progress_percentage': progress.progress_percentage,
                    'is_completed': progress.is_completed,
                    'completed_at': progress.completed_at
                }
            }
            
        except Exception as e:
            logger.error(f"Error marking tutorial completed: {str(e)}")
            raise
    
    def _update_education_performance(self, user_id):
        """Cập nhật performance score dựa trên education progress"""
        try:
            # Tính toán completion rate
            total_tutorials = RiskEducationTutorial.objects.filter(is_active=True).count()
            completed_tutorials = TutorialProgress.objects.filter(
                user_id=user_id,
                is_completed=True
            ).count()
            
            if total_tutorials > 0:
                completion_rate = (completed_tutorials / total_tutorials) * 100
                
                # Cập nhật performance score
                bookmaker = IndividualBookmaker.objects.filter(user_id=user_id).first()
                if bookmaker:
                    # Tăng performance score dựa trên education progress
                    education_bonus = min(completion_rate * 0.5, 20)  # Tối đa 20 điểm
                    bookmaker.performance_score = min(
                        bookmaker.performance_score + education_bonus, 100
                    )
                    bookmaker.save()
                    
        except Exception as e:
            logger.error(f"Error updating education performance: {str(e)}")


class RiskAlertService:
    """Service cho Risk Alert Management"""
    
    def get_risk_overview(self, user_id):
        """Lấy risk overview cho user"""
        try:
            bookmaker = IndividualBookmaker.objects.filter(user_id=user_id).first()
            if not bookmaker:
                return self._get_default_risk_overview()
            
            # Lấy alerts gần đây
            recent_alerts = RiskAlert.objects.filter(
                user_id=user_id,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('-created_at')
            
            # Tính toán risk trend
            risk_trend = self._calculate_risk_trend(bookmaker)
            
            # Tạo recommendations
            recommendations = self._generate_risk_recommendations(bookmaker, recent_alerts)
            
            return {
                'current_risk_level': bookmaker.risk_level,
                'risk_score': bookmaker.risk_score,
                'risk_trend': risk_trend,
                'recent_alerts': [
                    {
                        'id': alert.id,
                        'alert_type': alert.alert_type,
                        'severity': alert.severity,
                        'title': alert.title,
                        'message': alert.message,
                        'is_read': alert.is_read,
                        'created_at': alert.created_at
                    } for alert in recent_alerts[:10]
                ],
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting risk overview for user {user_id}: {str(e)}")
            raise
    
    def get_user_alerts(self, user_id):
        """Lấy alerts cho user"""
        try:
            alerts = RiskAlert.objects.filter(user_id=user_id).order_by('-created_at')
            
            return [
                {
                    'id': alert.id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'title': alert.title,
                    'message': alert.message,
                    'is_read': alert.is_read,
                    'created_at': alert.created_at
                } for alert in alerts
            ]
            
        except Exception as e:
            logger.error(f"Error getting user alerts for user {user_id}: {str(e)}")
            raise
    
    def mark_alert_read(self, user_id, alert_id):
        """Đánh dấu alert đã đọc"""
        try:
            alert = RiskAlert.objects.filter(
                user_id=user_id,
                id=alert_id
            ).first()
            
            if not alert:
                raise ValueError("Alert not found")
            
            alert.is_read = True
            alert.read_at = timezone.now()
            alert.save()
            
            return {
                'success': True,
                'message': 'Alert marked as read',
                'alert_id': alert.id
            }
            
        except Exception as e:
            logger.error(f"Error marking alert read: {str(e)}")
            raise
    
    def _get_default_risk_overview(self):
        """Lấy risk overview mặc định"""
        return {
            'current_risk_level': 'LOW',
            'risk_score': 0.0,
            'risk_trend': 'stable',
            'recent_alerts': [],
            'recommendations': ['Bắt đầu với tutorials cơ bản']
        }
    
    def _calculate_risk_trend(self, bookmaker):
        """Tính toán risk trend"""
        try:
            # Lấy performance history
            performance_history = BookmakerPerformance.objects.filter(
                user_id=bookmaker.user_id
            ).order_by('-created_at')[:5]
            
            if len(performance_history) < 2:
                return 'stable'
            
            # So sánh performance gần đây
            recent_score = performance_history[0].performance_score
            previous_score = performance_history[1].performance_score
            
            if recent_score > previous_score + 10:
                return 'improving'
            elif recent_score < previous_score - 10:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error calculating risk trend: {str(e)}")
            return 'stable'
    
    def _generate_risk_recommendations(self, bookmaker, recent_alerts):
        """Tạo recommendations dựa trên risk level và alerts"""
        recommendations = []
        
        # Recommendations dựa trên risk level
        if bookmaker.risk_level in ['HIGH', 'CRITICAL']:
            recommendations.append('Giảm kích thước cược ngay lập tức')
            recommendations.append('Hoàn thành tutorials về quản lý rủi ro')
            recommendations.append('Liên hệ support team để được tư vấn')
        
        # Recommendations dựa trên alerts
        unread_alerts = recent_alerts.filter(is_read=False)
        if unread_alerts.exists():
            recommendations.append(f'Có {unread_alerts.count()} cảnh báo chưa đọc')
        
        # Recommendations chung
        if bookmaker.performance_score < 50:
            recommendations.append('Tập trung vào tutorials cơ bản')
        
        if not recommendations:
            recommendations.append('Tiếp tục duy trì chiến lược hiện tại')
        
        return recommendations


class PerformanceAnalyticsService:
    """Service cho Performance Analytics"""
    
    def get_user_performance(self, user_id):
        """Lấy performance data cho user"""
        try:
            bookmaker = IndividualBookmaker.objects.filter(user_id=user_id).first()
            if not bookmaker:
                return self._get_default_performance()
            
            # Lấy performance history
            performance_history = BookmakerPerformance.objects.filter(
                user_id=user_id
            ).order_by('-created_at')[:12]  # 12 tháng gần nhất
            
            # Tính toán trends
            trend_data = self._calculate_trend_data(performance_history)
            
            # So sánh với benchmarks
            comparison_data = self._calculate_comparison_data(bookmaker)
            
            # Tạo improvement suggestions
            improvement_suggestions = self._generate_improvement_suggestions(
                bookmaker, performance_history
            )
            
            return {
                'overall_score': bookmaker.performance_score,
                'trend_data': trend_data,
                'comparison_data': comparison_data,
                'improvement_suggestions': improvement_suggestions
            }
            
        except Exception as e:
            logger.error(f"Error getting user performance for user {user_id}: {str(e)}")
            raise
    
    def _get_default_performance(self):
        """Lấy performance mặc định"""
        return {
            'overall_score': 0.0,
            'trend_data': [],
            'comparison_data': {
                'peer_average': 0.0,
                'industry_average': 0.0,
                'percentile': 0
            },
            'improvement_suggestions': ['Bắt đầu với tutorials cơ bản']
        }
    
    def _calculate_trend_data(self, performance_history):
        """Tính toán trend data"""
        try:
            trend_data = []
            for performance in performance_history:
                trend_data.append({
                    'period': performance.period,
                    'score': performance.performance_score,
                    'type': performance.performance_type,
                    'date': performance.created_at.strftime('%Y-%m-%d')
                })
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error calculating trend data: {str(e)}")
            return []
    
    def _calculate_comparison_data(self, bookmaker):
        """Tính toán comparison data"""
        try:
            # Tính toán peer average (giả định)
            peer_average = 65.0  # Trong thực tế sẽ query từ database
            
            # Industry average (giả định)
            industry_average = 60.0
            
            # Tính percentile
            if peer_average > 0:
                percentile = min((bookmaker.performance_score / peer_average) * 100, 100)
            else:
                percentile = 0
            
            return {
                'peer_average': peer_average,
                'industry_average': industry_average,
                'percentile': round(percentile, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating comparison data: {str(e)}")
            return {
                'peer_average': 0.0,
                'industry_average': 0.0,
                'percentile': 0
            }
    
    def _generate_improvement_suggestions(self, bookmaker, performance_history):
        """Tạo improvement suggestions"""
        suggestions = []
        
        # Suggestions dựa trên performance score
        if bookmaker.performance_score < 30:
            suggestions.append('Hoàn thành tutorials cơ bản về quản lý rủi ro')
            suggestions.append('Giảm kích thước cược')
            suggestions.append('Tập trung vào một loại cược cụ thể')
        elif bookmaker.performance_score < 60:
            suggestions.append('Tham gia tutorials nâng cao')
            suggestions.append('Phân tích patterns trong lịch sử cược')
            suggestions.append('Thiết lập stop-loss limits')
        elif bookmaker.performance_score < 80:
            suggestions.append('Tối ưu hóa chiến lược cá cược')
            suggestions.append('Tham gia advanced risk management courses')
            suggestions.append('Mentoring với experienced bookmakers')
        else:
            suggestions.append('Duy trì performance hiện tại')
            suggestions.append('Chia sẻ kinh nghiệm với cộng đồng')
            suggestions.append('Tham gia elite bookmaker programs')
        
        # Suggestions dựa trên trends
        if performance_history:
            recent_trend = self._analyze_recent_trend(performance_history)
            if recent_trend == 'declining':
                suggestions.append('Xem xét lại chiến lược gần đây')
                suggestions.append('Tạm dừng cá cược mới để phân tích')
        
        return suggestions
    
    def _analyze_recent_trend(self, performance_history):
        """Phân tích trend gần đây"""
        try:
            if len(performance_history) < 3:
                return 'stable'
            
            recent_scores = [p.performance_score for p in performance_history[:3]]
            
            # Kiểm tra trend
            if recent_scores[0] > recent_scores[1] > recent_scores[2]:
                return 'improving'
            elif recent_scores[0] < recent_scores[1] < recent_scores[2]:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error analyzing recent trend: {str(e)}")
            return 'stable'

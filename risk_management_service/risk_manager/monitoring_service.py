"""
Advanced Monitoring Service cho Risk Management
Real-time metrics, performance monitoring, và alerting
"""

import logging
from datetime import timedelta
from typing import Dict, Any
from decimal import Decimal
from django.utils import timezone
from django.core.cache import cache
from django.db import connection
from django.db.models import Avg, Count, Max, Min
import psutil

from .models import (
    RiskAlert, RiskMetrics, RiskAuditLog, RiskConfiguration,
    CircuitBreakerEvent, TradingSuspension
)

logger = logging.getLogger('risk_monitoring')

class RiskMonitoringService:
    """Service monitoring toàn diện cho Risk Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_monitoring')
        self.metrics_cache_timeout = 300  # 5 phút
        self.alert_thresholds = self._load_alert_thresholds()
    
    def _load_alert_thresholds(self) -> Dict:
        """Load ngưỡng cảnh báo từ configuration"""
        try:
            config = RiskConfiguration.objects.get(
                config_key='monitoring_alert_thresholds',
                is_active=True
            )
            return config.config_value
        except RiskConfiguration.DoesNotExist:
            # Default thresholds
            return {
                'response_time_warning': 1000,      # 1 giây
                'response_time_critical': 5000,     # 5 giây
                'error_rate_warning': 5.0,          # 5%
                'error_rate_critical': 15.0,        # 15%
                'memory_usage_warning': 80.0,       # 80%
                'memory_usage_critical': 95.0,      # 95%
                'cpu_usage_warning': 70.0,          # 70%
                'cpu_usage_critical': 90.0,         # 90%
                'database_connections_warning': 80,  # 80 connections
                'database_connections_critical': 95  # 95 connections
            }
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Thu thập metrics hệ thống"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database metrics
            db_metrics = self._get_database_metrics()
            
            # Application metrics
            app_metrics = self._get_application_metrics()
            
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_percent': disk.percent,
                    'disk_free_gb': round(disk.free / (1024**3), 2)
                },
                'database': db_metrics,
                'application': app_metrics,
                'risk_management': self._get_risk_management_metrics()
            }
            
            # Cache metrics
            cache.set('system_metrics', metrics, self.metrics_cache_timeout)
            
            # Check thresholds và tạo alerts
            self._check_thresholds_and_alert(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {'error': str(e)}
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """Lấy metrics database"""
        try:
            with connection.cursor() as cursor:
                # Active connections
                cursor.execute("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE state = 'active'
                """)
                active_connections = cursor.fetchone()[0]
                
                # Database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                db_size = cursor.fetchone()[0]
                
                # Slow queries (last hour)
                cursor.execute("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE state = 'active' 
                    AND query_start < NOW() - INTERVAL '1 hour'
                    AND query NOT LIKE '%pg_stat_activity%'
                """)
                slow_queries = cursor.fetchone()[0]
                
                return {
                    'active_connections': active_connections,
                    'database_size': db_size,
                    'slow_queries_last_hour': slow_queries,
                    'connection_pool_usage': round((active_connections / 100) * 100, 2)
                }
                
        except Exception as e:
            self.logger.warning(f"Error getting database metrics: {e}")
            return {
                'active_connections': 0,
                'database_size': 'Unknown',
                'slow_queries_last_hour': 0,
                'connection_pool_usage': 0.0
            }
    
    def _get_application_metrics(self) -> Dict[str, Any]:
        """Lấy metrics ứng dụng"""
        try:
            # Risk check performance
            recent_checks = RiskAuditLog.objects.filter(
                action_type='RISK_CHECK',
                created_at__gte=timezone.now() - timedelta(hours=1)
            )
            
            total_checks = recent_checks.count()
            successful_checks = recent_checks.filter(
                action_details__risk_result__approved=True
            ).count()
            
            error_rate = 0.0
            if total_checks > 0:
                error_rate = round(((total_checks - successful_checks) / total_checks) * 100, 2)
            
            # Response time metrics
            response_times = []
            for check in recent_checks[:100]:  # Last 100 checks
                if 'response_time' in check.action_details:
                    response_times.append(check.action_details['response_time'])
            
            avg_response_time = 0.0
            max_response_time = 0.0
            if response_times:
                avg_response_time = round(sum(response_times) / len(response_times), 2)
                max_response_time = max(response_times)
            
            return {
                'total_risk_checks_last_hour': total_checks,
                'successful_checks': successful_checks,
                'error_rate_percent': error_rate,
                'average_response_time_ms': avg_response_time,
                'max_response_time_ms': max_response_time,
                'checks_per_minute': round(total_checks / 60, 2)
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting application metrics: {e}")
            return {
                'total_risk_checks_last_hour': 0,
                'successful_checks': 0,
                'error_rate_percent': 0.0,
                'average_response_time_ms': 0.0,
                'max_response_time_ms': 0.0,
                'checks_per_minute': 0.0
            }
    
    def _get_risk_management_metrics(self) -> Dict[str, Any]:
        """Lấy metrics riêng cho Risk Management"""
        try:
            # Circuit breaker status
            active_circuit_breakers = CircuitBreakerEvent.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            # Trading suspensions
            active_suspensions = TradingSuspension.objects.filter(
                status='ACTIVE'
            ).count()
            
            # Risk alerts
            active_alerts = RiskAlert.objects.filter(
                status='ACTIVE'
            ).count()
            
            # High risk alerts
            high_risk_alerts = RiskAlert.objects.filter(
                status='ACTIVE',
                severity__in=['HIGH', 'CRITICAL']
            ).count()
            
            # Liability exposure
            liability_metrics = self._get_liability_exposure_metrics()
            
            return {
                'active_circuit_breakers_24h': active_circuit_breakers,
                'active_trading_suspensions': active_suspensions,
                'active_risk_alerts': active_alerts,
                'high_risk_alerts': high_risk_alerts,
                'liability_exposure': liability_metrics
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting risk management metrics: {e}")
            return {
                'active_circuit_breakers_24h': 0,
                'active_trading_suspensions': 0,
                'active_risk_alerts': 0,
                'high_risk_alerts': 0,
                'liability_exposure': {}
            }
    
    def _get_liability_exposure_metrics(self) -> Dict[str, Any]:
        """Lấy metrics về liability exposure"""
        try:
            # Recent liability calculations
            recent_liability_logs = RiskAuditLog.objects.filter(
                action_type='LIABILITY_CALCULATION',
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).order_by('-created_at')[:50]
            
            total_exposure = Decimal('0.00')
            max_exposure = Decimal('0.00')
            exposure_count = 0
            
            for log in recent_liability_logs:
                if 'liability_amount' in log.action_details:
                    amount = Decimal(str(log.action_details['liability_amount']))
                    total_exposure += amount
                    max_exposure = max(max_exposure, amount)
                    exposure_count += 1
            
            avg_exposure = Decimal('0.00')
            if exposure_count > 0:
                avg_exposure = total_exposure / exposure_count
            
            return {
                'total_exposure': float(total_exposure),
                'average_exposure': float(avg_exposure),
                'max_exposure': float(max_exposure),
                'exposure_count': exposure_count
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting liability exposure metrics: {e}")
            return {
                'total_exposure': 0.0,
                'average_exposure': 0.0,
                'max_exposure': 0.0,
                'exposure_count': 0
            }
    
    def _check_thresholds_and_alert(self, metrics: Dict[str, Any]):
        """Kiểm tra thresholds và tạo alerts"""
        try:
            # System thresholds
            if metrics['system']['cpu_percent'] > self.alert_thresholds['cpu_usage_critical']:
                self._create_system_alert('CRITICAL', 'CPU Usage Critical', 
                    f"CPU usage: {metrics['system']['cpu_percent']}%")
            
            elif metrics['system']['cpu_percent'] > self.alert_thresholds['cpu_usage_warning']:
                self._create_system_alert('HIGH', 'CPU Usage High', 
                    f"CPU usage: {metrics['system']['cpu_percent']}%")
            
            if metrics['system']['memory_percent'] > self.alert_thresholds['memory_usage_critical']:
                self._create_system_alert('CRITICAL', 'Memory Usage Critical', 
                    f"Memory usage: {metrics['system']['memory_percent']}%")
            
            elif metrics['system']['memory_percent'] > self.alert_thresholds['memory_usage_warning']:
                self._create_system_alert('HIGH', 'Memory Usage High', 
                    f"Memory usage: {metrics['system']['memory_percent']}%")
            
            # Database thresholds
            if metrics['database']['active_connections'] > self.alert_thresholds['database_connections_critical']:
                self._create_system_alert('CRITICAL', 'Database Connections Critical', 
                    f"Active connections: {metrics['database']['active_connections']}")
            
            elif metrics['database']['active_connections'] > self.alert_thresholds['database_connections_warning']:
                self._create_system_alert('HIGH', 'Database Connections High', 
                    f"Active connections: {metrics['database']['active_connections']}")
            
            # Application thresholds
            if metrics['application']['error_rate_percent'] > self.alert_thresholds['error_rate_critical']:
                self._create_system_alert('CRITICAL', 'Error Rate Critical', 
                    f"Error rate: {metrics['application']['error_rate_percent']}%")
            
            elif metrics['application']['error_rate_percent'] > self.alert_thresholds['error_rate_warning']:
                self._create_system_alert('HIGH', 'Error Rate High', 
                    f"Error rate: {metrics['application']['error_rate_percent']}%")
            
            if metrics['application']['average_response_time_ms'] > self.alert_thresholds['response_time_critical']:
                self._create_system_alert('CRITICAL', 'Response Time Critical', 
                    f"Average response time: {metrics['application']['average_response_time_ms']}ms")
            
            elif metrics['application']['average_response_time_ms'] > self.alert_thresholds['response_time_warning']:
                self._create_system_alert('HIGH', 'Response Time High', 
                    f"Average response time: {metrics['application']['average_response_time_ms']}ms")
            
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
    
    def _create_system_alert(self, severity: str, title: str, message: str):
        """Tạo system alert"""
        try:
            # Kiểm tra xem alert đã tồn tại chưa
            existing_alert = RiskAlert.objects.filter(
                alert_type='SYSTEM_ANOMALY',
                title=title,
                status='ACTIVE'
            ).first()
            
            if not existing_alert:
                RiskAlert.objects.create(
                    alert_type='SYSTEM_ANOMALY',
                    severity=severity,
                    title=title,
                    message=message,
                    related_data={
                        'alert_source': 'monitoring_service',
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                self.logger.warning(f"System alert created: {title} - {message}")
                
                # Gửi notification nếu cần
                self._send_notification(severity, title, message)
                
        except Exception as e:
            self.logger.error(f"Error creating system alert: {e}")
    
    def _send_notification(self, severity: str, title: str, message: str):
        """Gửi notification cho admin"""
        try:
            # Gửi email notification
            if severity in ['HIGH', 'CRITICAL']:
                self._send_email_notification(severity, title, message)
            
            # Gửi Slack/Teams notification
            if severity == 'CRITICAL':
                self._send_slack_notification(severity, title, message)
                
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    def _send_email_notification(self, severity: str, title: str, message: str):
        """Gửi email notification"""
        # TODO: Implement email notification
        pass
    
    def _send_slack_notification(self, severity: str, title: str, message: str):
        """Gửi Slack notification"""
        # TODO: Implement Slack notification
        pass
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Tạo báo cáo hiệu suất"""
        try:
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Performance metrics
            performance_metrics = RiskMetrics.objects.filter(
                metric_type='SYSTEM_PERFORMANCE',
                timestamp__gte=start_time,
                timestamp__lte=end_time
            ).aggregate(
                avg_response_time=Avg('metric_value'),
                max_response_time=Max('metric_value'),
                min_response_time=Min('metric_value')
            )
            
            # Error metrics
            error_metrics = RiskAuditLog.objects.filter(
                action_type='RISK_CHECK',
                created_at__gte=start_time,
                created_at__lte=end_time
            ).aggregate(
                total_requests=Count('id'),
                error_requests=Count('id', filter={'action_details__risk_result__approved': False})
            )
            
            # Calculate error rate
            total_requests = error_metrics['total_requests'] or 0
            error_requests = error_metrics['error_requests'] or 0
            error_rate = 0.0
            if total_requests > 0:
                error_rate = round((error_requests / total_requests) * 100, 2)
            
            # Availability calculation
            availability = 100.0 - error_rate
            
            report = {
                'period': f"Last {hours} hours",
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'performance': {
                    'average_response_time_ms': round(performance_metrics['avg_response_time'] or 0, 2),
                    'max_response_time_ms': round(performance_metrics['max_response_time'] or 0, 2),
                    'min_response_time_ms': round(performance_metrics['min_response_time'] or 0, 2)
                },
                'reliability': {
                    'total_requests': total_requests,
                    'error_requests': error_requests,
                    'error_rate_percent': error_rate,
                    'availability_percent': availability
                },
                'system_health': self._get_system_health_summary()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
    
    def _get_system_health_summary(self) -> Dict[str, str]:
        """Tạo summary về system health"""
        try:
            # Get current metrics
            current_metrics = cache.get('system_metrics')
            if not current_metrics:
                return {'status': 'UNKNOWN', 'message': 'No metrics available'}
            
            # Check critical issues
            if (current_metrics['system']['cpu_percent'] > self.alert_thresholds['cpu_usage_critical'] or
                current_metrics['system']['memory_percent'] > self.alert_thresholds['memory_usage_critical']):
                return {
                    'status': 'CRITICAL',
                    'message': 'System resources critically low'
                }
            
            # Check high issues
            if (current_metrics['system']['cpu_percent'] > self.alert_thresholds['cpu_usage_warning'] or
                current_metrics['system']['memory_percent'] > self.alert_thresholds['memory_usage_warning']):
                return {
                    'status': 'WARNING',
                    'message': 'System resources running high'
                }
            
            # Check application health
            if current_metrics['application']['error_rate_percent'] > self.alert_thresholds['error_rate_critical']:
                return {
                    'status': 'CRITICAL',
                    'message': 'High error rate detected'
                }
            
            if current_metrics['application']['error_rate_percent'] > self.alert_thresholds['error_rate_warning']:
                return {
                    'status': 'WARNING',
                    'message': 'Elevated error rate'
                }
            
            return {
                'status': 'HEALTHY',
                'message': 'All systems operating normally'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system health summary: {e}")
            return {'status': 'ERROR', 'message': f'Error: {str(e)}'}
    
    def start_monitoring(self):
        """Bắt đầu monitoring service"""
        try:
            self.logger.info("Starting Risk Monitoring Service...")
            
            # Collect initial metrics
            self.collect_system_metrics()
            
            # Schedule periodic collection
            # TODO: Implement with Celery or similar task scheduler
            
            self.logger.info("Risk Monitoring Service started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring service: {e}")
    
    def stop_monitoring(self):
        """Dừng monitoring service"""
        try:
            self.logger.info("Stopping Risk Monitoring Service...")
            # TODO: Implement cleanup logic
            self.logger.info("Risk Monitoring Service stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring service: {e}")


class PerformanceOptimizer:
    """Service tối ưu hiệu suất dựa trên metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance_optimizer')
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> Dict:
        """Load rules tối ưu hiệu suất"""
        try:
            config = RiskConfiguration.objects.get(
                config_key='performance_optimization_rules',
                is_active=True
            )
            return config.config_value
        except RiskConfiguration.DoesNotExist:
            # Default optimization rules
            return {
                'cache_optimization': {
                    'enabled': True,
                    'cache_timeout_multiplier': 1.5,
                    'max_cache_size_mb': 100
                },
                'database_optimization': {
                    'enabled': True,
                    'query_timeout_ms': 5000,
                    'max_connections': 50
                },
                'response_optimization': {
                    'enabled': True,
                    'compression_enabled': True,
                    'batch_size': 100
                }
            }
    
    def optimize_based_on_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hệ thống dựa trên metrics"""
        try:
            optimizations = {}
            
            # Cache optimization
            if self.optimization_rules['cache_optimization']['enabled']:
                cache_optimizations = self._optimize_cache(metrics)
                optimizations['cache'] = cache_optimizations
            
            # Database optimization
            if self.optimization_rules['database_optimization']['enabled']:
                db_optimizations = self._optimize_database(metrics)
                optimizations['database'] = db_optimizations
            
            # Response optimization
            if self.optimization_rules['response_optimization']['enabled']:
                response_optimizations = self._optimize_response(metrics)
                optimizations['response'] = response_optimizations
            
            # Apply optimizations
            self._apply_optimizations(optimizations)
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"Error optimizing based on metrics: {e}")
            return {'error': str(e)}
    
    def _optimize_cache(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu cache settings"""
        optimizations = {}
        
        try:
            # Check memory usage
            memory_percent = metrics['system']['memory_percent']
            
            if memory_percent > 80:
                # Reduce cache size
                new_cache_timeout = int(self.optimization_rules['cache_optimization']['cache_timeout_multiplier'] * 300)
                cache.set('cache_timeout', new_cache_timeout, 3600)
                
                optimizations['cache_timeout_reduced'] = {
                    'reason': 'High memory usage',
                    'new_timeout': new_cache_timeout,
                    'old_timeout': 300
                }
            
            # Check cache hit rate
            cache_hit_rate = self._calculate_cache_hit_rate()
            if cache_hit_rate < 70:
                # Increase cache timeout
                new_cache_timeout = int(300 * 1.2)
                cache.set('cache_timeout', new_cache_timeout, 3600)
                
                optimizations['cache_timeout_increased'] = {
                    'reason': 'Low cache hit rate',
                    'new_timeout': new_cache_timeout,
                    'old_timeout': 300
                }
            
        except Exception as e:
            self.logger.warning(f"Error optimizing cache: {e}")
        
        return optimizations
    
    def _optimize_database(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu database settings"""
        optimizations = {}
        
        try:
            # Check database connections
            active_connections = metrics['database']['active_connections']
            max_connections = self.optimization_rules['database_optimization']['max_connections']
            
            if active_connections > max_connections * 0.8:
                # Optimize query timeouts
                new_timeout = int(self.optimization_rules['database_optimization']['query_timeout_ms'] * 0.8)
                
                optimizations['query_timeout_reduced'] = {
                    'reason': 'High database connections',
                    'new_timeout': new_timeout,
                    'old_timeout': self.optimization_rules['database_optimization']['query_timeout_ms']
                }
            
        except Exception as e:
            self.logger.warning(f"Error optimizing database: {e}")
        
        return optimizations
    
    def _optimize_response(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu response settings"""
        optimizations = {}
        
        try:
            # Check response times
            avg_response_time = metrics['application']['average_response_time_ms']
            
            if avg_response_time > 2000:  # 2 seconds
                # Enable compression
                if not self.optimization_rules['response_optimization']['compression_enabled']:
                    optimizations['compression_enabled'] = {
                        'reason': 'High response time',
                        'action': 'Enable response compression'
                    }
                
                # Reduce batch size
                new_batch_size = int(self.optimization_rules['response_optimization']['batch_size'] * 0.8)
                optimizations['batch_size_reduced'] = {
                    'reason': 'High response time',
                    'new_batch_size': new_batch_size,
                    'old_batch_size': self.optimization_rules['response_optimization']['batch_size']
                }
            
        except Exception as e:
            self.logger.warning(f"Error optimizing response: {e}")
        
        return optimizations
    
    def _calculate_cache_hit_rate(self) -> float:
        """Tính toán cache hit rate"""
        try:
            # Mock calculation - replace with actual cache statistics
            cache_hits = cache.get('cache_hits', 0)
            cache_misses = cache.get('cache_misses', 0)
            
            total_requests = cache_hits + cache_misses
            if total_requests == 0:
                return 0.0
            
            return round((cache_hits / total_requests) * 100, 2)
            
        except Exception as e:
            self.logger.warning(f"Error calculating cache hit rate: {e}")
            return 0.0
    
    def _apply_optimizations(self, optimizations: Dict[str, Any]):
        """Áp dụng các tối ưu"""
        try:
            for category, category_optimizations in optimizations.items():
                for optimization_name, optimization_details in category_optimizations.items():
                    self.logger.info(f"Applying optimization: {optimization_name}")
                    self.logger.info(f"Details: {optimization_details}")
                    
                    # TODO: Implement actual optimization logic
                    # This could involve updating configuration, restarting services, etc.
                    
        except Exception as e:
            self.logger.error(f"Error applying optimizations: {e}")


# Export services
__all__ = [
    'RiskMonitoringService',
    'PerformanceOptimizer'
]

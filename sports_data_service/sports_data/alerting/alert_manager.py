"""
Alert Manager cho Sports Data Service
Quản lý hệ thống cảnh báo tự động cho đội ngũ kỹ thuật
"""

import logging
import smtplib
import requests
from datetime import timedelta
from typing import Dict, List, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class AlertLevel:
    """Mức độ cảnh báo"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AlertChannel:
    """Kênh gửi cảnh báo"""
    EMAIL = "EMAIL"
    SLACK = "SLACK"
    WEBHOOK = "WEBHOOK"
    SMS = "SMS"

class Alert:
    """Đối tượng cảnh báo"""
    
    def __init__(
        self,
        title: str,
        message: str,
        level: str = AlertLevel.INFO,
        source: str = "sports_data_service",
        metadata: Dict[str, Any] = None
    ):
        self.title = title
        self.message = message
        self.level = level
        self.source = source
        self.metadata = metadata or {}
        self.timestamp = timezone.now()
        self.id = f"{self.source}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'level': self.level,
            'source': self.source,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

class AlertManager:
    """
    Quản lý hệ thống cảnh báo
    """
    
    def __init__(self):
        self.alert_history: List[Alert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.alert_channels: Dict[str, Dict[str, Any]] = {}
        
        # Cấu hình mặc định
        self.default_config = {
            'max_alerts_per_hour': 10,
            'alert_cooldown_minutes': 5,
            'enable_email_alerts': True,
            'enable_slack_alerts': False,
            'enable_webhook_alerts': False,
            'enable_sms_alerts': False
        }
        
        # Load cấu hình từ settings
        self._load_config()
        
        # Khởi tạo alert rules
        self._initialize_alert_rules()
    
    def _load_config(self):
        """Load cấu hình từ Django settings"""
        for key, default_value in self.default_config.items():
            setting_key = f'SPORTS_ALERT_{key.upper()}'
            setattr(self, key, getattr(settings, setting_key, default_value))
    
    def _initialize_alert_rules(self):
        """Khởi tạo các quy tắc cảnh báo mặc định"""
        self.alert_rules = {
            'provider_failure': {
                'title': 'Provider Failure Alert',
                'level': AlertLevel.ERROR,
                'cooldown_minutes': 10,
                'max_alerts_per_hour': 3
            },
            'circuit_breaker_open': {
                'title': 'Circuit Breaker Opened',
                'level': AlertLevel.WARNING,
                'cooldown_minutes': 5,
                'max_alerts_per_hour': 5
            },
            'data_sync_failure': {
                'title': 'Data Sync Failure',
                'level': AlertLevel.ERROR,
                'cooldown_minutes': 15,
                'max_alerts_per_hour': 2
            },
            'high_error_rate': {
                'title': 'High Error Rate Detected',
                'level': AlertLevel.WARNING,
                'cooldown_minutes': 30,
                'max_alerts_per_hour': 2
            },
            'quota_exhaustion': {
                'title': 'API Quota Exhaustion',
                'level': AlertLevel.WARNING,
                'cooldown_minutes': 60,
                'max_alerts_per_hour': 1
            }
        }
    
    def send_alert(
        self,
        alert_type: str,
        message: str,
        level: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Gửi cảnh báo
        """
        try:
            # Kiểm tra rule
            if alert_type not in self.alert_rules:
                logger.warning(f"Unknown alert type: {alert_type}")
                return False
            
            rule = self.alert_rules[alert_type]
            alert_level = level or rule['level']
            
            # Kiểm tra cooldown
            if not self._should_send_alert(alert_type, rule):
                logger.info(f"Alert {alert_type} is in cooldown, skipping")
                return False
            
            # Tạo alert object
            alert = Alert(
                title=rule['title'],
                message=message,
                level=alert_level,
                metadata=metadata or {}
            )
            
            # Thêm vào lịch sử
            self.alert_history.append(alert)
            
            # Gửi cảnh báo qua các kênh
            success = self._send_alert_to_channels(alert)
            
            # Cập nhật cache để track cooldown
            self._update_alert_cooldown(alert_type)
            
            # Log alert
            logger.info(f"Alert sent: {alert_type} - {alert.level} - {message}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending alert {alert_type}: {str(e)}")
            return False
    
    def _should_send_alert(self, alert_type: str, rule: Dict[str, Any]) -> bool:
        """Kiểm tra xem có nên gửi cảnh báo không"""
        cache_key = f"alert_cooldown_{alert_type}"
        last_alert_time = cache.get(cache_key)
        
        if last_alert_time:
            cooldown_minutes = rule.get('cooldown_minutes', 5)
            if timezone.now() - last_alert_time < timedelta(minutes=cooldown_minutes):
                return False
        
        # Kiểm tra số lượng cảnh báo trong 1 giờ
        cache_key = f"alert_count_{alert_type}_{timezone.now().strftime('%Y%m%d_%H')}"
        alert_count = cache.get(cache_key, 0)
        max_alerts = rule.get('max_alerts_per_hour', 5)
        
        if alert_count >= max_alerts:
            return False
        
        return True
    
    def _update_alert_cooldown(self, alert_type: str):
        """Cập nhật cooldown cho alert type"""
        cache_key = f"alert_cooldown_{alert_type}"
        cache.set(cache_key, timezone.now(), 3600)  # 1 giờ
        
        # Cập nhật số lượng cảnh báo trong giờ hiện tại
        cache_key = f"alert_count_{alert_type}_{timezone.now().strftime('%Y%m%d_%H')}"
        cache.set(cache_key, cache.get(cache_key, 0) + 1, 3600)
    
    def _send_alert_to_channels(self, alert: Alert) -> bool:
        """Gửi cảnh báo qua các kênh được cấu hình"""
        success = False
        
        try:
            # Gửi email
            if self.enable_email_alerts:
                if self._send_email_alert(alert):
                    success = True
            
            # Gửi Slack
            if self.enable_slack_alerts:
                if self._send_slack_alert(alert):
                    success = True
            
            # Gửi webhook
            if self.enable_webhook_alerts:
                if self._send_webhook_alert(alert):
                    success = True
            
            # Gửi SMS
            if self.enable_sms_alerts:
                if self._send_sms_alert(alert):
                    success = True
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending alert to channels: {str(e)}")
            return False
    
    def _send_email_alert(self, alert: Alert) -> bool:
        """Gửi cảnh báo qua email"""
        try:
            # Cấu hình email từ settings
            smtp_host = getattr(settings, 'SPORTS_ALERT_SMTP_HOST', 'localhost')
            smtp_port = getattr(settings, 'SPORTS_ALERT_SMTP_PORT', 587)
            smtp_user = getattr(settings, 'SPORTS_ALERT_SMTP_USER', '')
            smtp_password = getattr(settings, 'SPORTS_ALERT_SMTP_PASSWORD', '')
            from_email = getattr(settings, 'SPORTS_ALERT_FROM_EMAIL', 'alerts@sportsdata.com')
            to_emails = getattr(settings, 'SPORTS_ALERT_TO_EMAILS', ['admin@sportsdata.com'])
            
            # Tạo email message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[{alert.level}] {alert.title}"
            
            # Email body
            body = f"""
            Alert Details:
            --------------
            Title: {alert.title}
            Level: {alert.level}
            Source: {alert.source}
            Time: {alert.timestamp}
            
            Message:
            {alert.message}
            
            Metadata:
            {alert.metadata}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Gửi email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_user and smtp_password:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
            return False
    
    def _send_slack_alert(self, alert: Alert) -> bool:
        """Gửi cảnh báo qua Slack"""
        try:
            webhook_url = getattr(settings, 'SPORTS_ALERT_SLACK_WEBHOOK', '')
            
            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return False
            
            # Tạo Slack message
            slack_message = {
                "text": f"🚨 *{alert.title}*",
                "attachments": [
                    {
                        "color": self._get_slack_color(alert.level),
                        "fields": [
                            {
                                "title": "Level",
                                "value": alert.level,
                                "short": True
                            },
                            {
                                "title": "Source",
                                "value": alert.source,
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                "short": True
                            },
                            {
                                "title": "Message",
                                "value": alert.message,
                                "short": False
                            }
                        ]
                    }
                ]
            }
            
            # Gửi webhook
            response = requests.post(webhook_url, json=slack_message, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Slack alert sent: {alert.title}")
                return True
            else:
                logger.error(f"Slack webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")
            return False
    
    def _send_webhook_alert(self, alert: Alert) -> bool:
        """Gửi cảnh báo qua webhook"""
        try:
            webhook_url = getattr(settings, 'SPORTS_ALERT_WEBHOOK_URL', '')
            
            if not webhook_url:
                logger.warning("Webhook URL not configured")
                return False
            
            # Gửi webhook
            response = requests.post(webhook_url, json=alert.to_dict(), timeout=10)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Webhook alert sent: {alert.title}")
                return True
            else:
                logger.error(f"Webhook failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending webhook alert: {str(e)}")
            return False
    
    def _send_sms_alert(self, alert: Alert) -> bool:
        """Gửi cảnh báo qua SMS"""
        # TODO: Implement SMS alerting
        logger.info("SMS alerting not implemented yet")
        return False
    
    def _get_slack_color(self, level: str) -> str:
        """Lấy màu cho Slack message dựa trên level"""
        colors = {
            AlertLevel.INFO: "#36a64f",      # Green
            AlertLevel.WARNING: "#ffa500",   # Orange
            AlertLevel.ERROR: "#ff0000",     # Red
            AlertLevel.CRITICAL: "#8b0000"   # Dark Red
        }
        return colors.get(level, "#36a64f")
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Lấy lịch sử cảnh báo trong N giờ gần đây"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert.to_dict() for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        return sorted(recent_alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def get_alert_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Lấy thống kê cảnh báo trong N giờ gần đây"""
        recent_alerts = self.get_alert_history(hours)
        
        stats = {
            'total_alerts': len(recent_alerts),
            'by_level': {},
            'by_source': {},
            'by_hour': {}
        }
        
        for alert in recent_alerts:
            # Thống kê theo level
            level = alert['level']
            stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
            
            # Thống kê theo source
            source = alert['source']
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
            
            # Thống kê theo giờ
            hour = alert['timestamp'][:13]  # YYYY-MM-DDTHH
            stats['by_hour'][hour] = stats['by_hour'].get(hour, 0) + 1
        
        return stats
    
    def clear_alert_history(self, days: int = 7):
        """Xóa lịch sử cảnh báo cũ hơn N ngày"""
        cutoff_time = timezone.now() - timedelta(days=days)
        
        # Giữ lại alerts mới
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        logger.info(f"Cleared alert history older than {days} days")

# Global Alert Manager instance
alert_manager = AlertManager()

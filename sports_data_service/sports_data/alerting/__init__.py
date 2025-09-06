"""
Alerting Module - Hệ thống cảnh báo và thông báo

Module này cung cấp:
- Multi-channel alerting (Email, Slack, Webhook, SMS)
- Smart alerting rules
- Cooldown và rate limiting
- Alert history và statistics

Classes:
- AlertManager: Quản lý hệ thống cảnh báo
- Alert: Đại diện cho một cảnh báo
- AlertLevel: Các mức độ cảnh báo
- AlertChannel: Các kênh gửi cảnh báo
"""

from .alert_manager import alert_manager, AlertManager, Alert, AlertLevel, AlertChannel

__all__ = [
    'alert_manager',
    'AlertManager',
    'Alert',
    'AlertLevel',
    'AlertChannel'
]

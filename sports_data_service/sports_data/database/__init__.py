"""
Database Module - Quản lý kết nối và connection pooling

Module này cung cấp:
- Database connection pooling
- Connection health monitoring
- Query execution utilities
- Connection statistics

Classes:
- DatabaseConnectionManager: Quản lý database connection pool
"""

from .connection_manager import db_connection_manager, DatabaseConnectionManager

__all__ = [
    'db_connection_manager',
    'DatabaseConnectionManager'
]

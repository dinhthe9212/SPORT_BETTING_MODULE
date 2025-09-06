"""
Authentication Module - Quản lý xác thực và ủy quyền

Module này cung cấp:
- JWT token management
- Token refresh functionality
- Token revocation
- Authentication utilities

Classes:
- JWTManager: Quản lý JWT tokens với refresh functionality
"""

from .jwt_utils import jwt_manager, JWTManager

__all__ = [
    'jwt_manager',
    'JWTManager'
]

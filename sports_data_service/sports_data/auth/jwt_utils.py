from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """Quản lý JWT tokens với refresh functionality"""
    
    def __init__(self):
        self.secret_key = getattr(settings, 'JWT_SECRET_KEY', 'your-secret-key')
        self.algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
        self.access_token_expiry = getattr(settings, 'JWT_ACCESS_TOKEN_EXPIRY', 15)  # 15 phút
        self.refresh_token_expiry = getattr(settings, 'JWT_REFRESH_TOKEN_EXPIRY', 7)  # 7 ngày
        self.refresh_token_prefix = 'refresh_token:'
    
    def generate_tokens(self, user_id: int, username: str) -> dict:
        """Tạo access token và refresh token"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'username': username,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(minutes=self.access_token_expiry)
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'username': username,
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=self.refresh_token_expiry)
        }
        
        # Tạo tokens
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # Lưu refresh token vào cache với expiry
        cache_key = f"{self.refresh_token_prefix}{user_id}"
        cache.set(cache_key, refresh_token, timeout=self.refresh_token_expiry * 24 * 60 * 60)
        
        logger.info(f"Generated tokens for user {username} (ID: {user_id})")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_token_expires_in': self.access_token_expiry * 60,
            'refresh_token_expires_in': self.refresh_token_expiry * 24 * 60 * 60
        }
    
    def verify_token(self, token: str) -> dict:
        """Xác thực token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            raise Exception("Invalid token")
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Làm mới access token từ refresh token"""
        try:
            # Xác thực refresh token
            payload = self.verify_token(refresh_token)
            
            if payload.get('type') != 'refresh':
                raise Exception("Invalid token type")
            
            user_id = payload.get('user_id')
            username = payload.get('username')
            
            # Kiểm tra refresh token có trong cache không
            cache_key = f"{self.refresh_token_prefix}{user_id}"
            cached_refresh_token = cache.get(cache_key)
            
            if not cached_refresh_token or cached_refresh_token != refresh_token:
                raise Exception("Invalid refresh token")
            
            # Tạo access token mới
            now = datetime.utcnow()
            access_payload = {
                'user_id': user_id,
                'username': username,
                'type': 'access',
                'iat': now,
                'exp': now + timedelta(minutes=self.access_token_expiry)
            }
            
            new_access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"Refreshed access token for user {username} (ID: {user_id})")
            
            return {
                'access_token': new_access_token,
                'access_token_expires_in': self.access_token_expiry * 60
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise
    
    def revoke_refresh_token(self, user_id: int) -> bool:
        """Thu hồi refresh token của user"""
        cache_key = f"{self.refresh_token_prefix}{user_id}"
        cache.delete(cache_key)
        logger.info(f"Revoked refresh token for user ID: {user_id}")
        return True
    
    def is_token_expired(self, token: str) -> bool:
        """Kiểm tra token có hết hạn chưa"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                return datetime.utcnow() > exp_datetime
            return True
        except:
            return True

# Global instance
jwt_manager = JWTManager()

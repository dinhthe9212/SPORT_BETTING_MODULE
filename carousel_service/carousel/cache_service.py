from django.core.cache import cache
from django.conf import settings
from typing import Optional


class CarouselCacheService:
    """Service để cache carousel data với Redis"""
    
    # Cache keys
    PRIORITIZED_ITEMS_KEY = "carousel:prioritized:{user_id}:{device_type}:{limit}"
    RANDOMIZED_ITEMS_KEY = "carousel:randomized:{device_type}:{limit}:{timestamp}"
    USER_PURCHASES_KEY = "carousel:purchases:{user_id}"
    
    # Cache timeouts (seconds)
    PRIORITIZED_TIMEOUT = 300  # 5 minutes
    RANDOMIZED_TIMEOUT = 600   # 10 minutes  
    PURCHASES_TIMEOUT = 1800   # 30 minutes
    
    @classmethod
    def get_prioritized_items_cache_key(cls, user_id: Optional[int], device_type: str, limit: int) -> str:
        """Tạo cache key cho prioritized items"""
        user_key = user_id or "anonymous"
        return cls.PRIORITIZED_ITEMS_KEY.format(
            user_id=user_key,
            device_type=device_type,
            limit=limit
        )
    
    @classmethod
    def get_user_purchases_cache_key(cls, user_id: int) -> str:
        """Tạo cache key cho user purchases"""
        return cls.USER_PURCHASES_KEY.format(user_id=user_id)
    
    @classmethod
    def cache_prioritized_items(cls, user_id: Optional[int], device_type: str, 
                               limit: int, items_data: list) -> bool:
        """Cache prioritized items"""
        try:
            cache_key = cls.get_prioritized_items_cache_key(user_id, device_type, limit)
            cache.set(cache_key, items_data, cls.PRIORITIZED_TIMEOUT)
            return True
        except Exception as e:
            print(f"Error caching prioritized items: {e}")
            return False
    
    @classmethod
    def get_cached_prioritized_items(cls, user_id: Optional[int], device_type: str, 
                                    limit: int) -> Optional[list]:
        """Lấy prioritized items từ cache"""
        try:
            cache_key = cls.get_prioritized_items_cache_key(user_id, device_type, limit)
            return cache.get(cache_key)
        except Exception as e:
            print(f"Error getting cached prioritized items: {e}")
            return None
    
    @classmethod
    def cache_user_purchases(cls, user_id: int, purchase_ids: list) -> bool:
        """Cache user purchase IDs"""
        try:
            cache_key = cls.get_user_purchases_cache_key(user_id)
            cache.set(cache_key, purchase_ids, cls.PURCHASES_TIMEOUT)
            return True
        except Exception as e:
            print(f"Error caching user purchases: {e}")
            return False
    
    @classmethod
    def get_cached_user_purchases(cls, user_id: int) -> Optional[list]:
        """Lấy user purchases từ cache"""
        try:
            cache_key = cls.get_user_purchases_cache_key(user_id)
            return cache.get(cache_key)
        except Exception as e:
            print(f"Error getting cached user purchases: {e}")
            return None
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> bool:
        """Invalidate tất cả cache của user (khi có purchase mới)"""
        try:
            # Invalidate user purchases
            purchases_key = cls.get_user_purchases_cache_key(user_id)
            cache.delete(purchases_key)
            
            # Invalidate prioritized items for all device types
            for device_type in ['mobile', 'tablet', 'desktop']:
                for limit in [15, 20, 25]:  # Common limits
                    prioritized_key = cls.get_prioritized_items_cache_key(user_id, device_type, limit)
                    cache.delete(prioritized_key)
            
            return True
        except Exception as e:
            print(f"Error invalidating user cache: {e}")
            return False
    
    @classmethod
    def invalidate_all_carousel_cache(cls) -> bool:
        """Invalidate toàn bộ carousel cache (khi có update products)"""
        try:
            # Pattern-based deletion (requires Redis)
            cache_patterns = [
                "carousel:prioritized:*",
                "carousel:randomized:*"
            ]
            
            # Note: Django cache framework không hỗ trợ pattern deletion
            # Cần implement với Redis client trực tiếp
            import redis
            r = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
            
            for pattern in cache_patterns:
                keys = r.keys(pattern)
                if keys:
                    r.delete(*keys)
            
            return True
        except Exception as e:
            print(f"Error invalidating all carousel cache: {e}")
            return False


class LeaderboardCacheService:
    """Service để cache leaderboard data"""
    
    # Cache keys
    INDIVIDUAL_LEADERBOARD_KEY = "leaderboard:individual:{period}:{category}:{limit}"
    GROUP_LEADERBOARD_KEY = "leaderboard:group:{period}:{category}:{limit}"
    USER_RANK_KEY = "leaderboard:user_rank:{user_id}:{period}:{category}"
    GROUP_RANK_KEY = "leaderboard:group_rank:{group_id}:{period}:{category}"
    
    # Cache timeouts
    LEADERBOARD_TIMEOUT = 3600  # 1 hour
    RANK_TIMEOUT = 1800         # 30 minutes
    
    @classmethod
    def cache_individual_leaderboard(cls, period: str, category: str, 
                                   limit: int, data: list) -> bool:
        """Cache individual leaderboard"""
        try:
            cache_key = cls.INDIVIDUAL_LEADERBOARD_KEY.format(
                period=period, category=category, limit=limit
            )
            cache.set(cache_key, data, cls.LEADERBOARD_TIMEOUT)
            return True
        except Exception as e:
            print(f"Error caching individual leaderboard: {e}")
            return False
    
    @classmethod
    def get_cached_individual_leaderboard(cls, period: str, category: str, 
                                        limit: int) -> Optional[list]:
        """Lấy individual leaderboard từ cache"""
        try:
            cache_key = cls.INDIVIDUAL_LEADERBOARD_KEY.format(
                period=period, category=category, limit=limit
            )
            return cache.get(cache_key)
        except Exception as e:
            print(f"Error getting cached individual leaderboard: {e}")
            return None
    
    @classmethod
    def cache_group_leaderboard(cls, period: str, category: str, 
                              limit: int, data: list) -> bool:
        """Cache group leaderboard"""
        try:
            cache_key = cls.GROUP_LEADERBOARD_KEY.format(
                period=period, category=category, limit=limit
            )
            cache.set(cache_key, data, cls.LEADERBOARD_TIMEOUT)
            return True
        except Exception as e:
            print(f"Error caching group leaderboard: {e}")
            return False
    
    @classmethod
    def get_cached_group_leaderboard(cls, period: str, category: str, 
                                   limit: int) -> Optional[list]:
        """Lấy group leaderboard từ cache"""
        try:
            cache_key = cls.GROUP_LEADERBOARD_KEY.format(
                period=period, category=category, limit=limit
            )
            return cache.get(cache_key)
        except Exception as e:
            print(f"Error getting cached group leaderboard: {e}")
            return None
    
    @classmethod
    def invalidate_leaderboard_cache(cls, period: str = None, category: str = None) -> bool:
        """Invalidate leaderboard cache khi có update rankings"""
        try:
            import redis
            r = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
            
            patterns = []
            if period and category:
                patterns = [
                    f"leaderboard:individual:{period}:{category}:*",
                    f"leaderboard:group:{period}:{category}:*"
                ]
            else:
                patterns = [
                    "leaderboard:individual:*",
                    "leaderboard:group:*",
                    "leaderboard:user_rank:*",
                    "leaderboard:group_rank:*"
                ]
            
            for pattern in patterns:
                keys = r.keys(pattern)
                if keys:
                    r.delete(*keys)
            
            return True
        except Exception as e:
            print(f"Error invalidating leaderboard cache: {e}")
            return False

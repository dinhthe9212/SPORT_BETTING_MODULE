from django.http import HttpResponseForbidden
from django.conf import settings
from django.core.cache import cache
import ipaddress
import logging

logger = logging.getLogger(__name__)

class IPWhitelistMiddleware:
    """Middleware kiểm soát truy cập dựa trên IP whitelist"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelist_cache_key = 'ip_whitelist'
        self.whitelist_cache_timeout = 300  # 5 phút
        
    def __call__(self, request):
        # Kiểm tra IP whitelist
        if not self._is_ip_allowed(request):
            logger.warning(f"Access denied for IP: {self._get_client_ip(request)}")
            return HttpResponseForbidden("Access denied: IP not in whitelist")
        
        response = self.get_response(request)
        return response
    
    def _get_client_ip(self, request):
        """Lấy IP thực của client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_ip_allowed(self, request):
        """Kiểm tra IP có được phép truy cập không"""
        client_ip = self._get_client_ip(request)
        
        # Lấy whitelist từ cache hoặc settings
        whitelist = self._get_whitelist()
        
        # Kiểm tra IP có trong whitelist không
        for allowed_ip in whitelist:
            try:
                if self._ip_in_range(client_ip, allowed_ip):
                    return True
            except ValueError:
                logger.warning(f"Invalid IP format in whitelist: {allowed_ip}")
                continue
        
        return False
    
    def _get_whitelist(self):
        """Lấy danh sách IP được phép từ cache hoặc settings"""
        # Thử lấy từ cache trước
        whitelist = cache.get(self.whitelist_cache_key)
        
        if whitelist is None:
            # Lấy từ settings
            whitelist = getattr(settings, 'IP_WHITELIST', [])
            
            # Lưu vào cache
            cache.set(self.whitelist_cache_key, whitelist, self.whitelist_cache_timeout)
        
        return whitelist
    
    def _ip_in_range(self, client_ip, allowed_ip):
        """Kiểm tra IP có nằm trong range được phép không"""
        try:
            # Nếu là CIDR notation (ví dụ: 192.168.1.0/24)
            if '/' in allowed_ip:
                network = ipaddress.ip_network(allowed_ip, strict=False)
                return ipaddress.ip_address(client_ip) in network
            
            # Nếu là IP đơn lẻ
            elif allowed_ip == client_ip:
                return True
            
            # Nếu là wildcard (ví dụ: 192.168.1.*)
            elif '*' in allowed_ip:
                allowed_pattern = allowed_ip.replace('*', '')
                return client_ip.startswith(allowed_pattern)
            
            # Nếu là range (ví dụ: 192.168.1.1-192.168.1.100)
            elif '-' in allowed_ip:
                start_ip, end_ip = allowed_ip.split('-')
                start = ipaddress.ip_address(start_ip.strip())
                end = ipaddress.ip_address(end_ip.strip())
                client = ipaddress.ip_address(client_ip)
                return start <= client <= end
            
            return False
            
        except ValueError:
            logger.warning(f"Invalid IP format: {allowed_ip}")
            return False
    
    def update_whitelist(self, new_whitelist):
        """Cập nhật IP whitelist"""
        cache.set(self.whitelist_cache_key, new_whitelist, self.whitelist_cache_timeout)
        logger.info(f"Updated IP whitelist: {new_whitelist}")
    
    def add_ip_to_whitelist(self, ip):
        """Thêm IP vào whitelist"""
        current_whitelist = self._get_whitelist()
        if ip not in current_whitelist:
            current_whitelist.append(ip)
            self.update_whitelist(current_whitelist)
            logger.info(f"Added IP to whitelist: {ip}")
    
    def remove_ip_from_whitelist(self, ip):
        """Xóa IP khỏi whitelist"""
        current_whitelist = self._get_whitelist()
        if ip in current_whitelist:
            current_whitelist.remove(ip)
            self.update_whitelist(current_whitelist)
            logger.info(f"Removed IP from whitelist: {ip}")
    
    def get_current_whitelist(self):
        """Lấy danh sách IP whitelist hiện tại"""
        return self._get_whitelist()

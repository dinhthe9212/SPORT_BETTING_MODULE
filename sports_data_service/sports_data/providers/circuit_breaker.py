"""
Circuit Breaker Pattern Implementation cho Sports Data Providers
Xử lý lỗi, failover và health monitoring cho các API providers
"""

import time
import logging
from enum import Enum
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Trạng thái của Circuit Breaker"""
    CLOSED = "CLOSED"      # Hoạt động bình thường
    OPEN = "OPEN"          # Ngắt mạch, không gọi API
    HALF_OPEN = "HALF_OPEN"  # Thử nghiệm khôi phục

class CircuitBreaker:
    """
    Circuit Breaker Pattern để xử lý lỗi và failover
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name
        
        # State variables
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        # Metrics
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        
        logger.info(f"Circuit Breaker '{name}' initialized: failure_threshold={failure_threshold}, recovery_timeout={recovery_timeout}")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Gọi function với Circuit Breaker protection"""
        self.total_requests += 1
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(f"Circuit Breaker '{self.name}' attempting reset to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                logger.warning(f"Circuit Breaker '{self.name}' is OPEN, request blocked")
                raise Exception(f"Circuit Breaker '{self.name}' is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure(e)
            raise
    
    def _on_success(self):
        """Xử lý khi request thành công"""
        self.failure_count = 0
        self.last_success_time = time.time()
        self.total_successes += 1
        
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit Breaker '{self.name}' reset to CLOSED after successful request")
            self.state = CircuitState.CLOSED
    
    def _on_failure(self, exception: Exception):
        """Xử lý khi request thất bại"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.total_failures += 1
        
        logger.warning(f"Circuit Breaker '{self.name}' failure #{self.failure_count}: {str(exception)}")
        
        if self.failure_count >= self.failure_threshold:
            logger.error(f"Circuit Breaker '{self.name}' opened after {self.failure_count} failures")
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Kiểm tra xem có nên thử reset circuit breaker không"""
        if self.last_failure_time is None:
            return False
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def get_health_status(self) -> Dict[str, Any]:
        """Lấy trạng thái sức khỏe của Circuit Breaker"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout,
            'last_failure_time': self.last_failure_time,
            'last_success_time': self.last_success_time,
            'total_requests': self.total_requests,
            'total_failures': self.total_failures,
            'total_successes': self.total_successes,
            'success_rate': (self.total_successes / self.total_requests * 100) if self.total_requests > 0 else 0,
            'is_healthy': self.state == CircuitState.CLOSED
        }
    
    def force_open(self):
        """Buộc mở Circuit Breaker"""
        logger.warning(f"Circuit Breaker '{self.name}' forced to OPEN")
        self.state = CircuitState.OPEN
        self.failure_count = self.failure_threshold
    
    def force_close(self):
        """Buộc đóng Circuit Breaker"""
        logger.info(f"Circuit Breaker '{self.name}' forced to CLOSED")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
    
    def reset(self):
        """Reset Circuit Breaker về trạng thái ban đầu"""
        logger.info(f"Circuit Breaker '{self.name}' reset")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception,
    name: str = None
):
    """
    Decorator để áp dụng Circuit Breaker cho function
    """
    def decorator(func: Callable) -> Callable:
        # Tạo tên cho circuit breaker nếu không được chỉ định
        cb_name = name or f"{func.__module__}.{func.__name__}"
        
        # Tạo circuit breaker instance
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            name=cb_name
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        # Thêm circuit breaker instance vào wrapper để có thể truy cập
        wrapper.circuit_breaker = cb
        return wrapper
    
    return decorator

class CircuitBreakerManager:
    """
    Quản lý tất cả Circuit Breakers trong hệ thống
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def add_circuit_breaker(self, name: str, circuit_breaker: CircuitBreaker):
        """Thêm Circuit Breaker vào manager"""
        self.circuit_breakers[name] = circuit_breaker
        logger.info(f"Added Circuit Breaker '{name}' to manager")
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Lấy Circuit Breaker theo tên"""
        return self.circuit_breakers.get(name)
    
    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Lấy trạng thái sức khỏe của tất cả Circuit Breakers"""
        return {
            name: cb.get_health_status() 
            for name, cb in self.circuit_breakers.items()
        }
    
    def force_open_all(self):
        """Buộc mở tất cả Circuit Breakers"""
        for name, cb in self.circuit_breakers.items():
            cb.force_open()
        logger.warning("All Circuit Breakers forced to OPEN")
    
    def force_close_all(self):
        """Buộc đóng tất cả Circuit Breakers"""
        for name, cb in self.circuit_breakers.items():
            cb.force_close()
        logger.info("All Circuit Breakers forced to CLOSED")
    
    def reset_all(self):
        """Reset tất cả Circuit Breakers"""
        for name, cb in self.circuit_breakers.items():
            cb.reset()
        logger.info("All Circuit Breakers reset")
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Lấy tổng quan sức khỏe hệ thống"""
        all_status = self.get_all_health_status()
        
        total_circuits = len(all_status)
        healthy_circuits = sum(1 for status in all_status.values() if status['is_healthy'])
        open_circuits = sum(1 for status in all_status.values() if status['state'] == 'OPEN')
        half_open_circuits = sum(1 for status in all_status.values() if status['state'] == 'HALF_OPEN')
        
        total_requests = sum(status['total_requests'] for status in all_status.values())
        total_failures = sum(status['total_failures'] for status in all_status.values())
        
        overall_success_rate = (
            (total_requests - total_failures) / total_requests * 100 
            if total_requests > 0 else 100
        )
        
        return {
            'total_circuits': total_circuits,
            'healthy_circuits': healthy_circuits,
            'open_circuits': open_circuits,
            'half_open_circuits': half_open_circuits,
            'overall_health_percentage': (healthy_circuits / total_circuits * 100) if total_circuits > 0 else 0,
            'total_requests': total_requests,
            'total_failures': total_failures,
            'overall_success_rate': overall_success_rate,
            'system_status': 'HEALTHY' if open_circuits == 0 else 'DEGRADED' if open_circuits < total_circuits else 'CRITICAL'
        }

# Global Circuit Breaker Manager instance
circuit_breaker_manager = CircuitBreakerManager()

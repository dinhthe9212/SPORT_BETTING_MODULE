from psycopg2 import pool
from django.conf import settings
import logging
import threading
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """Quản lý database connection pool"""
    
    def __init__(self):
        self.pool = None
        self.lock = threading.Lock()
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'failed_connections': 0,
            'last_health_check': None
        }
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Khởi tạo connection pool"""
        try:
            db_settings = settings.DATABASES['default']
            pool_settings = getattr(settings, 'DB_POOL_SETTINGS', {})
            
            self.pool = pool.ThreadedConnectionPool(
                minconn=pool_settings.get('MIN_CONNECTIONS', 5),
                maxconn=pool_settings.get('MAX_CONNECTIONS', 20),
                host=db_settings['HOST'],
                port=db_settings['PORT'],
                database=db_settings['NAME'],
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                connect_timeout=pool_settings.get('CONNECTION_TIMEOUT', 30),
                options=f"-c idle_in_transaction_session_timeout={pool_settings.get('IDLE_TIMEOUT', 300)}"
            )
            
            logger.info(f"Database connection pool initialized with {pool_settings.get('MIN_CONNECTIONS', 5)}-{pool_settings.get('MAX_CONNECTIONS', 20)} connections")
            
            # Khởi chạy health check thread
            self._start_health_check_thread()
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {str(e)}")
            self.pool = None
    
    def _start_health_check_thread(self):
        """Khởi chạy thread kiểm tra sức khỏe connection pool"""
        def health_check_worker():
            while True:
                try:
                    self._perform_health_check()
                    time.sleep(getattr(settings, 'DB_POOL_SETTINGS', {}).get('HEALTH_CHECK_INTERVAL', 60))
                except Exception as e:
                    logger.error(f"Health check worker error: {str(e)}")
                    time.sleep(10)
        
        health_thread = threading.Thread(target=health_check_worker, daemon=True)
        health_thread.start()
        logger.info("Database connection pool health check thread started")
    
    def _perform_health_check(self):
        """Thực hiện kiểm tra sức khỏe connection pool"""
        if not self.pool:
            return
        
        try:
            with self.lock:
                # Lấy thống kê connection pool
                pool_stats = self.pool.get_stats()
                
                self.connection_stats.update({
                    'total_connections': pool_stats.get('total_connections', 0),
                    'active_connections': pool_stats.get('active_connections', 0),
                    'idle_connections': pool_stats.get('idle_connections', 0),
                    'last_health_check': time.time()
                })
                
                # Kiểm tra connection pool health
                if pool_stats.get('active_connections', 0) > pool_stats.get('total_connections', 0) * 0.8:
                    logger.warning("Database connection pool is reaching capacity")
                
                # Test connection
                test_conn = self.pool.getconn()
                if test_conn:
                    test_conn.close()
                    self.pool.putconn(test_conn)
                
                logger.debug(f"Database connection pool health check completed: {self.connection_stats}")
                
        except Exception as e:
            logger.error(f"Database connection pool health check failed: {str(e)}")
            self.connection_stats['failed_connections'] += 1
    
    @contextmanager
    def get_connection(self):
        """Lấy connection từ pool với context manager"""
        conn = None
        try:
            if not self.pool:
                raise Exception("Database connection pool not initialized")
            
            conn = self.pool.getconn()
            if conn:
                self.connection_stats['active_connections'] += 1
                yield conn
            else:
                raise Exception("Failed to get database connection from pool")
                
        except Exception as e:
            logger.error(f"Error getting database connection: {str(e)}")
            raise
        finally:
            if conn:
                try:
                    self.pool.putconn(conn)
                    self.connection_stats['active_connections'] -= 1
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {str(e)}")
    
    def execute_query(self, query, params=None):
        """Thực thi query với connection từ pool"""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if query.strip().upper().startswith('SELECT'):
                        return cursor.fetchall()
                    else:
                        conn.commit()
                        return cursor.rowcount
            except Exception as e:
                conn.rollback()
                logger.error(f"Query execution failed: {str(e)}")
                raise
    
    def execute_many(self, query, params_list):
        """Thực thi nhiều queries với connection từ pool"""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.executemany(query, params_list)
                    conn.commit()
                    return cursor.rowcount
            except Exception as e:
                conn.rollback()
                logger.error(f"Batch query execution failed: {str(e)}")
                raise
    
    def get_pool_status(self):
        """Lấy trạng thái connection pool"""
        if not self.pool:
            return {
                'status': 'not_initialized',
                'error': 'Connection pool not initialized'
            }
        
        try:
            pool_stats = self.pool.get_stats()
            return {
                'status': 'healthy',
                'pool_stats': pool_stats,
                'connection_stats': self.connection_stats,
                'settings': getattr(settings, 'DB_POOL_SETTINGS', {})
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'connection_stats': self.connection_stats
            }
    
    def reset_pool(self):
        """Reset connection pool"""
        try:
            with self.lock:
                if self.pool:
                    self.pool.closeall()
                    logger.info("Database connection pool closed")
                
                self._initialize_pool()
                logger.info("Database connection pool reset completed")
                
        except Exception as e:
            logger.error(f"Failed to reset database connection pool: {str(e)}")
    
    def close_pool(self):
        """Đóng connection pool"""
        try:
            if self.pool:
                self.pool.closeall()
                logger.info("Database connection pool closed")
        except Exception as e:
            logger.error(f"Error closing database connection pool: {str(e)}")

# Global instance
db_connection_manager = DatabaseConnectionManager()

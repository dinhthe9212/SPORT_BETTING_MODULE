"""
Django Management Command để chạy Circuit Breaker Monitoring
Chạy liên tục hoặc một lần để kiểm tra các rule
"""

from django.core.management.base import BaseCommand
import time
import logging
from risk_manager.circuit_breakers import CircuitBreakerManager
from django.utils import timezone

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Chạy circuit breaker monitoring cho risk management'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval', 
            type=int, 
            default=60, 
            help='Khoảng thời gian kiểm tra (giây) - mặc định: 60'
        )
        parser.add_argument(
            '--once', 
            action='store_true', 
            help='Chạy một lần và thoát'
        )
        parser.add_argument(
            '--create-rules', 
            action='store_true', 
            help='Tạo default rules trước khi chạy monitoring'
        )
        parser.add_argument(
            '--verbose', 
            action='store_true', 
            help='Hiển thị thông tin chi tiết'
        )
    
    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options['once']
        create_rules = options['create_rules']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🚀 Khởi động Circuit Breaker Monitoring...'
            )
        )
        
        if verbose:
            self.stdout.write(f'  - Interval: {interval} giây')
            self.stdout.write(f'  - Mode: {"One-time" if run_once else "Continuous"}')
            self.stdout.write(f'  - Create rules: {"Yes" if create_rules else "No"}')
        
        # Khởi tạo manager
        manager = CircuitBreakerManager()
        
        # Tạo default rules nếu được yêu cầu
        if create_rules:
            self.stdout.write('📋 Tạo default circuit breaker rules...')
            try:
                created_rules = manager.create_default_rules()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Đã tạo {len(created_rules)} default rules'
                    )
                )
                if verbose:
                    for rule in created_rules:
                        self.stdout.write(f'    - {rule.name} ({rule.severity})')
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f'❌ Lỗi khi tạo default rules: {e}'
                    )
                )
        
        # Chạy monitoring
        if run_once:
            self.stdout.write('🔍 Chạy một lần circuit breaker monitoring...')
            try:
                triggered_rules = manager.run_monitoring_cycle()
                self._display_results(triggered_rules, verbose)
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f'❌ Lỗi trong monitoring cycle: {e}'
                    )
                )
        else:
            self.stdout.write('🔄 Chạy continuous monitoring...')
            self.stdout.write('  (Nhấn Ctrl+C để dừng)')
            
            try:
                cycle_count = 0
                while True:
                    cycle_count += 1
                    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if verbose:
                        self.stdout.write(f'\n🔄 Cycle #{cycle_count} - {current_time}')
                    
                    try:
                        triggered_rules = manager.run_monitoring_cycle()
                        self._display_results(triggered_rules, verbose)
                        
                        if verbose:
                            self.stdout.write(f'⏳ Chờ {interval} giây...')
                        
                        time.sleep(interval)
                        
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(
                                f'❌ Lỗi trong monitoring cycle #{cycle_count}: {e}'
                            )
                        )
                        if verbose:
                            self.stdout.write(f'⏳ Chờ {interval} giây trước khi thử lại...')
                        time.sleep(interval)
                        
            except KeyboardInterrupt:
                self.stdout.write('\n🛑 Dừng circuit breaker monitoring...')
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Đã chạy {cycle_count} monitoring cycles'
                    )
                )
    
    def _display_results(self, triggered_rules, verbose=False):
        """Hiển thị kết quả monitoring"""
        
        if not triggered_rules:
            if verbose:
                self.stdout.write('✅ Không có rule nào được triggered')
            return
        
        self.stdout.write(
            self.style.WARNING(
                f'⚠️  {len(triggered_rules)} rules được triggered:'
            )
        )
        
        for i, trigger in enumerate(triggered_rules, 1):
            rule = trigger['rule']
            result = trigger['result']
            action = trigger['action_taken']
            
            self.stdout.write(f'  {i}. {rule.name} ({rule.severity})')
            self.stdout.write(f'     Lý do: {result["reason"]}')
            self.stdout.write(f'     Hành động: {action["action"]}')
            
            if verbose and action.get('success'):
                if 'suspension_id' in action:
                    self.stdout.write(f'     Suspension ID: {action["suspension_id"]}')
                if 'alert_id' in action:
                    self.stdout.write(f'     Alert ID: {action["alert_id"]}')
                if 'limits_reduced' in action:
                    self.stdout.write(f'     Giảm limits: {action["reduction_percentage"]}%')
                if 'emergency_stop_activated' in action:
                    self.stdout.write(f'     Emergency Stop: {action["stop_reason"]}')
            
            if verbose and result.get('data'):
                self.stdout.write(f'     Dữ liệu: {result["data"]}')
            
            self.stdout.write('')

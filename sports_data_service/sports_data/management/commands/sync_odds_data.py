"""
Management command để đồng bộ dữ liệu tỷ lệ cược từ The-Odds-API
Chạy mỗi 10 phút để cập nhật tỷ lệ cược tham khảo cho Admin
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.cache import cache
import logging
from datetime import datetime

from sports_data.providers.multi_sports_provider import MultiSportsDataProvider
from sports_data.models import Sport

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Đồng bộ dữ liệu tỷ lệ cược từ The-Odds-API theo lịch trình'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Bắt buộc đồng bộ ngay cả khi cache còn hạn',
        )
        parser.add_argument(
            '--sport',
            type=str,
            help='Chỉ định môn thể thao cụ thể để đồng bộ',
        )
        parser.add_argument(
            '--market',
            type=str,
            default='h2h',
            help='Loại thị trường cược (h2h, spreads, totals)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Bắt đầu đồng bộ dữ liệu tỷ lệ cược...')
        )
        
        start_time = timezone.now()
        force_sync = options['force']
        specific_sport = options['sport']
        market_type = options['market']
        
        try:
            # Khởi tạo multi-provider service
            sports_service = MultiSportsDataProvider()
            
            # Lấy danh sách môn thể thao cần đồng bộ odds
            if specific_sport:
                sports = Sport.objects.filter(name__icontains=specific_sport, is_active=True)
            else:
                # Chỉ đồng bộ các môn thể thao chính có odds data
                main_sports = ['football', 'basketball', 'american_football', 'baseball', 'hockey']
                sports = Sport.objects.filter(
                    name__in=main_sports,
                    is_active=True
                )
            
            total_sports = sports.count()
            self.stdout.write(f"📊 Tổng số môn thể thao cần đồng bộ odds: {total_sports}")
            
            # Đồng bộ odds cho từng môn thể thao
            for sport in sports:
                self.stdout.write(f"🎲 Đang đồng bộ odds cho {sport.name}...")
                
                try:
                    # Kiểm tra cache trước khi đồng bộ
                    cache_key = f"odds_data_sync_{sport.name}_{market_type}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    
                    if not force_sync and cache.get(cache_key):
                        self.stdout.write(f"   ⏭️  Odds cho {sport.name} đã được đồng bộ gần đây, bỏ qua")
                        continue
                    
                    # Đồng bộ odds data
                    self._sync_odds_for_sport(sports_service, sport, market_type)
                    
                    # Đánh dấu đã đồng bộ trong cache (10 phút)
                    cache.set(cache_key, True, 600)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ Odds cho {sport.name} đồng bộ thành công")
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"   ❌ Lỗi đồng bộ odds cho {sport.name}: {str(e)}")
                    )
                    logger.error(f"Error syncing odds for sport {sport.name}: {str(e)}")
                    continue
            
            end_time = timezone.now()
            duration = end_time - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Hoàn thành đồng bộ dữ liệu tỷ lệ cược trong {duration.total_seconds():.2f} giây'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Lỗi đồng bộ dữ liệu tỷ lệ cược: {str(e)}')
            )
            logger.error(f"Error in sync_odds_data command: {str(e)}")
            raise

    def _sync_odds_for_sport(self, sports_service, sport, market_type):
        """Đồng bộ odds cho một môn thể thao cụ thể"""
        try:
            # Lấy odds data từ provider
            odds_data = sports_service.get_odds(sport.name.lower(), market_type)
            
            if odds_data and 'data' in odds_data:
                # Xử lý và lưu odds data
                self._process_odds_data(sport, odds_data['data'], market_type)
                
        except Exception as e:
            logger.warning(f"Error syncing odds for {sport.name}: {str(e)}")

    def _process_odds_data(self, sport, odds_data, market_type):
        """Xử lý và lưu odds data vào database"""
        try:
            # TODO: Implement odds data processing logic
            # 1. Parse odds data từ API response
            # 2. Map với matches trong database
            # 3. Lưu odds data cho admin reference
            # 4. Cập nhật cache cho quick access
            
            # Tạm thời log để debug
            logger.info(f"Processing odds data for {sport.name}, market: {market_type}, data count: {len(odds_data) if isinstance(odds_data, list) else 0}")
            
        except Exception as e:
            logger.error(f"Error processing odds data for {sport.name}: {str(e)}")

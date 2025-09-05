"""
Management command để đồng bộ dữ liệu thể thao theo lịch trình
Chạy mỗi 5 phút để cập nhật live scores, fixtures và statistics
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.cache import cache
import logging
from datetime import datetime, timedelta

from sports_data.providers.multi_sports_provider import MultiSportsDataProvider
from sports_data.models import Sport, SportsDataProvider as ProviderModel

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Đồng bộ dữ liệu thể thao từ các providers theo lịch trình'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Bắt buộc đồng bộ ngay cả khi cache còn hạn',
        )
        parser.add_argument(
            '--provider',
            type=str,
            help='Chỉ định provider cụ thể để đồng bộ',
        )
        parser.add_argument(
            '--sport',
            type=str,
            help='Chỉ định môn thể thao cụ thể để đồng bộ',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Bắt đầu đồng bộ dữ liệu thể thao...')
        )
        
        start_time = timezone.now()
        force_sync = options['force']
        specific_provider = options['provider']
        specific_sport = options['sport']
        
        try:
            # Khởi tạo multi-provider service
            sports_service = MultiSportsDataProvider()
            
            # Lấy danh sách môn thể thao cần đồng bộ
            if specific_sport:
                sports = Sport.objects.filter(name__icontains=specific_sport, is_active=True)
            else:
                sports = Sport.objects.filter(is_active=True)
            
            total_sports = sports.count()
            self.stdout.write(f"📊 Tổng số môn thể thao cần đồng bộ: {total_sports}")
            
            # Đồng bộ từng môn thể thao
            for sport in sports:
                self.stdout.write(f"🏈 Đang đồng bộ {sport.name}...")
                
                try:
                    # Kiểm tra cache trước khi đồng bộ
                    cache_key = f"sports_data_sync_{sport.name}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    
                    if not force_sync and cache.get(cache_key):
                        self.stdout.write(f"   ⏭️  {sport.name} đã được đồng bộ gần đây, bỏ qua")
                        continue
                    
                    # Đồng bộ live scores
                    self._sync_live_scores(sports_service, sport)
                    
                    # Đồng bộ fixtures
                    self._sync_fixtures(sports_service, sport)
                    
                    # Đồng bộ statistics
                    self._sync_statistics(sports_service, sport)
                    
                    # Đánh dấu đã đồng bộ trong cache (5 phút)
                    cache.set(cache_key, True, 300)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ {sport.name} đồng bộ thành công")
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"   ❌ Lỗi đồng bộ {sport.name}: {str(e)}")
                    )
                    logger.error(f"Error syncing sport {sport.name}: {str(e)}")
                    continue
            
            # Cập nhật provider performance metrics
            self._update_provider_metrics(sports_service)
            
            end_time = timezone.now()
            duration = end_time - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Hoàn thành đồng bộ dữ liệu thể thao trong {duration.total_seconds():.2f} giây'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Lỗi đồng bộ dữ liệu: {str(e)}')
            )
            logger.error(f"Error in sync_sports_data command: {str(e)}")
            raise

    def _sync_live_scores(self, sports_service, sport):
        """Đồng bộ live scores cho môn thể thao"""
        try:
            live_data = sports_service.get_live_scores(sport.name.lower())
            
            if live_data and 'data' in live_data:
                # Cập nhật live scores vào database
                self._update_live_scores_in_db(sport, live_data['data'])
                
        except Exception as e:
            logger.warning(f"Error syncing live scores for {sport.name}: {str(e)}")

    def _sync_fixtures(self, sports_service, sport):
        """Đồng bộ fixtures cho môn thể thao"""
        try:
            # Đồng bộ fixtures cho hôm nay và 7 ngày tới
            for i in range(8):
                date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
                fixtures_data = sports_service.get_fixtures(sport.name.lower(), date)
                
                if fixtures_data and 'data' in fixtures_data:
                    # Cập nhật fixtures vào database
                    self._update_fixtures_in_db(sport, fixtures_data['data'], date)
                    
        except Exception as e:
            logger.warning(f"Error syncing fixtures for {sport.name}: {str(e)}")

    def _sync_statistics(self, sports_service, sport):
        """Đồng bộ statistics cho môn thể thao"""
        try:
            # Cập nhật thống kê cơ bản
            self._update_sport_statistics(sport)
            
        except Exception as e:
            logger.warning(f"Error syncing statistics for {sport.name}: {str(e)}")

    def _update_live_scores_in_db(self, sport, live_data):
        """Cập nhật live scores vào database"""
        # TODO: Implement live score update logic
        pass

    def _update_fixtures_in_db(self, sport, fixtures_data, date):
        """Cập nhật fixtures vào database"""
        # TODO: Implement fixtures update logic
        pass

    def _update_sport_statistics(self, sport):
        """Cập nhật thống kê môn thể thao"""
        # TODO: Implement statistics update logic
        pass

    def _update_provider_metrics(self, sports_service):
        """Cập nhật metrics hiệu suất của providers"""
        try:
            for provider_name, provider in sports_service.providers.items():
                if hasattr(provider, 'get_performance_metrics'):
                    metrics = provider.get_performance_metrics()
                    
                    # Cập nhật vào database
                    provider_model, created = ProviderModel.objects.get_or_create(
                        name=provider_name
                    )
                    
                    if hasattr(provider_model, 'data_accuracy'):
                        provider_model.data_accuracy = metrics.get('accuracy', 0.95)
                        provider_model.update_speed = metrics.get('speed', 30)
                        provider_model.coverage_rate = metrics.get('coverage', 0.90)
                        provider_model.last_successful_update = timezone.now()
                        provider_model.save()
                        
        except Exception as e:
            logger.warning(f"Error updating provider metrics: {str(e)}")

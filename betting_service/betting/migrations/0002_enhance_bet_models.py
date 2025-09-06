# Generated manually for Bet model enhancements

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0001_initial'),
    ]

    operations = [
        # Add new fields to BetSlip model
        migrations.AddField(
            model_name='betslip',
            name='bet_type',
            field=models.CharField(
                choices=[
                    ('SINGLE', 'Single Bet (Cược đơn)'),
                    ('MULTIPLE', 'Multiple Bets (Cược nhiều)'),
                    ('PARLAY', 'Parlay (Cược xiên)'),
                    ('SYSTEM', 'System Bet (Cược hệ thống)')
                ],
                default='SINGLE',
                max_length=20,
                help_text='Loại hình cược'
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='bet_status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pending (Chờ xử lý)'),
                    ('CONFIRMED', 'Confirmed (Đã xác nhận)'),
                    ('CANCELLED', 'Cancelled (Đã hủy)'),
                    ('SETTLED', 'Settled (Đã thanh toán)'),
                    ('CASHED_OUT', 'Cashed Out (Đã rút tiền)')
                ],
                default='PENDING',
                max_length=20,
                help_text='Trạng thái của bet'
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='saga_transaction_id',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                help_text='ID của saga transaction để theo dõi quá trình xử lý'
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='wallet_transaction_id',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                help_text='ID của wallet transaction'
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='confirmed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='betslip',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='betslip',
            name='settled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='betslip',
            name='error_message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='betslip',
            name='retry_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='betslip',
            name='max_retries',
            field=models.IntegerField(default=3),
        ),
        
        # Add new fields to BetSelection model
        migrations.AddField(
            model_name='betselection',
            name='odds_at_placement',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=5,
                help_text='Snapshot của odds tại thời điểm đặt cược',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='betselection',
            name='placement_timestamp',
            field=models.DateTimeField(
                default=django.utils.timezone.now
            ),
        ),
    ]

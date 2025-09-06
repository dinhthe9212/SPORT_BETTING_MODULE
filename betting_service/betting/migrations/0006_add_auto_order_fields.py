# Generated manually for Auto Order Management feature

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0005_add_biweekly_quarterly_periods'),
    ]

    operations = [
        migrations.AddField(
            model_name='betslip',
            name='take_profit_threshold',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Ngưỡng chốt lời - Tự động Cash Out khi đạt mức lợi nhuận này',
                max_digits=10,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='stop_loss_threshold',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Ngưỡng cắt lỗ - Tự động Cash Out khi giảm xuống mức thua lỗ này',
                max_digits=10,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='auto_order_status',
            field=models.CharField(
                choices=[
                    ('INACTIVE', 'Inactive (Không hoạt động)'),
                    ('ACTIVE', 'Active (Đang hoạt động)'),
                    ('TRIGGERED', 'Triggered (Đã kích hoạt)'),
                    ('COMPLETED', 'Completed (Đã hoàn thành)'),
                    ('CANCELLED', 'Cancelled (Đã hủy)'),
                    ('SUSPENDED', 'Suspended (Tạm dừng)'),
                ],
                default='INACTIVE',
                help_text='Trạng thái lệnh tự động',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='auto_order_created_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Thời điểm tạo lệnh tự động',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='auto_order_triggered_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Thời điểm lệnh tự động được kích hoạt',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='auto_order_reason',
            field=models.CharField(
                blank=True,
                help_text='Lý do kích hoạt lệnh tự động (TAKE_PROFIT/STOP_LOSS)',
                max_length=50,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='betslip',
            name='auto_order_enabled',
            field=models.BooleanField(
                default=False,
                help_text='Tính năng lệnh tự động có được bật cho phiếu cược này không'
            ),
        ),
        migrations.AddIndex(
            model_name='betslip',
            index=models.Index(fields=['auto_order_status'], name='betting_bet_auto_or_123456_idx'),
        ),
        migrations.AddIndex(
            model_name='betslip',
            index=models.Index(fields=['auto_order_enabled'], name='betting_bet_auto_or_789012_idx'),
        ),
        migrations.AddIndex(
            model_name='betslip',
            index=models.Index(fields=['take_profit_threshold'], name='betting_bet_take_pr_345678_idx'),
        ),
        migrations.AddIndex(
            model_name='betslip',
            index=models.Index(fields=['stop_loss_threshold'], name='betting_bet_stop_l_901234_idx'),
        ),
    ]

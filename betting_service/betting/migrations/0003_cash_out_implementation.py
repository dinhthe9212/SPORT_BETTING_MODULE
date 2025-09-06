# Generated manually for Cash Out implementation

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0002_enhance_bet_models'),
    ]

    operations = [
        # Add new fields to BetSlip model
        migrations.AddField(
            model_name='betslip',
            name='cash_out_fair_value',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Giá trị công bằng trước khi trừ phí', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='betslip',
            name='cash_out_fee_amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Số tiền phí Cash Out', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='betslip',
            name='cash_out_fee_percentage',
            field=models.DecimalField(blank=True, decimal_places=4, help_text='Tỷ lệ phí Cash Out (0.05 = 5%)', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='betslip',
            name='cash_out_enabled',
            field=models.BooleanField(default=True, help_text='Tính năng Cash Out có được bật cho phiếu cược này không'),
        ),
        migrations.AddField(
            model_name='betslip',
            name='cash_out_before_match',
            field=models.BooleanField(default=False, help_text='Cho phép Cash Out trước khi trận đấu bắt đầu'),
        ),
        migrations.AddField(
            model_name='betslip',
            name='cash_out_requested_at',
            field=models.DateTimeField(blank=True, help_text='Thời điểm yêu cầu Cash Out', null=True),
        ),
        migrations.AddField(
            model_name='betslip',
            name='bet_status',
            field=models.CharField(choices=[('PENDING', 'Pending (Chờ xử lý)'), ('CONFIRMED', 'Confirmed (Đã xác nhận)'), ('CANCELLED', 'Cancelled (Đã hủy)'), ('SETTLED', 'Settled (Đã thanh toán)'), ('CASHED_OUT', 'Cashed Out (Đã rút tiền)'), ('CASHING_OUT', 'Cashing Out (Đang xử lý rút tiền)')], default='PENDING', max_length=20),
        ),
        
        # Add new fields to BetSelection model
        migrations.AddField(
            model_name='betselection',
            name='live_odds_at_cashout',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Live odds tại thời điểm Cash Out', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='betselection',
            name='cashout_timestamp',
            field=models.DateTimeField(blank=True, help_text='Thời điểm Cash Out được thực hiện', null=True),
        ),
        migrations.AddField(
            model_name='betselection',
            name='selection_status',
            field=models.CharField(choices=[('PENDING', 'Pending (Chờ xử lý)'), ('WINNING', 'Winning (Đang thắng)'), ('LOSING', 'Losing (Đã thua)'), ('SETTLED', 'Settled (Đã thanh toán)')], default='PENDING', max_length=20),
        ),
        
        # Create CashOutConfiguration model
        migrations.CreateModel(
            name='CashOutConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookmaker_type', models.CharField(choices=[('SYSTEM', 'System Bookmaker (Nhà cái hệ thống)'), ('COMMUNITY', 'Community Bookmaker (Nhà cái cộng đồng)'), ('INDIVIDUAL', 'Individual User (Người dùng cá nhân)'), ('GROUP', 'Group Users (Nhóm người dùng)')], max_length=20)),
                ('bookmaker_id', models.CharField(help_text='ID của nhà cái (user_id, group_id, hoặc "system")', max_length=255)),
                ('cash_out_fee_percentage', models.DecimalField(blank=True, decimal_places=4, help_text='Tỷ lệ phí Cash Out cụ thể (để trống để sử dụng margin của sự kiện)', max_digits=5, null=True)),
                ('cash_out_enabled', models.BooleanField(default=True, help_text='Bật/tắt tính năng Cash Out')),
                ('cash_out_before_match', models.BooleanField(default=False, help_text='Cho phép Cash Out trước khi trận đấu bắt đầu')),
                ('min_cash_out_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Số tiền Cash Out tối thiểu', max_digits=10, null=True)),
                ('max_cash_out_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Số tiền Cash Out tối đa', max_digits=10, null=True)),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now, help_text='Thời điểm bắt đầu áp dụng cấu hình')),
                ('valid_until', models.DateTimeField(blank=True, help_text='Thời điểm kết thúc áp dụng cấu hình', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_cashout_configs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cash Out Configuration',
                'verbose_name_plural': 'Cash Out Configurations',
            },
        ),
        
        # Create CashOutHistory model
        migrations.CreateModel(
            name='CashOutHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_amount', models.DecimalField(decimal_places=2, help_text='Số tiền Cash Out được yêu cầu', max_digits=10)),
                ('fair_value', models.DecimalField(decimal_places=2, help_text='Giá trị công bằng trước khi trừ phí', max_digits=10)),
                ('fee_amount', models.DecimalField(decimal_places=2, help_text='Số tiền phí Cash Out', max_digits=10)),
                ('fee_percentage', models.DecimalField(decimal_places=4, help_text='Tỷ lệ phí Cash Out', max_digits=5)),
                ('final_amount', models.DecimalField(decimal_places=2, help_text='Số tiền cuối cùng người chơi nhận được', max_digits=10)),
                ('status', models.CharField(choices=[('REQUESTED', 'Requested (Đã yêu cầu)'), ('PROCESSING', 'Processing (Đang xử lý)'), ('COMPLETED', 'Completed (Hoàn thành)'), ('FAILED', 'Failed (Thất bại)'), ('CANCELLED', 'Cancelled (Đã hủy)')], default='REQUESTED', max_length=20)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('original_odds', models.DecimalField(decimal_places=2, help_text='Tỷ lệ cược gốc tại thời điểm đặt cược', max_digits=5)),
                ('live_odds', models.DecimalField(decimal_places=2, help_text='Tỷ lệ cược trực tiếp tại thời điểm Cash Out', max_digits=5)),
                ('saga_transaction_id', models.CharField(blank=True, max_length=255, null=True)),
                ('wallet_transaction_id', models.CharField(blank=True, max_length=255, null=True)),
                ('failure_reason', models.TextField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('bet_slip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cashout_history', to='betting.betslip')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cashout_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cash Out History',
                'verbose_name_plural': 'Cash Out Histories',
                'ordering': ['-requested_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='betslip',
            index=models.Index(fields=['user', 'bet_status'], name='betting_bet_user_id_123456'),
        ),
        migrations.AddIndex(
            model_name='betslip',
            index=models.Index(fields=['is_cash_out_available'], name='betting_bet_is_cash_123456'),
        ),
        migrations.AddIndex(
            model_name='betslip',
            index=models.Index(fields=['cash_out_enabled'], name='betting_bet_cash_ou_123456'),
        ),
        migrations.AddIndex(
            model_name='betslip',
            index=models.Index(fields=['created_at'], name='betting_bet_created_123456'),
        ),
        migrations.AddIndex(
            model_name='cashoutconfiguration',
            index=models.Index(fields=['bookmaker_type', 'bookmaker_id'], name='betting_cash_bookmak_123456'),
        ),
        migrations.AddIndex(
            model_name='cashoutconfiguration',
            index=models.Index(fields=['cash_out_enabled'], name='betting_cash_cash_ou_123456'),
        ),
        migrations.AddIndex(
            model_name='cashoutconfiguration',
            index=models.Index(fields=['valid_from', 'valid_until'], name='betting_cash_valid_f_123456'),
        ),
        migrations.AddIndex(
            model_name='cashouthistory',
            index=models.Index(fields=['user', 'status'], name='betting_cash_user_id_123456'),
        ),
        migrations.AddIndex(
            model_name='cashouthistory',
            index=models.Index(fields=['bet_slip'], name='betting_cash_bet_sli_123456'),
        ),
        migrations.AddIndex(
            model_name='cashouthistory',
            index=models.Index(fields=['requested_at'], name='betting_cash_request_123456'),
        ),
        migrations.AddIndex(
            model_name='cashouthistory',
            index=models.Index(fields=['saga_transaction_id'], name='betting_cash_saga_tr_123456'),
        ),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='cashoutconfiguration',
            unique_together={('bookmaker_type', 'bookmaker_id')},
        ),
    ]

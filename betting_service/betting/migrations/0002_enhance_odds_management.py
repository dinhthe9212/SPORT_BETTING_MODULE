# Generated manually for Odds Management Enhancement

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0001_initial'),
    ]

    operations = [
        # Add new fields to Odd model
        migrations.AddField(
            model_name='odd',
            name='odds_type',
            field=models.CharField(
                choices=[
                    ('STATIC', 'Static (Tỷ lệ cố định)'),
                    ('DYNAMIC', 'Dynamic (Tỷ lệ động)'),
                    ('RISK_BASED', 'Risk-Based (Tỷ lệ dựa trên rủi ro)'),
                ],
                default='STATIC',
                help_text='Loại tỷ lệ: Static, Dynamic, hoặc Risk-Based',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='odds_status',
            field=models.CharField(
                choices=[
                    ('ACTIVE', 'Active (Hoạt động)'),
                    ('SUSPENDED', 'Suspended (Tạm dừng)'),
                    ('CLOSED', 'Closed (Đóng)'),
                    ('LOCKED', 'Locked (Khóa)'),
                ],
                default='ACTIVE',
                help_text='Trạng thái hiện tại của odds',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='base_value',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Giá trị cơ bản của odds (không thay đổi)',
                max_digits=5,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='risk_multiplier',
            field=models.DecimalField(
                decimal_places=2,
                default=1.00,
                help_text='Hệ số nhân rủi ro cho dynamic odds',
                max_digits=5
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='liability_threshold',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Ngưỡng rủi ro tối đa cho phép',
                max_digits=15,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='current_liability',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                help_text='Rủi ro hiện tại đã tích lũy',
                max_digits=15
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='min_value',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Giá trị tối thiểu cho dynamic odds',
                max_digits=5,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='max_value',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Giá trị tối đa cho dynamic odds',
                max_digits=5,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='adjustment_step',
            field=models.DecimalField(
                decimal_places=3,
                default=0.01,
                help_text='Bước điều chỉnh cho dynamic odds',
                max_digits=4
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='last_risk_update',
            field=models.DateTimeField(
                blank=True,
                help_text='Thời điểm cập nhật rủi ro cuối cùng',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_odds',
                to='auth.user'
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='risk_profile_id',
            field=models.CharField(
                blank=True,
                help_text='ID của risk profile từ Risk Management Service',
                max_length=255,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='odd',
            name='auto_adjust_enabled',
            field=models.BooleanField(
                default=False,
                help_text='Bật/tắt tự động điều chỉnh odds theo rủi ro'
            ),
        ),
        
        # Create OddsHistory model
        migrations.CreateModel(
            name='OddsHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_value', models.DecimalField(decimal_places=2, help_text='Giá trị odds cũ', max_digits=5)),
                ('new_value', models.DecimalField(decimal_places=2, help_text='Giá trị odds mới', max_digits=5)),
                ('change_reason', models.CharField(
                    choices=[
                        ('MANUAL_ADJUSTMENT', 'Manual Adjustment (Điều chỉnh thủ công)'),
                        ('RISK_ADJUSTMENT', 'Risk Adjustment (Điều chỉnh theo rủi ro)'),
                        ('MARKET_CHANGE', 'Market Change (Thay đổi thị trường)'),
                        ('LIQUIDITY_ADJUSTMENT', 'Liquidity Adjustment (Điều chỉnh thanh khoản)'),
                        ('STATUS_CHANGE', 'Status Change (Thay đổi trạng thái)'),
                        ('SYSTEM_UPDATE', 'System Update (Cập nhật hệ thống)'),
                        ('PROMOTION_IMPACT', 'Promotion Impact (Tác động khuyến mãi)'),
                    ],
                    help_text='Lý do thay đổi',
                    max_length=50
                )),
                ('risk_liability', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Rủi ro tại thời điểm thay đổi',
                    max_digits=15,
                    null=True
                )),
                ('risk_multiplier', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Hệ số rủi ro tại thời điểm thay đổi',
                    max_digits=5,
                    null=True
                )),
                ('additional_data', models.JSONField(
                    blank=True,
                    default=dict,
                    help_text='Dữ liệu bổ sung (status changes, market data, etc.)'
                )),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('risk_profile_id', models.CharField(
                    blank=True,
                    help_text='ID của risk profile từ Risk Management Service',
                    max_length=255,
                    null=True
                )),
                ('risk_alert_id', models.CharField(
                    blank=True,
                    help_text='ID của risk alert nếu có',
                    max_length=255,
                    null=True
                )),
                ('odd', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='history',
                    to='betting.odd'
                )),
                ('changed_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='odds_changes',
                    to='auth.user'
                )),
            ],
            options={
                'verbose_name_plural': 'Odds History',
                'ordering': ['-timestamp'],
            },
        ),
        
        # Add indexes for performance
        migrations.AddIndex(
            model_name='odd',
            index=models.Index(fields=['odds_type', 'odds_status'], name='betting_odd_odds_ty_8a1b2c_idx'),
        ),
        migrations.AddIndex(
            model_name='odd',
            index=models.Index(fields=['match', 'is_active'], name='betting_odd_match_i_9b2c3d_idx'),
        ),
        migrations.AddIndex(
            model_name='odd',
            index=models.Index(fields=['last_risk_update'], name='betting_odd_last_ri_4c5d6e_idx'),
        ),
        migrations.AddIndex(
            model_name='oddshistory',
            index=models.Index(fields=['odd', 'timestamp'], name='betting_oddsh_odd_id_7d8e9f_idx'),
        ),
        migrations.AddIndex(
            model_name='oddshistory',
            index=models.Index(fields=['change_reason', 'timestamp'], name='betting_oddsh_chang_0f1g2h_idx'),
        ),
        migrations.AddIndex(
            model_name='oddshistory',
            index=models.Index(fields=['risk_liability'], name='betting_oddsh_risk_l_3g4h5i_idx'),
        ),
    ]

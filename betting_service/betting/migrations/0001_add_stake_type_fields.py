# Generated manually for adding stake_type and fixed_stake_value fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='stake_type',
            field=models.CharField(
                choices=[
                    ('FREE', 'Free Stake (Cược miễn phí)'),
                    ('FIXED', 'Fixed Stake (Cược cố định)')
                ],
                default='FREE',
                help_text='Loại hình sự kiện: Free stake hoặc Fixed stake',
                max_length=10
            ),
        ),
        migrations.AddField(
            model_name='match',
            name='fixed_stake_value',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Giá trị cố định cho Fixed stake (chỉ áp dụng khi stake_type = FIXED)',
                max_digits=10,
                null=True
            ),
        ),
    ]

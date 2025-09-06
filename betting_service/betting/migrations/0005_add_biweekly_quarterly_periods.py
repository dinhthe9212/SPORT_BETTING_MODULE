# Generated manually for adding BIWEEKLY and QUARTERLY periods

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0004_add_leaderboard_statistics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstatistics',
            name='period',
            field=models.CharField(
                choices=[
                    ('DAILY', 'Daily (Hàng ngày)'),
                    ('WEEKLY', 'Weekly (Hàng tuần)'),
                    ('BIWEEKLY', 'Biweekly (2 tuần)'),
                    ('MONTHLY', 'Monthly (Hàng tháng)'),
                    ('QUARTERLY', 'Quarterly (Theo quý)'),
                    ('YEARLY', 'Yearly (Hàng năm)'),
                    ('ALL_TIME', 'All Time (Tất cả thời gian)'),
                ],
                default='ALL_TIME',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='leaderboard',
            name='period',
            field=models.CharField(
                choices=[
                    ('DAILY', 'Daily (Hàng ngày)'),
                    ('WEEKLY', 'Weekly (Hàng tuần)'),
                    ('BIWEEKLY', 'Biweekly (2 tuần)'),
                    ('MONTHLY', 'Monthly (Hàng tháng)'),
                    ('QUARTERLY', 'Quarterly (Theo quý)'),
                    ('YEARLY', 'Yearly (Hàng năm)'),
                    ('ALL_TIME', 'All Time (Tất cả thời gian)'),
                ],
                default='WEEKLY',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='bettingstatistics',
            name='period',
            field=models.CharField(
                choices=[
                    ('DAILY', 'Daily (Hàng ngày)'),
                    ('WEEKLY', 'Weekly (Hàng tuần)'),
                    ('BIWEEKLY', 'Biweekly (2 tuần)'),
                    ('MONTHLY', 'Monthly (Hàng tháng)'),
                    ('QUARTERLY', 'Quarterly (Theo quý)'),
                    ('YEARLY', 'Yearly (Hàng năm)'),
                    ('ALL_TIME', 'All Time (Tất cả thời gian)'),
                ],
                default='DAILY',
                max_length=20
            ),
        ),
    ]

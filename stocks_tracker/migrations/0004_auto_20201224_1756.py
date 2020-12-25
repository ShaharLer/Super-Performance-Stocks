# Generated by Django 3.1.2 on 2020-12-24 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks_tracker', '0003_auto_20201224_1725'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock_stat',
            name='date',
        ),
        migrations.AddField(
            model_name='stock_stat',
            name='yahoo_date_format',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
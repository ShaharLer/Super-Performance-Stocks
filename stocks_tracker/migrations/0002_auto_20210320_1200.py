# Generated by Django 3.1.2 on 2021-03-20 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='ev_to_sell_ratio',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='ps_to_growth_ratio',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]

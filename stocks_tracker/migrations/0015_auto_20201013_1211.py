# Generated by Django 3.1.2 on 2020-10-13 09:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stocks_tracker', '0014_auto_20201013_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='last_scrapper_updated',
            field=models.DateField(default=datetime.datetime(2020, 10, 13, 9, 11, 55, 441825, tzinfo=utc), verbose_name='Last scrapper1 update'),
        ),
    ]

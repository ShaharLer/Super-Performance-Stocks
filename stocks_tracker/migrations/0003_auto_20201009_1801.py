# Generated by Django 3.1.2 on 2020-10-09 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks_tracker', '0002_auto_20201009_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='last_scrapper_updated',
            field=models.DateTimeField(verbose_name='Last scrapper update'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='last_technically_updated',
            field=models.DateTimeField(null=True, verbose_name='Last technical update'),
        ),
    ]
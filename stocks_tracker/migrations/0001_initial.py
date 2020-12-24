# Generated by Django 3.1.2 on 2020-12-24 12:39

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('net_income_growth', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('eps_growth', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('sales_growth', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('pivot', models.FloatField(blank=True, default=None, null=True)),
                ('is_scrapper_succeeded', models.BooleanField(null=True)),
                ('is_accelerated', models.BooleanField(null=True)),
                ('is_eps_growth', models.BooleanField(null=True)),
                ('is_technically_valid', models.BooleanField(null=True)),
                ('is_breakout', models.BooleanField(null=True)),
                ('last_scrapper_update', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last scrapper update')),
                ('last_rater_update', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last rater update')),
                ('last_technically_valid_update', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last technical update')),
                ('last_breakout', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last breakout')),
                ('is_high_tight_flag_exists', models.BooleanField(default=False)),
                ('high_tight_flag_data', models.CharField(blank=True, max_length=500, null=True)),
                ('is_stock_in_watchlist', models.BooleanField(null=True)),
            ],
            options={
                'ordering': ['symbol'],
            },
        ),
    ]


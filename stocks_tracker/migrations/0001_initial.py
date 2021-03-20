# Generated by Django 3.1.2 on 2021-01-29 12:29

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
                ('sector', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('industry', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('net_income_growth_q', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('eps_growth_q', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('sales_growth_q', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('net_income_growth_y', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('eps_growth_y', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('sales_growth_y', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=None, null=True, size=None)),
                ('pivot', models.FloatField(blank=True, default=None, null=True)),
                ('is_scrapper_succeeded_q', models.BooleanField(null=True)),
                ('is_scrapper_succeeded_y', models.BooleanField(null=True)),
                ('is_accelerated_q', models.BooleanField(null=True)),
                ('is_eps_growth_q', models.BooleanField(null=True)),
                ('is_accelerated_y', models.BooleanField(null=True)),
                ('is_eps_growth_y', models.BooleanField(null=True)),
                ('is_technically_valid', models.BooleanField(null=True)),
                ('is_breakout', models.BooleanField(null=True)),
                ('last_scrapper_update', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last scrapper update')),
                ('last_rater_update', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last rater update')),
                ('last_technically_valid_update', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last technical update')),
                ('last_breakout', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last breakout')),
                ('is_high_tight_flag_exists', models.BooleanField(default=False)),
                ('high_tight_flag_data', models.CharField(blank=True, max_length=500, null=True)),
                ('is_stock_in_watchlist', models.BooleanField(null=True)),
                ('target_avg_sales', models.CharField(blank=True, max_length=500, null=True)),
                ('target_avg_eps', models.CharField(blank=True, max_length=500, null=True)),
                ('target_sales_growth', models.CharField(blank=True, max_length=500, null=True)),
                ('is_growth_potential', models.BooleanField(null=True)),
                ('is_yahoo_scrapper_succeeded', models.BooleanField(null=True)),
                ('price_to_sell_ratio', models.FloatField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ['symbol'],
            },
        ),
    ]

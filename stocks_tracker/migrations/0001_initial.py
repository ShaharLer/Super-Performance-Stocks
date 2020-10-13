# Generated by Django 3.1.2 on 2020-10-09 14:19

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
                ('symbol', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('eps_growth', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(null=True), size=None)),
                ('sales_growth', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(null=True), size=None)),
                ('net_income_growth', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(null=True), size=None)),
                ('pivot', models.FloatField(null=True)),
                ('is_accelerated', models.BooleanField(null=True)),
                ('is_eps_growth', models.BooleanField(null=True)),
                ('is_technically_valid', models.BooleanField(null=True)),
                ('last_scrapper_updated', models.DateTimeField(verbose_name='Last updated by the stock scrapper')),
                ('last_technically_updated', models.DateTimeField(verbose_name='Last updated by the technical validation script')),
            ],
        ),
    ]

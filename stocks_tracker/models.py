from django.db import models
from django.contrib.postgres.fields import ArrayField
import datetime


class Stock(models.Model):
    symbol = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    net_income_growth = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    eps_growth = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    sales_growth = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    pivot = models.FloatField(null=True, blank=True, default=None)
    is_scrapper_succeeded = models.BooleanField(null=True)
    is_accelerated = models.BooleanField(null=True)
    is_eps_growth = models.BooleanField(null=True)
    is_technically_valid = models.BooleanField(null=True)
    last_scrapper_update = models.DateField('Last scrapper update', default=datetime.date.today())
    last_rater_update = models.DateField('Last rater update', null=True, blank=True, default=None)
    last_technically_valid_update = models.DateField('Last technical update', null=True, blank=True, default=None)
    last_breakout = models.DateField('Last breakout', null=True, blank=True, default=None)
    current_stage_number = models.IntegerField(null=True, blank=True, default=None)
    is_high_tight_flag_pattern = models.BooleanField(default = False)
    high_tight_flag_details = models.TextField(null=True,blank=True)


    def __str__(self):
        return self.symbol

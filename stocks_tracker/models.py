from django.db import models
from django.contrib.postgres.fields import ArrayField


class Stock(models.Model):
    symbol = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    net_income_growth_q = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    eps_growth_q = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    sales_growth_q = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    net_income_growth_y = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    eps_growth_y = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    sales_growth_y = ArrayField(models.FloatField(), null=True, blank=True, default=None)
    pivot = models.FloatField(null=True, blank=True, default=None)
    is_scrapper_succeeded_q = models.BooleanField(null=True)
    is_scrapper_succeeded_y = models.BooleanField(null=True)
    is_accelerated_q = models.BooleanField(null=True)
    is_eps_growth_q = models.BooleanField(null=True)
    is_accelerated_y = models.BooleanField(null=True)
    is_eps_growth_y = models.BooleanField(null=True)
    is_technically_valid = models.BooleanField(null=True)
    is_breakout = models.BooleanField(null=True)
    last_scrapper_update = models.DateTimeField('Last scrapper update', null=True, blank=True, default=None)
    last_rater_update = models.DateTimeField('Last rater update', null=True, blank=True, default=None)
    last_technically_valid_update = models.DateTimeField('Last technical update', null=True, blank=True, default=None)
    last_breakout = models.DateTimeField('Last breakout', null=True, blank=True, default=None)
    is_high_tight_flag_exists = models.BooleanField(default = False)
    high_tight_flag_data = models.CharField(null=True,blank=True,max_length=500)
    is_stock_in_watchlist = models.BooleanField(null=True)
    target_avg_sales = models.CharField(null=True,blank=True,max_length=500)
    target_avg_eps = models.CharField(null=True,blank=True,max_length=500)
    target_sales_growth = models.CharField(null=True,blank=True,max_length=500)
    is_growth_potential = models.BooleanField(null=True)
    is_yahoo_scrapper_succeeded = models.BooleanField(null=True)

    class Meta:
        ordering = ['symbol']

    def __str__(self):
        return self.symbol

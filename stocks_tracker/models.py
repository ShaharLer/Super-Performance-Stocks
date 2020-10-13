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
    last_scrapper_updated = models.DateField('Last scrapper update', default=datetime.date.today())
    last_technically_updated = models.DateField('Last technical update', null=True, blank=True, default=None)

    def __str__(self):
        return self.symbol
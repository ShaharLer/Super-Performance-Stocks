from rest_framework import serializers
from . import models


class HelloSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stock
        fields = ('id', 'symbol', 'name', 'net_income_growth', 'eps_growth', 'sales_growth', 'pivot', 'is_accelerated',
                  'is_eps_growth', 'is_technically_valid', 'last_scrapper_updated', 'last_technically_updated')

from rest_framework import serializers
from . import models


class TechnicalStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stock
        fields = ('symbol', 'name', 'pivot')


class BreakoutStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stock
        fields = ('symbol', 'name', 'pivot', 'last_breakout')


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stock
        fields = ('symbol', 'name', 'sector', 'industry', 'price_to_sell_ratio')

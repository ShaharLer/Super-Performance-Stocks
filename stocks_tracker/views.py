from django.http import HttpResponse
from rest_framework import viewsets
from django.shortcuts import render
from stocks_tracker.utils.breakout.breakout_stocks import *
from stocks_tracker.utils.rater.stocks_rater import *
from stocks_tracker.utils.scrapper.marketwatch_scrapper import *
from stocks_tracker.utils.technical.technical_analsys_of_stock import *
from stocks_tracker.utils.volume.volume_watchlist_of_valid_stock import *
from .serializers import TechnicalStockSerializer, BreakoutStockSerializer
from django.http import JsonResponse


class TechnicallyValidStocksViewSet(viewsets.ModelViewSet):
    serializer_class = TechnicalStockSerializer
    queryset = Stock.objects.filter(is_technically_valid=True).order_by('symbol')


class BreakoutStocksViewSet(viewsets.ModelViewSet):
    serializer_class = BreakoutStockSerializer
    queryset = Stock.objects.filter(last_breakout__isnull=False).order_by('symbol')


def count_stocks(request):
    total_stocks = Stock.objects.all().count()
    return HttpResponse('Total number of stocks in DB is: {total_stocks}')


def stocks_scrapper(request):
    marketwatch_scrapper_main()
    return HttpResponse('Finished stocks_scrapper')


def stock_rater(request):
    stocks_rater_main()
    return HttpResponse('Finished stock_rater')


def technically_valid_stocks(request):
    technically_valid_stocks_main()
    return HttpResponse('Finished technically_valid_stocks')


def breakout_stocks(request):
    breakout_stocks_main()
    return HttpResponse('Finished breakout_stocks')

def volume_watchlist(request):
    return render(request, 'home_page.html')

def volume_update(request):
    data = volume_watchlist_of_valid_stock_main()
    return JsonResponse(data, safe=False)

from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from stocks_tracker.utils.breakout.breakout_stocks import breakout_stocks_main
from stocks_tracker.utils.nasdaq.nasdaq_composite_info import nasdaq_composite_info_main
from stocks_tracker.utils.rater.stocks_rater import stocks_rater_main
from stocks_tracker.utils.scrapper.marketwatch_scrapper import marketwatch_scrapper_main
from stocks_tracker.utils.technical.technical_analsys_of_stock import technically_valid_stocks_main
from .models import Stock
from .serializers import TechnicalStockSerializer, BreakoutStockSerializer


class TechnicallyValidStocksViewSet(viewsets.ModelViewSet):
    serializer_class = TechnicalStockSerializer
    queryset = Stock.objects.filter(is_technically_valid=True).order_by('symbol')


class BreakoutStocksViewSet(viewsets.ModelViewSet):
    serializer_class = BreakoutStockSerializer
    queryset = Stock.objects.filter(last_breakout__isnull=False).order_by('symbol')


def count_stocks(request):
    total_stocks = Stock.objects.all().count()
    return HttpResponse(f'Total number of stocks in DB is: {total_stocks}')


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


def get_nasdaq_composite_response(nasdaq_composite):
    try:
        response = [
            {
                'ma3': nasdaq_composite.get_ma_3(),
                'ma3Change': nasdaq_composite.get_ma_3_change(),
                'ma7': nasdaq_composite.get_ma_7(),
                'ma7Change': nasdaq_composite.get_ma_7_change(),
                'isBuyMarket': nasdaq_composite.get_is_a_buy_market()
            }
        ]
        return Response(response)
    except:
        return Response([])


@api_view(['GET'])
def nasdaq_info(request):
    nasdaq_composite = nasdaq_composite_info_main()
    return get_nasdaq_composite_response(nasdaq_composite)

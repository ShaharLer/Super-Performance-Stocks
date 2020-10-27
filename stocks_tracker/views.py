from datetime import datetime

import dateutil.parser
from django.http import HttpResponse
from rest_framework import viewsets, status
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


def get_nasdaq_composite_response(nasdaq_composite_info_list):
    try:
        response = []
        for nasdaq_composite_info in nasdaq_composite_info_list:
            nasdaq_composite_object = {
                'date': nasdaq_composite_info.get_date(),
                'ma3': nasdaq_composite_info.get_ma_3(),
                'ma3Change': nasdaq_composite_info.get_ma_3_change(),
                'ma7': nasdaq_composite_info.get_ma_7(),
                'ma7Change': nasdaq_composite_info.get_ma_7_change(),
                'isBuyMarket': nasdaq_composite_info.get_is_a_buy_market()
            }
            response.append(nasdaq_composite_object)
        return Response(response, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Failed to parse info from the server'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_incorrect_dates_range_error_response(start_date, end_date):
    start_date = start_date.strftime("%d-%m-%Y")
    end_date = end_date.strftime("%d-%m-%Y")
    return Response({'message': f'start_date ({start_date}) cannot be greater than end_date ({end_date})'},
                    status=status.HTTP_400_BAD_REQUEST)


def parse_date(request, param):
    date = request.GET.get(param, '')
    date = dateutil.parser.isoparse(date).date() if date else date
    return date


def parse_dates(request, start_date_param, end_date_param):
    start_date = parse_date(request, start_date_param)
    end_date = parse_date(request, end_date_param)

    if start_date and not end_date:
        end_date = start_date
    elif end_date and not start_date:
        start_date = end_date
    elif not start_date and not end_date:
        start_date = datetime.today().date()
        end_date = datetime.today().date()

    return start_date, end_date


@api_view(['GET'])
def nasdaq_info(request):
    start_date, end_date = parse_dates(request, 'start_date', 'end_date')

    if end_date < start_date:
        return get_incorrect_dates_range_error_response(start_date, end_date)

    nasdaq_composite_info_list = nasdaq_composite_info_main(start_date, end_date)
    return get_nasdaq_composite_response(nasdaq_composite_info_list)

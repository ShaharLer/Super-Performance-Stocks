from datetime import datetime
from django.http import JsonResponse
import dateutil.parser
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from stocks_tracker.utils.breakout.breakout_stocks import breakout_stocks_main
from stocks_tracker.utils.nasdaq.nasdaq_composite_info import nasdaq_composite_info_main
from stocks_tracker.utils.pivot.pivot_processing import update_stock_in_db
from stocks_tracker.utils.rater.stocks_rater import stocks_rater_main
from stocks_tracker.utils.scrapper.marketwatch_scrapper import marketwatch_scrapper_main
from stocks_tracker.utils.technical.technical_analsys_of_stock import technically_valid_stocks_main
from stocks_tracker.utils.Chart_patterns.high_tight_flag import high_tight_flag_main
from .models import Stock
from .serializers import TechnicalStockSerializer, BreakoutStockSerializer

NASDAQ_FROM_DATE_KEY = 'from_date'
NASDAQ_TO_DATE_KEY = 'to_date'
STOCK_SYMBOL_KEY = 'symbol'
STOCK_PIVOT_KEY = 'pivot'


class TechnicallyValidStocksViewSet(viewsets.ModelViewSet):
    serializer_class = TechnicalStockSerializer
    queryset = Stock.objects.filter(is_technically_valid=True).order_by('symbol')


class BreakoutStocksViewSet(viewsets.ModelViewSet):
    serializer_class = BreakoutStockSerializer
    queryset = Stock.objects.filter(last_breakout__isnull=False).order_by('symbol')


def count_stocks(request):
    total_stocks = Stock.objects.all().count()
    return HttpResponse(f'Total number of stocks in DB is: {total_stocks}')


def parse_params(params, symbol_key, pivot_key):
    symbol = params.get(symbol_key, '')
    pivot_value = params.get(pivot_key, '')
    return symbol, pivot_value


def get_response_object(message, status_code):
    return Response({'message': message}, status=status_code)


def get_response_message_and_code(request):
    if not request.data:
        return 'No parameters were given', status.HTTP_400_BAD_REQUEST

    symbol, pivot_value = parse_params(request.data, STOCK_SYMBOL_KEY, STOCK_PIVOT_KEY)
    if not symbol or not pivot_value:
        return 'Both symbol and pivot should be given the request', status.HTTP_400_BAD_REQUEST

    try:
        pivot_value = float(pivot_value)
    except Exception as e:
        return 'Pivot must be a float number', status.HTTP_400_BAD_REQUEST

    updated_stock = update_stock_in_db(symbol, pivot_value)
    if not updated_stock:
        return 'Failed to update pivot for the stock', status.HTTP_500_INTERNAL_SERVER_ERROR

    return f'Stock {symbol} was updated successfully with pivot {pivot_value}', status.HTTP_200_OK


@api_view(['PUT'])
def pivot(request):
    message, status_code = get_response_message_and_code(request)
    return get_response_object(message, status_code)


def stocks_scrapper(request):
    marketwatch_scrapper_main()
    return HttpResponse('Finished stocks_scrapper')


def stock_rater(request):
    stocks_rater_main()
    return HttpResponse('Finished stock_rater')

def top(request):
    data = market_top_main()
    return JsonResponse(data, safe=False)

def stage_analysys(request):
    stage_main()
    return HttpResponse('Finished stage_main')

def technically_valid_stocks(request):
    technically_valid_stocks_main()
    return HttpResponse('Finished technically_valid_stocks')


def breakout_stocks(request):
    breakout_stocks_main()
    return HttpResponse('Finished breakout_stocks')

def high_tight_flag(request):
    high_tight_flag_main()
    return HttpResponse('Finished high tight flag evaluation')

def get_nasdaq_composite_response(nasdaq_composite_info_list):
    try:
        response = []
        for nasdaq_composite_info in nasdaq_composite_info_list:
            nasdaq_composite_object = {
                'date': nasdaq_composite_info.get_date().strftime('%d-%m-%Y'),
                'ma3': nasdaq_composite_info.get_ma_3(),
                'ma3Change': f'{nasdaq_composite_info.get_ma_3_change()}%',
                'ma7': nasdaq_composite_info.get_ma_7(),
                'ma7Change': f'{nasdaq_composite_info.get_ma_7_change()}%',
                'action': nasdaq_composite_info.get_market_action().value
            }
            response.append(nasdaq_composite_object)
        return Response(response, status=status.HTTP_200_OK)
    except:
        error_message = 'Failed to parse info from the server'
        return Response({'message': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_incorrect_dates_range_error_response(from_date, to_date):
    from_date = from_date.strftime("%d-%m-%Y")
    to_date = to_date.strftime("%d-%m-%Y")
    error_message = f'{NASDAQ_FROM_DATE_KEY} ({from_date}) cannot be greater than {NASDAQ_TO_DATE_KEY} ({to_date})'
    return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


def parse_date(params, param):
    date = params.get(param, '')
    return dateutil.parser.isoparse(date).date() if date else date


def parse_dates(params, from_date_param, to_date_param):
    from_date = parse_date(params, from_date_param)
    to_date = parse_date(params, to_date_param)

    if from_date and not to_date:
        to_date = from_date
    elif to_date and not from_date:
        from_date = to_date
    elif not from_date and not to_date:
        from_date = datetime.today().date()
        to_date = datetime.today().date()

    return from_date, to_date


@api_view(['GET'])
def nasdaq_info(request):
    from_date, to_date = parse_dates(request.GET, NASDAQ_FROM_DATE_KEY, NASDAQ_TO_DATE_KEY)

    if to_date < from_date:
        return get_incorrect_dates_range_error_response(from_date, to_date)

    nasdaq_composite_info_list = nasdaq_composite_info_main(from_date, to_date)
    return get_nasdaq_composite_response(nasdaq_composite_info_list)

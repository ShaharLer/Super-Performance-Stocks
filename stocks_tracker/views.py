from django.http import HttpResponse
from rest_framework import viewsets

from stocks_tracker.utils.breakout.breakout_stocks import *
from stocks_tracker.utils.rater.stocks_rater import *
from stocks_tracker.utils.scrapper.marketwatch_scrapper import *
from stocks_tracker.utils.technical.technical_analsys_of_stock import *
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


"""
class HelloApiView(APIView):
    serializer_classes = HelloSerializer

    def get(self, request, format=None):
        a_list = [
            'shahar',
            'tal',
            'nala'
        ]

        return Response({'message': 'Hello!', 'a_list': a_list})

    def post(self, request):
        serializer = HelloSerializer(data=request.data)

        if serializer.is_valid():
            name = serializer.data.get('name')
            message = f'Hello {name}'
            return Response({'message': message})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return Response({'method': 'put'})

    def patch(self, request, pk=None):
        return Response({'method': 'patch'})

    def delete(self, request, pk=None):
        return Response({'method': 'delete'})


class HelloViewSet(viewsets.ViewSet):

    def list(self, request):
        a_list = [
            'Marta',
            'Max',
            'Mika'
        ]
        return Response({'message': 'Hello!', 'a_list': a_list})

    def create(self, request):
        serializer = HelloSerializer(data=request.data)

        if serializer.is_valid():
            name = serializer.data.get('name')
            message = f'Hello {name}'
            return Response({'message': message})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        return Response({'http_method': 'GET'})

    def update(self, request, pk=None):
        return Response({'http_method': 'PUT'})

    def partial_update(self, request, pk=None):
        return Response({'http_method': 'PATCH'})

    def destroy(self, request, pk=None):
        return Response({'http_method': 'DELETE'})


# Get stocks_tracker and display them
def index(request):
    stocks_list = models.objects.all()
    return render(request, 'stocks_tracker/index.html')

"""

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import StockSerializer
from stocks_tracker.utils.Scrapper.marketwatch_scrapper import *
from stocks_tracker.utils.Rater.stocks_rater import *
from stocks_tracker.utils.Technical.technical_analsys_of_stock import *
from stocks_tracker.utils.Breakout.breakout_stocks import *


class StockViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    queryset = Stock.objects.all().order_by('symbol')


@api_view(['GET'])
def stocks_scrapper(request):
    marketwatch_scrapper_main()
    return Response({"message": "finished stocks_scrapper"})


@api_view(['GET'])
def stock_rater(request):
    stocks_rater_main()
    return Response({"message": "finished stock_rater"})


@api_view(['GET'])
def technically_valid_stocks(request):
    technically_valid_stocks_main()
    return Response({"message": "finished technically_valid_stocks"})


@api_view(['GET'])
def breakout_stocks(request):
    breakout_stocks_main()
    return Response({"message": "finished breakout_stocks"})


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

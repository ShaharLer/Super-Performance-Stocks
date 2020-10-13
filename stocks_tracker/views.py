from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import StockSerializer, HelloSerializer
from .models import Stock

from .utils.marketwatch_scrapper import *

# from rest_framework.decorators import api_view
# from stocks_tracker.serializers import StockSerializer


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


class StockViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    queryset = Stock.objects.all().order_by('symbol')


@api_view(['GET'])
def run_scrapper(request):
    marketwatch_scrapper_main()

    # stock1 = Stock.objects.get(symbol="A")
    """
    if len(Stock.objects.filter(symbol="RFIL")) == 0:
        stock = Stock()
        stock.symbol = "RFIL"
        stock.name = "RF-Industries"
        stock.last_scrapper_updated = "2020-10-12T15:48:00Z"
        stock.save()
    else:
        stock = Stock.objects.get(symbol="RFIL")
        stock.name = "RF-Industries test"
        stock.save()
        # stock.delete()
    """

    return Response({"message": "finished"})


"""
# Get stocks_tracker and display them
def index(request):
    stocks_list = models.objects.all()
    return render(request, 'stocks_tracker/index.html')

"""

# def home(request):
#     return HttpResponse("Hello World")

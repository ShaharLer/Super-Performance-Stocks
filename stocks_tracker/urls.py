from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('stock', views.StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('scrapper/', views.stocks_scrapper),
    path('rater/', views.stock_rater),
    path('technical/', views.technically_valid_stocks),
    path('breakout/', views.breakout_stocks),
]

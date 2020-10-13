from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('stock', views.StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('scrapper/', views.run_stocks_scrapper),
    path('rater/', views.run_stock_rater),
]

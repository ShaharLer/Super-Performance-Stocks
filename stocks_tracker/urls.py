from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('technically-valid', views.TechnicallyValidStocksViewSet)
router.register('breakout', views.BreakoutStocksViewSet)

urlpatterns = [
    path('stocks/', include(router.urls)),
    path('count/', views.count_stocks),
    path('pivot/', views.pivot),
    path('pivot/<str:symbol>/', views.pivot),
    path('scrapper/', views.stocks_scrapper),
    path('rater/', views.stock_rater),
    path('technical/', views.technically_valid_stocks),
    path('breakout/', views.breakout_detector),
    path('nasdaq/', views.nasdaq_info),
    path('flag/', views.high_tight_flag),
    path('background/', views.process_background_tasks),
    path('volume_update/', views.volume_update),
    path('get_stock_info',views.get_stock_info),
    path('remove_from_watchlist',views.remove_stock_from_watchlist),
    path('stock_stats/',views.stock_stats)
]

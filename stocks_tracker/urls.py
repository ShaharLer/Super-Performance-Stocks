from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('stocks/technical', views.TechnicallyValidStocksViewSet)
router.register('stocks/breakout', views.BreakoutStocksViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stocks/count/', views.count_stocks),
    path('scrapper/', views.stocks_scrapper),
    path('rater/', views.stock_rater),
    path('technical/', views.technically_valid_stocks),
    path('breakout/', views.breakout_stocks),
    path('volume-watchlist/', views.volume_watchlist),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.urls import path
from django.conf.urls import include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
# router.register('hello-viewset', views.HelloViewSet, basename='hello-viewset')
router.register('stock', views.StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('scrapper/', views.run_scrapper),
    # path('hello-view', views.HelloApiView.as_view()),
    # path('home', views.index, name='index'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import  convert_amount, CurrencyViewSet
from api.views import TimeSeriesExchangeRatesView

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')

urlpatterns = [
    #path('currency_rates_list/', currency_rates_list, name='currency_rates_list'),
    path('convert_amount/', convert_amount, name='convert_amount'),
    path('', include(router.urls)),  # Includes all Currency CRUD routes
    path('time_series_exchange_rate/', TimeSeriesExchangeRatesView.as_view(), name='time_series_exchange_rate'),

]
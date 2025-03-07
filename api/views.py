from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from api.models import CurrencyExchangeRate, Currency
from api.services import get_exchange_rate
from api.services_time_series import fetch_time_series_data
from datetime import date
from api.serializers import CurrencySerializer
from django.db.models import Q
import requests
from django.http import JsonResponse


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Currency deleted successfully"}, status=status.HTTP_200_OK)  
    


@api_view(['GET'])
def convert_amount(request):
    """
    API to convert an amount from one currency to another.
    """
    source_currency = request.GET.get("source_currency")
    exchanged_currency = request.GET.get("exchanged_currency")
    amount = request.GET.get("amount")

    if not all([source_currency, exchanged_currency, amount]):
        return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if currencies exist in the database
    if not Currency.objects.filter(code=source_currency).exists():
        return JsonResponse({"error": f"Unsupported currency: {source_currency}"}, status=400)

    if not Currency.objects.filter(code=exchanged_currency).exists():
        return JsonResponse({"error": f"Unsupported currency: {exchanged_currency}"}, status=400)

    rate_data = get_exchange_rate(source_currency, exchanged_currency, '2025-03-07')
    if rate_data:
        converted_amount = float(amount) * float(rate_data["rate_value"])
        return Response({
            "source_currency": source_currency,
            "exchanged_currency": exchanged_currency,
            "valuation_date": date.today(),
            "rate_value": rate_data["rate_value"],
            "converted_amount": str(converted_amount)
        }, status=status.HTTP_200_OK)

    return Response({"error": "Exchange rate not found"}, status=status.HTTP_404_NOT_FOUND)



class TimeSeriesExchangeRatesView(APIView):
    """
    API to fetch a time series list of exchange rates for the source currency.
    It returns only those exchanged currencies that are stored in the DB.
    The user only passes source_currency, start_date, and end_date.
    """

    def get(self, request):
        source_currency = request.GET.get("source_currency")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        
        # Validate required parameters
        if not source_currency or not start_date or not end_date:
            return Response(
                {"error": "Missing required parameters: source_currency, start_date, end_date"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if currency exist in the database
        if not Currency.objects.filter(code=source_currency).exists():
            return JsonResponse({"error": f"Unsupported currency: {source_currency}"}, status=400)

        # Fetch time series data (from DB or external provider)
        rate_data = fetch_time_series_data(source_currency, start_date, end_date)

        if not rate_data:
            return Response(
                {"error": "Exchange rate data not available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(rate_data, status=status.HTTP_200_OK)
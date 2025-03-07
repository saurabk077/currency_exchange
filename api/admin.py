from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from datetime import datetime
import logging

from .models import Currency, CurrencyExchangeRate

logger = logging.getLogger(__name__)

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol")
    list_display_links = ["name"]
    list_editable = ["symbol"]


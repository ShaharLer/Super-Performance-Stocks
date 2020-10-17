from django.contrib import admin
from .models import Stock

admin.site.site_header = "Stocks-Tracker admin"
admin.site.site_title = "Stocks-Tracker admin area"
admin.site.index_title = "Welcome to the Stocks-Tracker admin area"

admin.site.register(Stock)

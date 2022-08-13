from src.models import CustomUser, Request, Invoice
from django.contrib import admin
from django.contrib.admin import ModelAdmin

admin.site.register(CustomUser, ModelAdmin)
admin.site.register(Invoice)
admin.site.register(Request)

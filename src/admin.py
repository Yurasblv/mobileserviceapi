from src.models import User, Request, Invoice
from django.contrib import admin
from django.contrib.admin import ModelAdmin

admin.site.register(User, ModelAdmin)
admin.site.register(Invoice)
admin.site.register(Request)

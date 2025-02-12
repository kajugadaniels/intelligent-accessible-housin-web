from django.contrib import admin
from frontend.models import *

class RentApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'status', 'created_at')
    search_fields = ('user',)
    ordering = ('-created_at',)

admin.site.register(RentApplication, RentApplicationAdmin)
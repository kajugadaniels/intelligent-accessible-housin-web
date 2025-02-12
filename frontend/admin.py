from django.contrib import admin
from .models import RentApplication
from backend.models import User, Property

class RentApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'status', 'created_at', 'preferred_move_in_date')
    list_filter = ('status', 'user', 'property', 'created_at')
    search_fields = ('user__name', 'property__name', 'status')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'property', 'preferred_move_in_date', 'rental_period_months', 'message', 'status')
        }),
        ('Audit Information', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at',)

admin.site.register(RentApplication, RentApplicationAdmin)

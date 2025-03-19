from backend.models import *
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Registering Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('image')  # Optimize query by selecting related image
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('created_by')  # Optimize query by selecting related user
    
    class Meta:
        verbose_name = _('Amenity')
        verbose_name_plural = _('Amenities')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_usd', 'price_rwf', 'city', 'type', 'capacity', 'created_by', 'created_at', 'updated_at')
    search_fields = ('name', 'city', 'description', 'address')
    list_filter = ('category', 'city', 'type', 'created_at')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('amenities',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('category', 'created_by')  # Optimize query by selecting related models

    class Meta:
        verbose_name = _('Property')
        verbose_name_plural = _('Properties')
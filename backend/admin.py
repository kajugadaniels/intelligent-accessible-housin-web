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
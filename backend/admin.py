from backend.models import *
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Registering Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

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
        return queryset.select_related('created_by')

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

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image', 'created_at')
    search_fields = ('property__name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('property')  # Optimize query by selecting related property
    
    class Meta:
        verbose_name = _('Property Image')
        verbose_name_plural = _('Property Images')

@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'name', 'location', 'staff', 'cleanliness', 'value_for_money', 'comfort', 'facilities', 'free_wifi', 'status', 'created_at')
    search_fields = ('property__name', 'name', 'email', 'comment')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('property')  # Optimize query by selecting related property

    class Meta:
        verbose_name = _('Property Review')
        verbose_name_plural = _('Property Reviews')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'tenant', 'agent', 'property', 'start_date', 'end_date', 'rent_amount', 'payment_status', 'status', 'created_at', 'updated_at')
    search_fields = ('contract_number', 'tenant__name', 'agent__name', 'property__name')
    list_filter = ('status', 'payment_status', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('tenant', 'agent', 'property')  # Optimize query by selecting related models

    class Meta:
        verbose_name = _('Contract')
        verbose_name_plural = _('Contracts')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'phone_number', 'role', 'is_active', 'is_staff', 'created_at', 'updated_at')
    search_fields = ('email', 'name', 'phone_number')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('user_permissions',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('added_by')  # Optimize query by selecting related user (added_by)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
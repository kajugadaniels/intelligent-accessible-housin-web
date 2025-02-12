from backend.models import*
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# ---- User Admin
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone_number')
    ordering = ('-created_at',)
    fields = ('name', 'email', 'phone_number', 'role', 'is_active', 'image', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(User, UserAdmin)


# ---- Amenity Admin
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_by', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Amenity, AmenityAdmin)


# ---- Property Admin
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'type', 'price_rwf', 'city', 'created_by', 'created_at')
    search_fields = ('name', 'category', 'created_by__name', 'city')
    list_filter = ('type', 'category', 'created_by', 'city', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Property, PropertyAdmin)


# ---- PropertyImage Admin
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'created_at')
    list_filter = ('property', 'created_at')
    search_fields = ('property__name',)
    ordering = ('-created_at',)

admin.site.register(PropertyImage, PropertyImageAdmin)


# ---- PropertyReview Admin
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'name', 'location', 'staff', 'cleanliness', 'value_for_money', 'comfort', 'facilities', 'free_wifi', 'status', 'created_at')
    list_filter = ('property', 'status', 'created_at')
    search_fields = ('property__name', 'name', 'email')
    ordering = ('-created_at',)

admin.site.register(PropertyReview, PropertyReviewAdmin)


# ---- Contract Admin
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'tenant', 'agent', 'property', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'tenant', 'agent', 'property', 'created_at')
    search_fields = ('contract_number', 'tenant__name', 'agent__name', 'property__name')
    ordering = ('-created_at',)

    # To make the form user-friendly
    fieldsets = (
        (None, {
            'fields': ('contract_number', 'tenant', 'agent', 'property', 'start_date', 'end_date', 'rental_period_months', 'rent_amount', 'security_deposit')
        }),
        (_('Contract Status'), {
            'fields': ('status', 'payment_status')
        }),
        (_('Dates'), {
            'fields': ('signed_date', 'rent_due_date')
        }),
        (_('Payment Information'), {
            'fields': ('payment_method',)
        }),
        (_('Additional Terms'), {
            'fields': ('additional_terms',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at', 'updated_at',)

admin.site.register(Contract, ContractAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Amenity, Property, PropertyImage, PropertyReview

class CustomUserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'name', 'role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'name', 'phone_number')
    list_filter = ('role', 'is_active', 'is_staff')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name', 'phone_number', 'image', 'role', 'slug')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )

admin.site.register(User, CustomUserAdmin)


class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

admin.site.register(Amenity, AmenityAdmin)


class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'price_usd', 'price_rwf', 'created_by', 'created_at')
    search_fields = ('name', 'description', 'address')
    list_filter = ('created_by', 'amenities')
    ordering = ('-created_at',)

admin.site.register(Property, PropertyAdmin)


class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'created_at')
    list_filter = ('property',)
    ordering = ('-created_at',)

admin.site.register(PropertyImage, PropertyImageAdmin)


class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = (
        'property', 'name', 'location', 'staff', 'cleanliness',
        'value_for_money', 'comfort', 'facilities', 'free_wifi', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at', 'property')
    search_fields = ('property__name', 'name', 'email')
    ordering = ('-created_at',)

admin.site.register(PropertyReview, PropertyReviewAdmin)

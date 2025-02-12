from django.contrib import admin
from frontend.models import RentApplication

class RentApplicationAdmin(admin.ModelAdmin):
    # Display the user's name instead of email
    def user_name(self, obj):
        return obj.user.name

    user_name.admin_order_field = 'user__name'
    user_name.short_description = 'Name'

    list_display = ('user_name', 'property', 'status', 'created_at')
    search_fields = ('user__name',) 
    ordering = ('-created_at',)

admin.site.register(RentApplication, RentApplicationAdmin)

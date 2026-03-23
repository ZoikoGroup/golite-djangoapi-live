from django.contrib import admin
from .models import BusinessContact

@admin.register(BusinessContact)
class BusinessContactAdmin(admin.ModelAdmin):
    list_display  = ("full_name", "business_name", "business_email", "business_needs", "short_message", "created_at")
    search_fields = ("full_name", "business_name", "business_email", "message")
    list_filter   = ("created_at",)
    readonly_fields = ("full_name", "business_name", "business_email", "business_needs", "message", "created_at")
    ordering      = ("-created_at",)

    def short_message(self, obj):
        return obj.message[:40] + "..." if len(obj.message) > 40 else obj.message

    short_message.short_description = "Message"
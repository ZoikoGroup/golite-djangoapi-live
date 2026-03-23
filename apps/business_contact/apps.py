from django.apps import AppConfig


class BusinessContactConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.business_contact"   # ← update name too
    label = "business_contact"
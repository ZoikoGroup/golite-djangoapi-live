from django.urls import path
from .views import business_contact

urlpatterns = [
    path("", business_contact, name="business-contact"),
]
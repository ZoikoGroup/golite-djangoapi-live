from django.urls import path
from .views import (
    VCareOrderCreateAPIView,
    VCareUserGroupedOrdersAPIView
)

urlpatterns = [
    path("create", VCareOrderCreateAPIView.as_view()),
    path("by-user", VCareUserGroupedOrdersAPIView.as_view()),
]

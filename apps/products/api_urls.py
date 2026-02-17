from django.urls import path
from .api_views import (
    ProductListAPIView,
    ProductDetailAPIView,
    CategoryListAPIView,
)
app_name = 'products_api'
urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
]
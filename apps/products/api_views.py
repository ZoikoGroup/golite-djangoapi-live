from rest_framework import generics, filters
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer
from .filters import ProductFilter


# -----------------------------
# Product List
# -----------------------------
class ProductListAPIView(generics.ListAPIView):
    queryset = (
        Product.objects
        .prefetch_related('categories', 'variants', 'images')
        .all()
    )
    serializer_class = ProductSerializer


# -----------------------------
# Product Detail
# -----------------------------
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = (
        Product.objects
        .prefetch_related('categories', 'variants', 'images')
        .all()
    )
    serializer_class = ProductSerializer
    lookup_field = 'slug'


# -----------------------------
# Category List
# -----------------------------
class CategoryListAPIView(generics.ListAPIView):
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer


# -----------------------------
# Product ViewSet (Filter / Search / Ordering)
# -----------------------------
class ProductViewSet(ReadOnlyModelViewSet):
    queryset = (
        Product.objects
        .prefetch_related('categories', 'variants', 'images')
        .all()
    )
    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ['name', 'categories__name']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

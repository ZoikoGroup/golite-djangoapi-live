from rest_framework import serializers
from .models import Product, ProductVariant, ProductImage, ProductCategory


# -----------------------
# Image Serializer
# -----------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image',
            'is_main'
        ]


# -----------------------
# Variant Serializer
# -----------------------
class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'attributes',
            'price',
            'stock'
        ]


# -----------------------
# Category Serializer
# -----------------------
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = [
            'id',
            'name',
            'slug'
        ]


# -----------------------
# Product Serializer
# -----------------------
class ProductSerializer(serializers.ModelSerializer):

    categories = ProductCategorySerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',

            # ✅ Descriptions
            'short_description',
            'description',      # HTML content

            # ✅ Pricing
            'price',
            'sale_price',

            # ✅ SEO
            'seo_title',
            'seo_description',
            'seo_keywords',

            # ✅ Relations
            'categories',
            'variants',
            'images',

            # ✅ Timestamps
            'created_at',
            'updated_at',
        ]

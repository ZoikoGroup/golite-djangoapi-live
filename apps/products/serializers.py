from rest_framework import serializers
from .models import (
    Product,
    ProductAttribute,
    ProductImage,
    ProductCategory,
    ProductVariant
)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['id', 'colour', 'condition', 'storage']

class ProductVariantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id']

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantsSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'slug',
            'category',
            'attributes',
            'images',
            'variants',
            'created_at',
            'updated_at'
        ]

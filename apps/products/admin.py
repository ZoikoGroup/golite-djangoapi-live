from django.contrib import admin
from django import forms
import json

from .models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductCategory
)

# ---------------------------
# Variant Inline Form
# ---------------------------
class ProductVariantInlineForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['attributes', 'price', 'stock']
        widgets = {
            'attributes': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }
        help_texts = {
            'attributes': 'Enter attributes as JSON'
        }

    def clean_attributes(self):
        data = self.cleaned_data.get('attributes')
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format")
        return data


# ---------------------------
# Inlines
# ---------------------------
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    form = ProductVariantInlineForm
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# ---------------------------
# Category Admin
# ---------------------------
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


# ---------------------------
# Product Admin
# ---------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_categories', 'price', 'created_at')
    search_fields = ('name', 'categories__name')
    list_filter = ('categories',)
    filter_horizontal = ('categories',)   # ✅ Multi-select UI
    inlines = [ProductVariantInline, ProductImageInline]
    prepopulated_fields = {'slug': ('name',)}

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])

    get_categories.short_description = "Categories"


# ---------------------------
# Variant Admin
# ---------------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'attributes', 'price', 'stock')
    search_fields = ('product__name',)
    list_filter = ('product',)


# ---------------------------
# Image Admin
# ---------------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'is_main')
    list_filter = ('is_main',)

from django.contrib import admin
from django import forms
from itertools import product as cartesian_product
from .models import (
    Product,
    ProductAttribute,
    ProductImage,
    ProductCategory,
    ProductVariant,
    ProductVariantImage,
)


# ---------------- ATTRIBUTE INLINE FORM (WITH PLACEHOLDERS) ----------------
class ProductAttributeInlineForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ["storage", "colour", "condition"]
        widgets = {
            "storage": forms.TextInput(
                attrs={
                    "placeholder": "Ex: 128gb,256gb,512gb",
                    "style": "width: 250px;"
                }
            ),
            "colour": forms.TextInput(
                attrs={
                    "placeholder": "Ex: black,white",
                    "style": "width: 250px;"
                }
            ),
            "condition": forms.TextInput(
                attrs={
                    "placeholder": "Ex: B1 stock,C1 stock",
                    "style": "width: 250px;"
                }
            ),
        }


# ---------------- ATTRIBUTE INLINE ----------------
class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    form = ProductAttributeInlineForm
    extra = 0
    max_num = 1


# ---------------- PRODUCT IMAGE INLINE ----------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# ---------------- VARIANT INLINE ----------------
class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    can_delete = True
    show_change_link = True


# ---------------- CATEGORY ADMIN ----------------
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    search_fields = ["name"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}


# ---------------- PRODUCT ADMIN ----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
        ProductAttributeInline,
        ProductVariantInline,
    ]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        product = form.instance
        attribute = product.attributes.first()

        if not attribute:
            return

        # Clean and split values
        storages = list(set([s.strip() for s in attribute.storage.split(",") if s.strip()]))
        colours = list(set([c.strip() for c in attribute.colour.split(",") if c.strip()]))
        conditions = list(set([c.strip() for c in attribute.condition.split(",") if c.strip()]))

        if not storages or not colours or not conditions:
            return

        combinations = list(cartesian_product(storages, colours, conditions))

        for storage, colour, condition in combinations:
            ProductVariant.objects.get_or_create(
                product=product,
                storage=storage,
                colour=colour,
                condition=condition,
                defaults={
                    "regular_price": 0,
                    "sale_price": 0,
                    "stock_status": "in_stock",
                    "quantity": 0,
                }
            )


# ---------------- VARIANT IMAGE INLINE ----------------
class ProductVariantImageInline(admin.TabularInline):
    model = ProductVariantImage
    extra = 1


# ---------------- VARIANT ADMIN ----------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["product", "storage", "colour", "condition"]
    search_fields = ["product__name"]
    list_filter = ["product"]
    inlines = [ProductVariantImageInline]


# ---------------- PRODUCT IMAGE ADMIN ----------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "image", "is_main"]
    list_filter = ["is_main"]
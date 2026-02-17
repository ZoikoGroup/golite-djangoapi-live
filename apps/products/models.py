from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import uuid

from django_ckeditor_5.fields import CKEditor5Field


# --------------------------------------------------
# Product Category
# --------------------------------------------------
class ProductCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# --------------------------------------------------
# Product
# --------------------------------------------------
class Product(models.Model):
    categories = models.ManyToManyField(
        ProductCategory,
        related_name="products",
        blank=True
    )

    name = models.CharField(max_length=255)

    # Rich Short Description
    short_description = CKEditor5Field(
        "Short Description",
        config_name="default",
        blank=True,
        null=True
    )

    # Rich Content Description
    description = CKEditor5Field(
        "Description",
        config_name="default",
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=38,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    sale_price = models.DecimalField(
        max_digits=38,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )

    slug = models.SlugField(unique=True, blank=True)

    # ---------------- SEO ----------------
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.CharField(max_length=500, blank=True, null=True)
    seo_keywords = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Comma separated keywords"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:6]}"

        # Auto SEO
        if not self.seo_title:
            self.seo_title = self.name

        if not self.seo_description:
            self.seo_description = (
                self.short_description[:500]
                if self.short_description
                else self.name
            )

        if not self.seo_keywords:
            self.seo_keywords = self.name.replace(" ", ", ")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# --------------------------------------------------
# Product Variant
# --------------------------------------------------
class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="variants",
        on_delete=models.CASCADE
    )

    attributes = models.JSONField()

    price = models.DecimalField(
        max_digits=38,
        decimal_places=10,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.attributes}"


# --------------------------------------------------
# Variant Images
# --------------------------------------------------
class ProductVariantImage(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.ImageField(upload_to="variants/")
    is_main = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductVariantImage.objects.filter(
                variant=self.variant,
                is_main=True
            ).update(is_main=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.variant} Image"


# --------------------------------------------------
# Product Images
# --------------------------------------------------
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(
                product=self.product,
                is_main=True
            ).update(is_main=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} Image"

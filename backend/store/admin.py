from django.contrib import admin
from .models import (
    Category, Product, ProductImage, ProductFeature,
    ProductSpecification, ProductFAQ, ProductReview,
    Order, OrderItem, OrderStatusHistory,
)


# ── Category ──────────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ("id", "name", "slug", "is_active", "created_at")
    list_filter         = ("is_active",)
    search_fields       = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


# ── Product ───────────────────────────────────────────────────────────────────

class ProductImageInline(admin.TabularInline):
    """آپلود چند تصویر مستقیم از صفحه ادمین محصول."""
    model       = ProductImage
    extra       = 1
    fields      = ("image", "alt_text", "order", "is_cover")
    ordering    = ("order",)


class ProductFeatureInline(admin.TabularInline):
    model    = ProductFeature
    extra    = 1
    fields   = ("text", "order")
    ordering = ("order",)


class ProductSpecificationInline(admin.TabularInline):
    model    = ProductSpecification
    extra    = 1
    fields   = ("key", "value", "order")
    ordering = ("order",)


class ProductFAQInline(admin.StackedInline):
    model    = ProductFAQ
    extra    = 0
    fields   = ("question", "answer", "order")
    ordering = ("order",)


class ProductReviewInline(admin.TabularInline):
    model          = ProductReview
    extra          = 0
    fields         = ("user", "rating", "text", "is_approved", "created_at")
    readonly_fields = ("created_at",)
    ordering       = ("-created_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display    = ("id", "name", "slug", "price", "discount_price",
                       "stock", "weight", "is_active", "view_count", "created_at")
    list_filter     = ("is_active", "category")
    search_fields   = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("view_count", "created_at", "updated_at")
    inlines         = [ProductImageInline, ProductFeatureInline, ProductSpecificationInline, ProductFAQInline, ProductReviewInline]
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("category", "name", "slug", "description",
                       "sku", "is_active")
        }),
        ("قیمت و موجودی", {
            "fields": ("price", "discount_price", "stock", "weight")
        }),
        ("تصویر اصلی", {
            "fields": ("image",)
        }),
        ("SEO", {
            "classes": ("collapse",),
            "fields": ("meta_title", "meta_description"),
        }),
        ("آمار", {
            "classes": ("collapse",),
            "fields": ("view_count", "created_at", "updated_at"),
        }),
    )


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    fields          = ("product", "product_name_snapshot", "quantity", "unit_price")
    readonly_fields = ("product", "product_name_snapshot", "quantity", "unit_price")


class OrderStatusHistoryInline(admin.TabularInline):
    model           = OrderStatusHistory
    extra           = 0
    fields          = ("status", "note", "created_by", "created_at")
    readonly_fields = ("status", "note", "created_by", "created_at")
    ordering        = ("-created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ("id", "user", "status", "total_price",
                       "shipping_cost", "tracking_number", "created_at")
    list_filter     = ("status",)
    search_fields   = ("user__phone_number", "tracking_number")
    readonly_fields = ("total_price", "shipping_cost", "created_at",
                       "shipping_address_snapshot")
    inlines         = [OrderItemInline, OrderStatusHistoryInline]

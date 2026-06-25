from django.db import models
from django.conf import settings


# ── Category ──────────────────────────────────────────────────────────────────

class Category(models.Model):
    name        = models.CharField(max_length=128)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    image       = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


# ── Product ───────────────────────────────────────────────────────────────────

class Product(models.Model):
    # PROTECT: اگر دسته‌بندی دارای محصول باشد، حذف آن بلاک می‌شود
    category         = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        null=True, blank=True, related_name="products"
    )
    name             = models.CharField(max_length=256)
    slug             = models.SlugField(unique=True)
    description      = models.TextField(blank=True, default="")
    price            = models.DecimalField(max_digits=12, decimal_places=0)
    discount_price   = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    sku              = models.CharField(max_length=100, blank=True, null=True)
    meta_title       = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    view_count       = models.PositiveIntegerField(default=0)
    stock            = models.PositiveIntegerField(default=0)
    weight           = models.DecimalField(max_digits=8, decimal_places=3, default=0, verbose_name="وزن واقعی (kg)")
    length           = models.DecimalField(max_digits=8, decimal_places=1, default=0, verbose_name="طول (cm)")
    width            = models.DecimalField(max_digits=8, decimal_places=1, default=0, verbose_name="عرض (cm)")
    height           = models.DecimalField(max_digits=8, decimal_places=1, default=0, verbose_name="ارتفاع (cm)")
    image            = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.name

    @property
    def volumetric_weight(self):
        """وزن حجمی = (طول × عرض × ارتفاع) ÷ ۵۰۰۰ — اگر ابعاد ندارد ۰."""
        if self.length and self.width and self.height:
            return float(self.length * self.width * self.height) / 5000.0
        return 0.0

    @property
    def effective_shipping_weight(self):
        """وزن نهایی ارسال = max(وزن واقعی, وزن حجمی)."""
        return max(float(self.weight), self.volumetric_weight)

    @property
    def effective_price(self):
        """قیمت نهایی که مشتری می‌پردازد — اگر تخفیف دارد همان را برمی‌گرداند."""
        return self.discount_price if self.discount_price is not None else self.price


# ── ProductImage ──────────────────────────────────────────────────────────────

class ProductImage(models.Model):
    """گالری تصاویر محصول — هر محصول می‌تواند چندین تصویر داشته باشد."""
    product  = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image    = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    order    = models.PositiveSmallIntegerField(default=0)
    is_cover = models.BooleanField(default=False)

    class Meta:
        ordering        = ["order"]
        verbose_name    = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

    def __str__(self):
        return f"Image#{self.pk} — {self.product.name}"


# ── Product Feature ───────────────────────────────────────────────────────────

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="features")
    text    = models.CharField(max_length=500, verbose_name="متن ویژگی")
    order   = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering        = ["order"]
        verbose_name    = "ویژگی محصول"
        verbose_name_plural = "ویژگی‌های محصول"

    def __str__(self):
        return self.text[:60]


# ── Product Specification ─────────────────────────────────────────────────────

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications")
    key     = models.CharField(max_length=200, verbose_name="عنوان")
    value   = models.CharField(max_length=500, verbose_name="مقدار")
    order   = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering        = ["order"]
        verbose_name    = "مشخصات فنی"
        verbose_name_plural = "مشخصات فنی"

    def __str__(self):
        return f"{self.key}: {self.value}"


# ── Product FAQ ───────────────────────────────────────────────────────────────

class ProductFAQ(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=500, verbose_name="سوال")
    answer   = models.TextField(verbose_name="پاسخ")
    order    = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering        = ["order"]
        verbose_name    = "سوال متداول"
        verbose_name_plural = "سوالات متداول"

    def __str__(self):
        return self.question[:60]


# ── Product Review ────────────────────────────────────────────────────────────

class ProductReview(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating     = models.PositiveSmallIntegerField(default=5, verbose_name="امتیاز (۱ تا ۵)")
    text       = models.TextField(verbose_name="متن نظر")
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering        = ["-created_at"]
        verbose_name    = "نظر کاربر"
        verbose_name_plural = "نظرات کاربران"

    def __str__(self):
        return f"{self.user} — {self.product.name} ({self.rating}★)"


# ── Order ─────────────────────────────────────────────────────────────────────

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending",    "درحال تایید"),
        ("paid",       "تایید شده"),
        ("processing", "آماده سازی"),
        ("shipped",    "تحویل به پست"),
        ("delivered",  "تحویل داده شده"),
        ("cancelled",  "لغو شده"),
    ]

    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    address         = models.ForeignKey(
        "accounts.Address", on_delete=models.PROTECT, related_name="orders"
    )
    shipping_method = models.ForeignKey(
        "shipping.ShippingMethod", on_delete=models.PROTECT, related_name="orders"
    )
    status                   = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_price              = models.DecimalField(max_digits=14, decimal_places=0)
    shipping_cost            = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    tracking_number          = models.CharField(max_length=64, blank=True, default="")
    postal_tracking          = models.CharField(max_length=64, blank=True, default="")
    carrier_name             = models.CharField(max_length=100, blank=True)
    shipped_at               = models.DateTimeField(null=True, blank=True)
    delivered_at             = models.DateTimeField(null=True, blank=True)
    customer_notes           = models.TextField(blank=True)
    shipping_address_snapshot = models.JSONField(null=True, blank=True)
    created_at               = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"Order#{self.pk} — {self.user.phone_number}"

    def save(self, *args, **kwargs):
        """Auto-generate tracking_number after first INSERT only."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Only set tracking_number on the very first save to avoid
        # an extra UPDATE on every subsequent save() call.
        if is_new and not self.tracking_number:
            self.tracking_number = f"ORD-{self.pk:06d}"
            Order.objects.filter(pk=self.pk).update(tracking_number=self.tracking_number)


# ── OrderItem ─────────────────────────────────────────────────────────────────

class OrderItem(models.Model):
    order                = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product              = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_name_snapshot = models.CharField(max_length=256, blank=True)
    quantity             = models.PositiveIntegerField()
    unit_price           = models.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        verbose_name        = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"


# ── OrderStatusHistory ────────────────────────────────────────────────────────

class OrderStatusHistory(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    status     = models.CharField(max_length=30, choices=Order.STATUS_CHOICES)
    note       = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name        = "تاریخچه وضعیت سفارش"
        verbose_name_plural = "تاریخچه وضعیت سفارش‌ها"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.order} -> {self.status}"

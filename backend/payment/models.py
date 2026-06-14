from django.db import models
from store.models import Order


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED  = "failed",  "Failed"

    order            = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="transactions")
    amount           = models.DecimalField(max_digits=14, decimal_places=0)
    provider         = models.CharField(max_length=50, default="zarinpal")
    ref_id           = models.CharField(max_length=128, blank=True, default="")
    status           = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    gateway_response = models.JSONField(default=dict, blank=True)
    callback_token   = models.CharField(max_length=64, blank=True, db_index=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transaction #{self.pk} | Order #{self.order_id} | {self.status}"


class PaymentGatewaySettings(models.Model):
    """
    تنظیمات درگاه پرداخت زرین‌پال — Singleton
    از پنل ادمین قابل مدیریت است.
    """
    MODE_CHOICES = [
        ("sandbox", "حالت سندباکس (پرداخت شبیه‌سازی شده)"),
        ("production", "حالت واقعی (پرداخت واقعی با زرین‌پال)"),
    ]

    zarinpal_merchant_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="کد مرچنت زرین‌پال",
        help_text="کد مرچنت دریافتی از پنل زرین‌پال (برای سندباکس: sandbox)",
        default="sandbox",
    )
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default="sandbox",
        verbose_name="حالت عملیات",
        help_text="در حالت سندباکس، پرداخت واقعی انجام نمی‌شود"
    )
    # تنظیمات پیشرفته
    callback_base_url = models.URLField(
        blank=True,
        verbose_name="آدرس پایه کالبک",
        help_text="آدرس پایه برای بازگشت از درگاه (مثلاً: https://yourdomain.com/api/payment/callback)"
    )
    auto_verify = models.BooleanField(
        default=True,
        verbose_name="تایید خودکار تراکنش",
        help_text="در حالت سندباکس تراکنش‌ها به صورت خودکار تایید می‌شوند"
    )
    # فیلدهای فقط‌خواندنی
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "تنظیمات درگاه پرداخت"
        verbose_name_plural = "تنظیمات درگاه پرداخت"

    def __str__(self):
        mode_display = dict(self.MODE_CHOICES).get(self.mode, self.mode)
        return f"تنظیمات زرین‌پال — {mode_display}"

    @classmethod
    def get(cls):
        """Singleton getter — همیشه ردیف pk=1 را برمی‌گرداند."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def is_sandbox_mode(self) -> bool:
        return self.mode == "sandbox"

    @property
    def is_production_mode(self) -> bool:
        return self.mode == "production"

    def get_merchant_code(self) -> str:
        """برگرداندن کد مرچنت مناسب بر اساس حالت."""
        if self.is_sandbox_mode:
            return "sandbox"
        return self.zarinpal_merchant_code or "sandbox"

    def get_callback_base_url(self) -> str:
        """برگرداندن آدرس کالبک — اولویت با فیلد callback_base_url است."""
        if self.callback_base_url:
            return self.callback_base_url.rstrip("/")
        # فال‌بک به settings
        from django.conf import settings
        return getattr(settings, "PAYMENT_CALLBACK_BASE_URL", "http://127.0.0.1:8000/api/payment/callback")

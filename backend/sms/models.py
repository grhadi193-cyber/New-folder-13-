from django.db import models


class SMSLog(models.Model):
    recipient = models.CharField(max_length=20, verbose_name="شماره گیرنده")
    message = models.TextField(verbose_name="متن پیام")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")
    success = models.BooleanField(default=False, verbose_name="موفق")
    error_message = models.TextField(
        null=True, blank=True, verbose_name="پیام خطا"
    )
    # فیلدهای جدید برای دیباگ
    is_test_mode = models.BooleanField(default=False, verbose_name="حالت تست")
    provider_response = models.TextField(blank=True, default="", verbose_name="پاسخ پرووایدر")

    class Meta:
        verbose_name = "لاگ پیامک"
        verbose_name_plural = "لاگ‌های پیامک"
        ordering = ["-sent_at"]

    def __str__(self):
        status = "✓" if self.success else "✗"
        mode = "[TEST]" if self.is_test_mode else "[REAL]"
        return f"{mode} [{status}] {self.recipient} — {self.sent_at:%Y-%m-%d %H:%M}"


class SMSSettings(models.Model):
    """
    تنظیمات پیامک (Kavenegar) — Singleton
    از پنل ادمین قابل مدیریت است.
    """
    MODE_CHOICES = [
        ("test", "حالت تست (لاگ در دیتابیس + نمایش در کنسول)"),
        ("production", "حالت واقعی (ارسال از طریق Kavenegar)"),
    ]

    kavenegar_api_key = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="API Key کاوه نگار",
        help_text="کلید API دریافتی از پنل Kavenegar"
    )
    sender_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره ارسال‌کننده",
        help_text="شماره خط اختصاصی (مثلاً: 1000596446)"
    )
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default="test",
        verbose_name="حالت عملیات",
        help_text="در حالت تست، پیامک واقعی ارسال نمی‌شود و فقط لاگ می‌شود"
    )
    # تنظیمات OTP
    otp_template_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="قالب OTP (نام الگو در Kavenegar)",
        help_text="نام الگوی OTP ثبت‌شده در پنل Kavenegar (اختیاری)"
    )
    # فیلدهای فقط‌خواندنی
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "تنظیمات پیامک"
        verbose_name_plural = "تنظیمات پیامک"

    def __str__(self):
        mode_display = dict(self.MODE_CHOICES).get(self.mode, self.mode)
        return f"تنظیمات پیامک — {mode_display}"

    @classmethod
    def get(cls):
        """Singleton getter — همیشه ردیف pk=1 را برمی‌گرداند."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def is_test_mode(self) -> bool:
        return self.mode == "test"

    @property
    def is_production_mode(self) -> bool:
        return self.mode == "production"

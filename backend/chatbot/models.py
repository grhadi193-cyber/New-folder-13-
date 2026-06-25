import json
from django.db import models


class ChatbotConfig(models.Model):
    api_key = models.CharField(
        max_length=256, blank=True, default="",
        verbose_name="کلید API Mimo",
        help_text="کلید API پلتفرم میمو (Mimo Platform)",
    )
    api_base_url = models.URLField(
        default="https://api.xiaomimimo.com/v1",
        verbose_name="آدرس پایه API",
        help_text="آدرس پایه API میمو — بدون /chat/completions",
    )
    model = models.CharField(
        max_length=100, default="mimo-v2.5-pro",
        verbose_name="مدل",
        help_text="شناسه مدل Mimo (مثلاً mimo-v2.5-pro یا mimo-v2-flash)",
    )
    temperature = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.7,
        verbose_name="دما (Temperature)",
    )
    max_tokens = models.PositiveIntegerField(
        default=1024,
        verbose_name="حداکثر توکن",
    )
    welcome_message = models.TextField(
        default="سلام! 👋 من دستیار فروش آتی فرزام هستم. چطور می‌تونم کمکتون کنم؟",
        verbose_name="پیام خوش‌آمدگویی",
    )
    quick_replies = models.JSONField(
        default=list,
        blank=True,
        verbose_name="پاسخ‌های سریع",
        help_text='لیست دکمه‌ها — مثال: ["مشاهده محصولات", "راهنمای خرید", "تماس با پشتیبانی"]',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="چت‌بات فعال",
    )
    last_prompt_update = models.DateTimeField(
        null=True, blank=True,
        verbose_name="آخرین بروزرسانی پرامپت",
    )
    cached_prompt = models.TextField(
        blank=True, default="",
        verbose_name="پرامپت کش‌شده",
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات چت‌بات"
        verbose_name_plural = "تنظیمات چت‌بات"

    def __str__(self):
        return "تنظیمات چت‌بات"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_quick_replies_list(self):
        if isinstance(self.quick_replies, str):
            try:
                return json.loads(self.quick_replies)
            except (json.JSONDecodeError, TypeError):
                return []
        return self.quick_replies if isinstance(self.quick_replies, list) else []


class ChatSession(models.Model):
    session_key = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="chat_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "جلسه گفتگو"
        verbose_name_plural = "جلسات گفتگو"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Chat {self.session_key[:12]}…"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "کاربر"),
        ("assistant", "دستیار"),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "پیام چت"
        verbose_name_plural = "پیام‌های چت"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}…"

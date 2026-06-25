from django.db import models


class SiteSettings(models.Model):
    site_name        = models.CharField(max_length=200, default="فروشگاه من")
    logo             = models.ImageField(upload_to="site/", null=True, blank=True)
    banner_text      = models.CharField(max_length=500, blank=True)
    announcement     = models.TextField(blank=True)
    primary_color    = models.CharField(max_length=7, default="#01696f")
    maintenance_mode = models.BooleanField(default=False)
    shop_enabled     = models.BooleanField(default=True, verbose_name="فروشگاه فعال")
    max_order_quantity = models.PositiveIntegerField(default=20, verbose_name="حداکثر تعداد محصول در هر سفارش")
    otp_test_mode    = models.BooleanField(default=False, verbose_name="حالت تست پیامک (نمایش کد در فرانت)")
    social_instagram = models.URLField(blank=True)
    social_telegram  = models.URLField(blank=True)
    support_phone    = models.CharField(max_length=20, blank=True)

    hero_title  = models.CharField(max_length=200, blank=True, default="Welcome to our store")
    hero_text   = models.TextField(blank=True, default="Best products at best prices.")
    hero_banner = models.ImageField(upload_to="banners/", null=True, blank=True)
    hero_bg_image = models.ImageField(upload_to="site/hero/", null=True, blank=True)
    about_us    = models.TextField(blank=True)

    # ── فیلدهای اضافی برای جایگزینی PocketBase ──────────────────────────
    support_email     = models.EmailField(blank=True, default="info@atifarzam.ir")
    address           = models.CharField(max_length=500, blank=True, default="تهران، ایران")
    work_hours        = models.CharField(max_length=200, blank=True, default="شنبه تا چهارشنبه — ۸ تا ۱۷")
    google_play_url   = models.URLField(blank=True)
    app_store_url     = models.URLField(blank=True)
    software_login_url = models.URLField(blank=True)
    software_description = models.TextField(blank=True)

    about_image         = models.ImageField(upload_to="site/about/", null=True, blank=True)
    software_image      = models.ImageField(upload_to="site/software/", null=True, blank=True)
    app_image           = models.ImageField(upload_to="site/app/", null=True, blank=True)
    why_us_icon_1       = models.ImageField(upload_to="site/why_us/", null=True, blank=True)
    why_us_icon_2       = models.ImageField(upload_to="site/why_us/", null=True, blank=True)
    why_us_icon_3       = models.ImageField(upload_to="site/why_us/", null=True, blank=True)
    category_image_1    = models.ImageField(upload_to="site/categories/", null=True, blank=True)
    category_image_2    = models.ImageField(upload_to="site/categories/", null=True, blank=True)
    category_image_3    = models.ImageField(upload_to="site/categories/", null=True, blank=True)
    category_image_4    = models.ImageField(upload_to="site/categories/", null=True, blank=True)
    testimonial_bg      = models.ImageField(upload_to="site/testimonials/", null=True, blank=True)
    newsletter_bg       = models.ImageField(upload_to="site/newsletter/", null=True, blank=True)

    class Meta:
        verbose_name        = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return "تنظیمات اصلی سایت"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Banner(models.Model):
    title       = models.CharField(max_length=200)
    subtitle    = models.CharField(max_length=500, blank=True)
    image       = models.ImageField(upload_to="banners/")
    link        = models.URLField(blank=True)
    cta_text    = models.CharField(max_length=100, blank=True, default="مشاهده")
    cta_link    = models.URLField(blank=True)
    cta2_text   = models.CharField(max_length=100, blank=True)
    cta2_link   = models.URLField(blank=True)
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "بنر"
        verbose_name_plural = "بنرها"
        ordering            = ["order", "-created_at"]

    def __str__(self):
        return self.title


class Partner(models.Model):
    name       = models.CharField(max_length=200)
    logo       = models.ImageField(upload_to="partners/")
    website    = models.URLField(blank=True)
    order      = models.PositiveSmallIntegerField(default=0)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "شریک"
        verbose_name_plural = "شرکا"
        ordering            = ["order", "-created_at"]

    def __str__(self):
        return self.name


class Page(models.Model):
    title      = models.CharField(max_length=200)
    slug       = models.SlugField(unique=True, allow_unicode=True)
    content    = models.TextField(blank=True)
    is_active  = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "صفحه"
        verbose_name_plural = "صفحات"
        ordering            = ["-created_at"]

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name       = models.CharField(max_length=128, verbose_name="نام")
    phone      = models.CharField(max_length=15, verbose_name="شماره موبایل")
    message    = models.TextField(verbose_name="پیام")
    is_read    = models.BooleanField(default=False, verbose_name="خوانده شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name        = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.phone}"

from django.contrib import admin

from core.models import SiteSettings, Banner, Partner, Page, ContactMessage


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("هویت سایت", {
            "fields": ("site_name", "logo", "primary_color"),
        }),
        ("محتوای صفحه اصلی", {
            "fields": ("banner_text", "announcement", "hero_title", "hero_text", "hero_banner", "hero_bg_image", "about_us"),
        }),
        ("تصاویر بخش‌های سایت", {
            "fields": (
                "about_image", "software_image", "app_image",
                "why_us_icon_1", "why_us_icon_2", "why_us_icon_3",
                "category_image_1", "category_image_2", "category_image_3", "category_image_4",
                "testimonial_bg", "newsletter_bg",
            ),
        }),
        ("شبکه‌های اجتماعی و پشتیبانی", {
            "fields": ("social_instagram", "social_telegram", "support_phone", "support_email", "address", "work_hours"),
        }),
        ("نرم‌افزار و اپلیکیشن", {
            "fields": ("software_login_url", "software_description", "google_play_url", "app_store_url"),
        }),
        ("وضعیت سایت", {
            "fields": ("maintenance_mode", "shop_enabled"),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display  = ("title", "order", "is_active", "created_at")
    list_filter   = ("is_active",)
    list_editable = ("order", "is_active")
    fieldsets = (
        (None, {
            "fields": ("title", "subtitle", "image", "link", "order", "is_active"),
        }),
        ("دکمه‌ها", {
            "fields": ("cta_text", "cta_link", "cta2_text", "cta2_link"),
        }),
    )


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display  = ("name", "order", "is_active", "created_at")
    list_filter   = ("is_active",)
    list_editable = ("order", "is_active")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display  = ("title", "slug", "is_active", "updated_at")
    list_filter   = ("is_active",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ("name", "phone", "is_read", "created_at")
    list_filter   = ("is_read",)
    list_editable = ("is_read",)
    readonly_fields = ("name", "phone", "message", "created_at")
    search_fields = ("name", "phone", "message")

    def has_add_permission(self, request):
        return False

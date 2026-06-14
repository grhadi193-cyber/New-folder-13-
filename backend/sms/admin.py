from django.contrib import admin

from sms.models import SMSLog, SMSSettings


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ("recipient", "is_test_mode", "success", "sent_at", "short_message")
    list_filter = ("is_test_mode", "success", "sent_at")
    search_fields = ("recipient", "message", "error_message", "provider_response")
    readonly_fields = ("recipient", "message", "sent_at", "success", "error_message", "is_test_mode", "provider_response")
    ordering = ("-sent_at",)

    def short_message(self, obj: SMSLog) -> str:
        return obj.message[:60] + ("…" if len(obj.message) > 60 else "")

    short_message.short_description = "پیام"

    def has_add_permission(self, request):  # noqa: ANN001
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ANN001
        return False


@admin.register(SMSSettings)
class SMSSettingsAdmin(admin.ModelAdmin):
    """
    SMSSettings singleton — در پنل ادمین Django قابل ویرایش.
    """
    fieldsets = (
        ("حالت عملیات", {
            "fields": ("mode",),
            "description": "در حالت تست، پیامک واقعی ارسال نمی‌شود و فقط در بخش لاگ‌های پیامک قابل مشاهده است."
        }),
        ("تنظیمات کاوه نگار", {
            "fields": ("kavenegar_api_key", "sender_number", "otp_template_name"),
            "description": "این تنظیمات فقط در حالت واقعی (Production) استفاده می‌شوند."
        }),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SMSSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

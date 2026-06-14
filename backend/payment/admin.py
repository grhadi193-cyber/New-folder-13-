from django.contrib import admin
from .models import Transaction, PaymentGatewaySettings


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ("id", "order", "amount", "status", "ref_id", "created_at")
    list_filter   = ("status",)
    search_fields = ("ref_id", "order__id")
    readonly_fields = ("created_at", "gateway_response")


@admin.register(PaymentGatewaySettings)
class PaymentGatewaySettingsAdmin(admin.ModelAdmin):
    """
    PaymentGatewaySettings singleton — در پنل ادمین Django قابل ویرایش.
    """
    fieldsets = (
        ("حالت عملیات", {
            "fields": ("mode", "auto_verify"),
            "description": "در حالت سندباکس، پرداخت واقعی انجام نمی‌شود و تراکنش‌ها به صورت خودکار تایید می‌شوند."
        }),
        ("تنظیمات زرین‌پال", {
            "fields": ("zarinpal_merchant_code", "callback_base_url"),
            "description": "کد مرچنت در حالت سندباکس نیاز نیست. آدرس کالبک را با https وارد کنید."
        }),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not PaymentGatewaySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

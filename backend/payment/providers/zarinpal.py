import logging
from decimal import Decimal
from django.conf import settings
from .base import BasePaymentProvider

logger = logging.getLogger(__name__)

class ZarinpalProvider(BasePaymentProvider):
    @property
    def name(self) -> str:
        return "zarinpal"

    def _get_gateway_settings(self):
        """Get PaymentGatewaySettings singleton."""
        from payment.models import PaymentGatewaySettings
        return PaymentGatewaySettings.get()

    def _get_merchant_code(self) -> str:
        """Get merchant code from admin settings or fall back to env."""
        try:
            gateway_settings = self._get_gateway_settings()
            return gateway_settings.get_merchant_code()
        except Exception:
            # Fall back to env settings
            return getattr(settings, "ZARINPAL_MERCHANT_CODE", "sandbox")

    def _get_callback_url(self) -> str:
        """Get callback URL from admin settings or fall back to env."""
        try:
            gateway_settings = self._get_gateway_settings()
            return gateway_settings.get_callback_base_url()
        except Exception:
            # Fall back to env settings
            return getattr(
                settings, "PAYMENT_CALLBACK_BASE_URL",
                "http://127.0.0.1:8000/api/payment/callback"
            ).rstrip("/")

    def initiate(self, transaction, callback_url: str = None) -> str:
        from azbankgateways import bankfactories, models as bank_models
        factory = bankfactories.BankFactory()
        bank = factory.create(bank_type=bank_models.BankType.ZARINPAL)

        amount = Decimal(str(transaction.amount))
        bank.set_amount(int(amount) * 10)
        bank.set_mobile_number(transaction.order.user.phone_number)

        # استفاده از callback_url پاس‌شده از orchestrator (شامل token امنیتی)
        if not callback_url:
            callback_url = self._get_callback_url()
        bank.set_client_callback_url(callback_url)
        bank.set_order_id(str(transaction.order.pk))

        # تنظیم کد مرچنت از ادمین
        merchant_code = self._get_merchant_code()
        # توجه: az-iranian-bank-gateways مرچنت رو از settings می‌خونه
        # پس برای تغییر داینامیک، از محیط استفاده می‌کنیم
        import os
        os.environ["ZARINPAL_MERCHANT_CODE"] = merchant_code

        redirect_url = bank.redirect_gateway_url()
        transaction.ref_id = bank.get_transaction_id() or ""
        transaction.gateway_response = {
            "gateway_token": transaction.ref_id,
            "merchant_code": merchant_code[:8] + "..." if len(merchant_code) > 8 else merchant_code,
        }

        return redirect_url

    def verify(self, transaction, raw_params: dict) -> bool:
        from azbankgateways import bankfactories, models as bank_models
        factory = bankfactories.BankFactory()
        bank = factory.create(bank_type=bank_models.BankType.ZARINPAL)

        # تنظیم کد مرچنت از ادمین
        merchant_code = self._get_merchant_code()
        import os
        os.environ["ZARINPAL_MERCHANT_CODE"] = merchant_code

        bank.set_gateway_callback_parameters(raw_params, bank_models.BankType.ZARINPAL)
        bank.verify_from_gateway(request=None)

        tracking_code = bank.get_tracking_code()
        success = bank.is_success()

        transaction.ref_id = str(tracking_code or "")
        transaction.gateway_response = {
            **transaction.gateway_response,
            "tracking_code": tracking_code,
            "verify_params": raw_params,
        }

        return success

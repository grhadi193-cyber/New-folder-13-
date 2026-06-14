import logging
from .base import BasePaymentProvider

logger = logging.getLogger(__name__)

class MockProvider(BasePaymentProvider):
    @property
    def name(self) -> str:
        return "mock"

    def initiate(self, transaction, callback_url: str = None) -> str:
        transaction_id = transaction.pk

        # اگر callback_url از orchestrator پاس شده، از همان استفاده کن
        if not callback_url:
            from payment.models import PaymentGatewaySettings
            try:
                gateway_settings = PaymentGatewaySettings.get()
                base_url = gateway_settings.get_callback_base_url()
            except Exception:
                base_url = "http://127.0.0.1:8000/api/payment/callback"
            callback_url = f"{base_url}?transaction_id={transaction_id}"

        # Authority با پیشوند SANDBOX_ برای شناسایی sandbox در callback
        fake_url = f"{callback_url}&Authority=SANDBOX_{transaction_id}&Status=OK"

        transaction.gateway_response = {
            "debug": True,
            "fake_url": fake_url,
            "sandbox": True,
            "note": "این یک پرداخت سندباکس است. برای فعال‌سازی پرداخت واقعی، حالت را در تنظیمات ادمین به 'حالت واقعی' تغییر دهید."
        }
        logger.info(f"[MockProvider] Sandbox payment for order #{transaction.order.pk}, transaction #{transaction_id}")
        logger.info(f"[MockProvider] Fake callback URL: {fake_url}")
        return fake_url

    def verify(self, transaction, raw_params: dict) -> bool:
        authority = raw_params.get("Authority", "")
        status = raw_params.get("Status", "")
        success = authority.startswith("SANDBOX_") and status == "OK"

        transaction.ref_id = authority
        transaction.gateway_response = {
            **transaction.gateway_response,
            "verify_params": raw_params,
            "debug": True,
            "sandbox_verified": True,
        }

        if success:
            logger.info(f"[MockProvider] Sandbox payment verified for transaction #{transaction.pk}")
        else:
            logger.warning(f"[MockProvider] Sandbox payment failed for transaction #{transaction.pk}: status={status}")

        return success

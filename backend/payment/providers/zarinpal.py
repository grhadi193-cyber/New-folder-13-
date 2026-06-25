import logging
from decimal import Decimal
from .base import BasePaymentProvider

logger = logging.getLogger(__name__)


class ZarinpalProvider(BasePaymentProvider):
    @property
    def name(self) -> str:
        return "zarinpal"

    def _get_gateway_settings(self):
        from payment.models import PaymentGatewaySettings
        return PaymentGatewaySettings.get()

    def _get_merchant_code(self) -> str:
        try:
            return self._get_gateway_settings().get_merchant_code()
        except Exception:
            from django.conf import settings
            return getattr(settings, "ZARINPAL_MERCHANT_CODE", "sandbox")

    def initiate(self, transaction, callback_url: str = None) -> str:
        from azbankgateways.bankfactories import BankFactory
        from azbankgateways.models import BankType

        import os
        os.environ["ZARINPAL_MERCHANT_CODE"] = self._get_merchant_code()

        factory = BankFactory()
        bank = factory.create(bank_type=BankType.ZARINPAL)

        amount = Decimal(str(transaction.amount))
        bank.set_amount(int(amount))
        bank.set_mobile_number(transaction.order.user.phone_number)

        if not callback_url:
            from payment.models import PaymentGatewaySettings
            try:
                callback_url = PaymentGatewaySettings.get().get_callback_base_url()
            except Exception:
                from django.conf import settings
                callback_url = getattr(
                    settings, "PAYMENT_CALLBACK_BASE_URL",
                    "http://127.0.0.1:8000/api/payment/callback"
                )

        bank.set_client_callback_url(callback_url)

        bank_record = bank.ready()
        authority = bank.get_reference_number()

        transaction.ref_id = authority or ""
        transaction.gateway_response = {
            "gateway_token": authority,
            "tracking_code": bank_record.tracking_code,
            "bank_record_id": bank_record.pk,
        }
        logger.info(
            "[ZarinpalProvider] Payment initiated: order=#%s, authority=%s, tracking=%s",
            transaction.order.pk, authority, bank_record.tracking_code,
        )

        startpay_url = bank._startpay_url + authority
        return startpay_url

    def verify(self, transaction, raw_params: dict) -> bool:
        from azbankgateways.models import Bank

        tracking_code = raw_params.get("tc", "")
        if not tracking_code:
            logger.warning("[ZarinpalProvider] No tracking code in callback params")
            return False

        try:
            bank_record = Bank.objects.get(tracking_code=tracking_code)
        except Bank.DoesNotExist:
            logger.error("[ZarinpalProvider] Bank record not found for tracking_code=%s", tracking_code)
            return False

        success = bank_record.is_success
        transaction.ref_id = bank_record.reference_number or ""
        transaction.gateway_response = {
            **transaction.gateway_response,
            "tracking_code": tracking_code,
            "bank_status": bank_record.status,
            "verify_params": raw_params,
        }

        if success:
            logger.info("[ZarinpalProvider] Payment verified: tracking=%s, ref=%s", tracking_code, bank_record.reference_number)
        else:
            logger.warning("[ZarinpalProvider] Payment not successful: tracking=%s, status=%s", tracking_code, bank_record.status)

        return success

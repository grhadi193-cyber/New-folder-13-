import secrets
import logging
from decimal import Decimal
from django.conf import settings
from django.db import transaction as db_transaction

from store.models import Order
from sms.services import send_order_success_sms
from .models import Transaction, PaymentGatewaySettings
from .providers import MockProvider, ZarinpalProvider

logger = logging.getLogger(__name__)


def get_provider(name: str):
    """
    Get payment provider based on current settings (from Django Admin).
    Returns MockProvider in sandbox mode, ZarinpalProvider in production or zarinpal_sandbox.
    """
    try:
        gateway_settings = PaymentGatewaySettings.get()
        if gateway_settings.is_sandbox_mode:
            return MockProvider()
        # zarinpal_sandbox and production both use the real ZarinpalProvider
    except Exception:
        # If table doesn't exist yet (first migration), fall back to settings.DEBUG
        if getattr(settings, "DEBUG", True):
            return MockProvider()

    return ZarinpalProvider()


def start_payment(order: Order, provider_name: str = "zarinpal") -> tuple[str, int]:
    provider = get_provider(provider_name)

    amount = Decimal(str(order.total_price))

    # یک token یک‌بارمصرف تصادفی برای تأیید کالبک
    token = secrets.token_urlsafe(32)

    txn = Transaction.objects.create(
        order=order,
        amount=amount,
        status=Transaction.Status.PENDING,
        provider=provider.name,
        callback_token=token,
    )

    try:
        # callback_url با token embed‌شده به provider داده می‌شود
        base_callback_url = _build_base_callback_url(order)
        callback_url = f"{base_callback_url}?transaction_id={txn.id}&cb_token={token}"

        payment_url = provider.initiate(txn, callback_url=callback_url)
        txn.save(update_fields=["ref_id", "gateway_response"])
        return payment_url, txn.pk
    except Exception as exc:
        txn.status = Transaction.Status.FAILED
        txn.gateway_response = {"error": str(exc)}
        txn.save(update_fields=["status", "gateway_response"])
        logger.exception(f"[Payment] Gateway initiation failed for order #{order.pk}")
        raise


def _build_base_callback_url(order: Order) -> str:
    """
    آدرس پایه کالبک را از PaymentGatewaySettings می‌خواند.
    اولویت: تنظیمات ادمین > PAYMENT_CALLBACK_BASE_URL در settings > localhost
    """
    try:
        gateway_settings = PaymentGatewaySettings.get()
        return gateway_settings.get_callback_base_url()
    except Exception:
        base = getattr(settings, "PAYMENT_CALLBACK_BASE_URL", "http://127.0.0.1:8000/api/payment/callback")
        return base.rstrip("/")


def verify_payment(transaction_id: int, raw_params: dict) -> bool:
    try:
        with db_transaction.atomic():
            txn = Transaction.objects.select_for_update().get(pk=transaction_id)
    except Transaction.DoesNotExist:
        logger.error(f"[Payment] verify() called with unknown transaction_id={transaction_id}")
        return False

    if txn.status == Transaction.Status.SUCCESS:
        return True
    if txn.status == Transaction.Status.FAILED:
        return False

    # در حالت سندباکس (MockProvider) با auto_verify=True، تراکنش خودکار تایید شود
    # zarinpal_sandbox از اینجا رد می‌شه چون تأیید واقعی از طریق زرین‌پال انجام می‌شه
    try:
        gateway_settings = PaymentGatewaySettings.get()
        if gateway_settings.is_sandbox_mode and gateway_settings.auto_verify:
            logger.info("[Payment] Auto-verifying sandbox transaction #%s", transaction_id)
            with db_transaction.atomic():
                txn.status = Transaction.Status.SUCCESS
                txn.ref_id = raw_params.get("Authority", f"SANDBOX_{transaction_id}")
                txn.gateway_response = {**txn.gateway_response, "auto_verify": True, "verify_params": raw_params}
                txn.save(update_fields=["status", "ref_id", "gateway_response"])
                _mark_order_paid(txn)
            return True
    except Exception:
        pass  # If settings table doesn't exist, proceed normally

    provider = get_provider(txn.provider)

    try:
        with db_transaction.atomic():
            success = provider.verify(txn, raw_params)
            txn.status = Transaction.Status.SUCCESS if success else Transaction.Status.FAILED
            txn.save(update_fields=["status", "ref_id", "gateway_response"])

            if success:
                _mark_order_paid(txn)
        return success
    except Exception as exc:
        txn.status = Transaction.Status.FAILED
        txn.gateway_response = {**txn.gateway_response, "verify_error": str(exc)}
        txn.save(update_fields=["status", "gateway_response"])
        logger.exception(f"[Payment] Gateway verify failed for transaction #{transaction_id}")
        return False


def _mark_order_paid(txn: Transaction) -> None:
    order = Order.objects.select_for_update().get(pk=txn.order_id)
    order.status = "paid"
    order.save(update_fields=["status"])

    # اطلاع‌رسانی پرداخت موفق
    try:
        from notifications.services import send_notification
        send_notification(
            event_type="order_paid",
            user=order.user,
            order=order,
            use_queue=True,
        )
    except Exception as notif_exc:
        logger.error(f"[Payment] Notification failed after payment for order #{order.pk}: {notif_exc}")

    # همچنان SMS قدیمی هم ارسال شود (backward compatible)
    try:
        send_order_success_sms(phone_number=order.user.phone_number, order_id=order.pk)
    except Exception as sms_exc:
        logger.error(f"[Payment] SMS failed after payment for order #{order.pk}: {sms_exc}")

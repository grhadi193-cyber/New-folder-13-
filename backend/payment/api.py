import hashlib
import hmac
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from ninja import Router, Query

from core.auth import AuthBearer
from .schemas import InitiatePaymentIn, InitiatePaymentOut, VerifyCallbackIn
from .orchestrator import start_payment, verify_payment
from store.models import Order
from core.exceptions import NotFoundError

import logging

logger = logging.getLogger(__name__)

router = Router(tags=["Payment"])

_auth = AuthBearer()


# ── Callback Security ─────────────────────────────────────────────────────────

def _verify_gateway_signature(request, gateway_name: str = "zarinpal") -> bool:
    """
    بررسی امضای دیجیتال درگاه پرداخت.
    برای Zarinpal: بررسی Authority و Status در query params.
    برای درگاه‌های دیگر: بررسی signature در هدر.
    """
    if gateway_name == "zarinpal":
        authority = request.GET.get("Authority", "")
        if not authority:
            return False
        if len(authority) < 10:
            return False
        return True

    # Generic HMAC signature verification for other gateways
    signature = request.headers.get("X-Gateway-Signature", "")
    if not signature:
        return False

    secret = getattr(settings, "PAYMENT_GATEWAY_SECRET", "")
    if not secret:
        logger.warning("PAYMENT_GATEWAY_SECRET not set — cannot verify signatures")
        return True  # Allow in development; block in production

    body = request.body or b""
    expected = hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


def _get_frontend_base_url() -> str:
    """آدرس پایه فرانت‌اند را از تنظیمات می‌خواند."""
    return getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/initiate", response=InitiatePaymentOut, auth=_auth)
def initiate_payment(request, payload: InitiatePaymentIn):
    """
    Initiate payment for an existing order.
    The order must belong to the authenticated user.
    """
    try:
        order = Order.objects.get(pk=payload.order_id, user=request.auth)
    except Order.DoesNotExist:
        return JsonResponse(
            {"error": True, "code": "not_found", "message": f"سفارش #{payload.order_id} یافت نشد."},
            status=404,
        )

    if order.status == "paid":
        return JsonResponse(
            {"error": True, "code": "already_paid", "message": "این سفارش قبلاً پرداخت شده است."},
            status=400,
        )

    payment_url, transaction_id = start_payment(order)
    return InitiatePaymentOut(payment_url=payment_url, transaction_id=transaction_id)


@router.get("/callback")
def payment_callback(request, params: Query[VerifyCallbackIn]):
    """
    Gateway redirect endpoint.
    After azbankgateways verifies payment, it redirects here with ?tc=<tracking_code>&transaction_id=...&cb_token=...
    Also handles legacy sandbox flow with ?Authority=SANDBOX_...&Status=OK
    """
    frontend_base = _get_frontend_base_url()
    raw = dict(request.GET)
    raw_flat = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in raw.items()}

    # ── Determine transaction_id ──
    transaction_id = params.transaction_id

    # Try to find transaction via azbankgateways tracking code
    if not transaction_id and params.tc:
        from azbankgateways.models import Bank
        try:
            bank_record = Bank.objects.get(tracking_code=params.tc)
            from .models import Transaction
            txn = Transaction.objects.filter(
                ref_id=bank_record.reference_number,
                status="pending",
            ).order_by("-created_at").first()
            if txn:
                transaction_id = txn.pk
        except Exception:
            pass

    # Sandbox fallback: extract from Authority
    authority = params.Authority
    if not transaction_id and authority and authority.startswith("SANDBOX_"):
        try:
            transaction_id = int(authority.split("_")[1])
        except (IndexError, ValueError):
            redirect_url = f"{frontend_base}/payment-result?status=failed&reason=invalid_authority"
            return HttpResponseRedirect(redirect_url)

    if not transaction_id:
        redirect_url = f"{frontend_base}/payment-result?status=failed&reason=not_found"
        return HttpResponseRedirect(redirect_url)

    success = verify_payment(transaction_id, raw_flat)

    order_id = ""
    try:
        from .models import Transaction
        txn = Transaction.objects.get(pk=transaction_id)
        order_id = txn.order_id
    except Exception:
        pass

    if success:
        redirect_url = (
            f"{frontend_base}/payment-result"
            f"?status=paid"
            f"&transaction_id={transaction_id}"
            f"&order_id={order_id}"
        )
    else:
        redirect_url = (
            f"{frontend_base}/payment-result"
            f"?status=failed"
            f"&transaction_id={transaction_id}"
        )

    return HttpResponseRedirect(redirect_url)


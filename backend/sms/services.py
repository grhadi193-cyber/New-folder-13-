"""
SMS Service Layer.
SMSLog fields: recipient, message, success, error_message, sent_at, is_test_mode, provider_response
- Test Mode: print to console + write SMSLog, never call Kavenegar
- Production: call Kavenegar + write SMSLog
- Mode is controlled from Django Admin (SMSSettings)
- No public API. Called explicitly from other services (no signals).
"""

import logging
from django.conf import settings
from .models import SMSLog, SMSSettings

logger = logging.getLogger(__name__)


def _get_settings() -> SMSSettings:
    """Get SMS settings singleton."""
    return SMSSettings.get()


def _send(phone_number: str, message: str, sms_type: str) -> None:
    sms_settings = _get_settings()

    if sms_settings.is_test_mode:
        # حالت تست — فقط لاگ و چاپ در کنسول
        print(f"[SMS][TEST MODE] To={phone_number} Type={sms_type}: {message}")
        logger.info("[SMS][TEST] %s to %s: %s", sms_type, phone_number, message)
        SMSLog.objects.create(
            recipient=phone_number,
            message=message,
            success=True,
            is_test_mode=True,
            provider_response="[TEST MODE] پیامک واقعی ارسال نشد.",
        )
        return

    # Production — Kavenegar
    api_key = sms_settings.kavenegar_api_key or getattr(settings, "KAVENEGAR_API_KEY", "")
    sender = sms_settings.sender_number or getattr(settings, "SMS_SENDER", "")

    if not api_key:
        logger.error("[SMS] Kavenegar API Key is not set! Message not sent.")
        SMSLog.objects.create(
            recipient=phone_number,
            message=message,
            success=False,
            is_test_mode=False,
            error_message="Kavenegar API Key تنظیم نشده است.",
        )
        raise RuntimeError("Kavenegar API Key is not configured.")

    try:
        from kavenegar import KavenegarAPI
        api = KavenegarAPI(api_key)
        params = {"receptor": phone_number, "message": message}
        if sender:
            params["sender"] = sender
        response = api.sms_send(params)
        response_str = str(response) if response else "OK"
        SMSLog.objects.create(
            recipient=phone_number,
            message=message,
            success=True,
            is_test_mode=False,
            provider_response=response_str[:500],
        )
        logger.info("[SMS] Sent %s to %s via Kavenegar", sms_type, phone_number)
    except Exception as exc:
        SMSLog.objects.create(
            recipient=phone_number,
            message=message,
            success=False,
            is_test_mode=False,
            error_message=str(exc)[:500],
        )
        logger.exception("[SMS] Failed to send %s to %s: %s", sms_type, phone_number, exc)
        raise


def send_otp(phone_number: str, code: str) -> None:
    """
    Send OTP code via SMS.
    In test mode: logs to database, visible in Django Admin SMSLog.
    In production: sends via Kavenegar.
    """
    sms_settings = _get_settings()

    # اگر قالب OTP در Kavenegar تعریف شده باشد
    if sms_settings.is_production_mode and sms_settings.otp_template_name:
        _send_otp_template(phone_number, code, sms_settings)
    else:
        _send(phone_number, f"کد تأیید شما: {code}", sms_type="OTP")


def _send_otp_template(phone_number: str, code: str, sms_settings: SMSSettings) -> None:
    """Send OTP using Kavenegar template (lookups)."""
    try:
        from kavenegar import KavenegarAPI
        api = KavenegarAPI(sms_settings.kavenegar_api_key)
        params = {
            "receptor": phone_number,
            "template": sms_settings.otp_template_name,
            "token": code,
        }
        if sms_settings.sender_number:
            params["sender"] = sms_settings.sender_number
        response = api.verify_lookup(params)
        response_str = str(response) if response else "OK"
        SMSLog.objects.create(
            recipient=phone_number,
            message=f"OTP via template '{sms_settings.otp_template_name}': {code}",
            success=True,
            is_test_mode=False,
            provider_response=response_str[:500],
        )
        logger.info("[SMS] OTP sent via template to %s", phone_number)
    except Exception as exc:
        # فال‌بک به ارسال معمولی
        logger.warning("[SMS] Template send failed, falling back to normal SMS: %s", exc)
        _send(phone_number, f"کد تأیید شما: {code}", sms_type="OTP")


def send_order_success_sms(phone_number: str, order_id: int) -> None:
    """Called explicitly from payment.services after successful payment."""
    _send(
        phone_number,
        f"سفارش شماره {order_id} شما با موفقیت ثبت و پرداخت شد. ممنون از خریدتان.",
        sms_type="ORDER_SUCCESS",
    )


def send_raw_sms(phone_number: str, message: str) -> None:
    """
    ارسال پیامک سفارشی.
    برای استفاده در پنل ادمین یا ارسال‌های دستی.
    """
    _send(phone_number, message, sms_type="RAW")

"""
store/signals.py
وقتی Product ذخیره یا حذف می‌شود، یک POST async به فرانت می‌زند تا
query cache را invalidate کند.

متغیرهای env لازم (در .env بک‌اند):
  FRONTEND_REVALIDATE_URL    = "http://localhost:5173/api/revalidate"
  FRONTEND_REVALIDATE_SECRET = "some-strong-secret"
  
  PB_URL                     = "http://127.0.0.1:8090"
  PB_ADMIN_EMAIL             = "your-admin-email@example.com"
  PB_ADMIN_PASSWORD          = "your-admin-password"
"""
import logging
import threading

import requests
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Product

logger = logging.getLogger(__name__)

# FRONTEND webhook settings
REVALIDATE_URL    = getattr(settings, "FRONTEND_REVALIDATE_URL", "")
REVALIDATE_SECRET = getattr(settings, "FRONTEND_REVALIDATE_SECRET", "")
REVALIDATE_TIMEOUT = 4  # ثانیه

# PocketBase settings — نام‌ها با .env هماهنگ شد
PB_URL      = getattr(settings, "PB_URL", "")
PB_EMAIL    = getattr(settings, "PB_ADMIN_EMAIL", "")
PB_PASSWORD = getattr(settings, "PB_ADMIN_PASSWORD", "")
PB_FIND_ENDPOINT = getattr(settings, "PB_FIND_ENDPOINT", "/api/collections/products_ui/records")
PB_SYNC_ENDPOINT = getattr(settings, "PB_SYNC_ENDPOINT", "/api/collections/products_ui/records")

# Token placeholder (در runtime پر میشه)
_pb_token = None


def _pb_login() -> str:
    """لاگین به PocketBase و دریافت token"""
    if not PB_URL or not PB_EMAIL or not PB_PASSWORD:
        logger.warning("PocketBase credentials not configured (PB_URL/PB_ADMIN_EMAIL/PB_ADMIN_PASSWORD)")
        return ""
    
    try:
        # endpoint درست: auth-with-password (نه auth)
        resp = requests.post(
            f"{PB_URL}/api/admins/auth-with-password",
            json={"identity": PB_EMAIL, "password": PB_PASSWORD},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json().get("token", "")
    except Exception as exc:
        logger.error("PocketBase login failed: %s", exc)
        return ""


def _pb_find(token: str, product_id: int) -> dict | None:
    """پیدا کردن رکورد در PocketBase بر اساس product_id"""
    if not token:
        return None
    
    try:
        resp = requests.get(
            f"{PB_URL}{PB_FIND_ENDPOINT}",
            params={"filter": f'product_id={product_id}'},
            headers={"Authorization": token},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        return items[0] if items else None
    except Exception as exc:
        logger.warning("PocketBase find failed for product=%s: %s", product_id, exc)
        return None


def _pb_sync(product: Product, action: str) -> None:
    """سینک یک محصول با PocketBase (create یا update)"""
    token = _pb_login()
    if not token:
        raise Exception("نمی‌توان به PocketBase لاگین کرد")
    
    existing = _pb_find(token, product.pk)
    
    data = {
        "product_id": str(product.pk),
        "name": product.name,
        "slug": product.slug,
        "price": str(product.price),
        "description": product.description or "",
        "category": product.category.name if product.category else "",
        "is_active": product.is_active,
    }
    
    url = f"{PB_URL}{PB_SYNC_ENDPOINT}"
    headers = {"Authorization": token}
    
    if existing:
        resp = requests.patch(f"{url}/{existing['id']}", json=data, headers=headers, timeout=10)
    else:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
    
    resp.raise_for_status()
    logger.info("PocketBase sync succeeded for product=%s action=%s", product.pk, action)


def _fire(product_id: int, slug: str, action: str) -> None:
    """POST به فرانت — در thread جداگانه تا request اصلی بلاک نشود."""
    if not REVALIDATE_URL:
        logger.debug("FRONTEND_REVALIDATE_URL تنظیم نشده — webhook ارسال نشد.")
        return
    payload = {
        "secret":     REVALIDATE_SECRET,
        "product_id": product_id,
        "slug":        slug,
        "action":      action,
    }
    try:
        resp = requests.post(REVALIDATE_URL, json=payload, timeout=REVALIDATE_TIMEOUT)
        resp.raise_for_status()
        logger.info("Webhook ارسال شد → product=%s action=%s", product_id, action)
    except Exception as exc:
        logger.warning("Webhook شکست خورد (product=%s): %s", product_id, exc)


def _async_fire(product_id: int, slug: str, action: str) -> None:
    threading.Thread(target=_fire, args=(product_id, slug, action), daemon=True).start()


@receiver(post_save, sender=Product)
def on_product_saved(sender, instance: Product, created: bool, **kwargs) -> None:
    _async_fire(instance.pk, instance.slug, "created" if created else "updated")
    # سینک به PocketBase هم async
    threading.Thread(
        target=_pb_sync, args=(instance, "created" if created else "updated"), daemon=True
    ).start()


@receiver(post_delete, sender=Product)
def on_product_deleted(sender, instance: Product, **kwargs) -> None:
    _async_fire(instance.pk, instance.slug, "deleted")

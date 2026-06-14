"""
store/signals.py

متغیرهای env لازم (در .env بک‌اند):
  PB_URL            = "http://127.0.0.1:8090"
  PB_ADMIN_EMAIL    = "your-admin-email@example.com"
  PB_ADMIN_PASSWORD = "your-admin-password"
"""
import logging
import threading

import requests
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Product

logger = logging.getLogger(__name__)

REVALIDATE_URL    = getattr(settings, "FRONTEND_REVALIDATE_URL", "")
REVALIDATE_SECRET = getattr(settings, "FRONTEND_REVALIDATE_SECRET", "")

PB_URL      = getattr(settings, "PB_URL", "")
PB_EMAIL    = getattr(settings, "PB_ADMIN_EMAIL", "")
PB_PASSWORD = getattr(settings, "PB_ADMIN_PASSWORD", "")
PB_COLLECTION = getattr(settings, "PB_COLLECTION_PRODUCTS", "products_ui")

# PocketBase < 0.23 از /api/admins/ استفاده میکرد
# PocketBase >= 0.23 رفت زیر /api/collections/_superusers/
_AUTH_ENDPOINTS = [
    "/api/collections/_superusers/auth-with-password",  # PB >= 0.23
    "/api/admins/auth-with-password",                   # PB < 0.23
]


def _pb_login() -> tuple[str, str]:
    """
    لاگین به PocketBase — هر دو نسخه قدیم و جدید رو امتحان میکنه.
    برمیگردونه: (token, auth_header_value)
    """
    if not PB_URL or not PB_EMAIL or not PB_PASSWORD:
        logger.warning("PocketBase credentials not set (PB_URL / PB_ADMIN_EMAIL / PB_ADMIN_PASSWORD)")
        return "", ""

    for endpoint in _AUTH_ENDPOINTS:
        try:
            resp = requests.post(
                f"{PB_URL}{endpoint}",
                json={"identity": PB_EMAIL, "password": PB_PASSWORD},
                timeout=10,
            )
            if resp.status_code == 404:
                continue  # این نسخه endpoint نداره، بعدی رو امتحان کن
            resp.raise_for_status()
            data = resp.json()
            token = data.get("token", "")
            # PB >= 0.23 توکن باید با "Bearer " بیاد
            auth_header = f"Bearer {token}" if endpoint.startswith("/api/collections/") else token
            logger.info("PocketBase login OK via %s", endpoint)
            return token, auth_header
        except requests.HTTPError as e:
            logger.error("PocketBase login HTTP error (%s): %s", endpoint, e)
        except Exception as e:
            logger.error("PocketBase login failed (%s): %s", endpoint, e)

    return "", ""


def _pb_find(auth_header: str, product_id: int) -> dict | None:
    if not auth_header:
        return None
    try:
        resp = requests.get(
            f"{PB_URL}/api/collections/{PB_COLLECTION}/records",
            params={"filter": f'product_id={product_id}', "perPage": 1},
            headers={"Authorization": auth_header},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        return items[0] if items else None
    except Exception as e:
        logger.warning("PocketBase find failed product=%s: %s", product_id, e)
        return None


def _pb_sync(product: Product, action: str) -> None:
    _, auth_header = _pb_login()
    if not auth_header:
        raise Exception("PocketBase login failed — check PB_ADMIN_EMAIL / PB_ADMIN_PASSWORD in .env")

    existing = _pb_find(auth_header, product.pk)

    data = {
        "product_id": str(product.pk),
        "name": product.name,
        "slug": product.slug,
        "price": str(product.price),
        "description": product.description or "",
        "category": product.category.name if product.category else "",
        "is_active": product.is_active,
    }

    url = f"{PB_URL}/api/collections/{PB_COLLECTION}/records"
    headers = {"Authorization": auth_header}

    if existing:
        resp = requests.patch(f"{url}/{existing['id']}", json=data, headers=headers, timeout=10)
    else:
        resp = requests.post(url, json=data, headers=headers, timeout=10)

    resp.raise_for_status()
    logger.info("PocketBase sync OK product=%s action=%s", product.pk, action)


def _fire(product_id: int, slug: str, action: str) -> None:
    if not REVALIDATE_URL:
        return
    try:
        requests.post(REVALIDATE_URL, json={
            "secret": REVALIDATE_SECRET,
            "product_id": product_id,
            "slug": slug,
            "action": action,
        }, timeout=4)
    except Exception as e:
        logger.warning("Webhook failed product=%s: %s", product_id, e)


@receiver(post_save, sender=Product)
def on_product_saved(sender, instance: Product, created: bool, **kwargs) -> None:
    action = "created" if created else "updated"
    threading.Thread(target=_fire, args=(instance.pk, instance.slug, action), daemon=True).start()
    threading.Thread(target=_pb_sync, args=(instance, action), daemon=True).start()


@receiver(post_delete, sender=Product)
def on_product_deleted(sender, instance: Product, **kwargs) -> None:
    threading.Thread(target=_fire, args=(instance.pk, instance.slug, "deleted"), daemon=True).start()

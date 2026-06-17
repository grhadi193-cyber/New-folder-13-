from decimal import Decimal
from typing import List, Optional

from core.exceptions import NotFoundError
from .models import (
    ShippingMethod,
    ShippingRate,
    ShippingZone,
    Province,
    City,
)

MASHHAD_PROVINCE_NAME = "خراسان رضوی"


# ── Province / City ─────────────────────────────────────────────────────────

def get_active_provinces() -> List[Province]:
    return list(Province.objects.filter(is_active=True).order_by("name"))


def get_cities_by_province(province_id: int) -> List[City]:
    return list(City.objects.filter(province_id=province_id, is_active=True).order_by("name"))


# ── Shipping Methods ────────────────────────────────────────────────────────

def get_active_shipping_methods() -> List[ShippingMethod]:
    return list(ShippingMethod.objects.filter(is_active=True))


# ── Province/City name → ID lookup ─────────────────────────────────────────

def _resolve_province_city_ids(
    province_name: str,
    city_name: Optional[str] = None,
) -> tuple[Optional[int], Optional[int]]:
    province = Province.objects.filter(name__iexact=province_name.strip(), is_active=True).first()
    if not province:
        return None, None

    city_id = None
    if city_name:
        city = City.objects.filter(
            province=province, name__iexact=city_name.strip(), is_active=True
        ).first()
        if city:
            city_id = city.pk

    return province.pk, city_id


def _is_mashhad(province: Province) -> bool:
    return MASHHAD_PROVINCE_NAME in province.name or province.zone_number == 1


# ── Zone-based cost formula ────────────────────────────────────────────────

def _calc_zone_cost(
    method: ShippingMethod,
    province: Province,
    total_weight_kg: float,
    order_total: Decimal,
) -> Decimal:
    """
    فرمول zone-based:
      قیمت = base_price[zone] + max(0, وزن_نهایی - 1) × price_per_kg[zone]

    ابتدا ShippingRate برای province پیدا می‌کند.
    اگر نبود، از base_cost / cost_per_kg متد استفاده می‌کند (fallback).
    """
    if method.free_above is not None and order_total >= method.free_above:
        return Decimal("0")

    if method.fixed_price is not None:
        return method.fixed_price

    rate = ShippingRate.objects.filter(
        shipping_method=method,
        province=province,
        is_active=True,
    ).first()

    if rate:
        base = rate.cost
        per_kg = method.cost_per_kg
    else:
        base = method.base_cost
        per_kg = method.cost_per_kg

    extra_weight = max(0.0, total_weight_kg - 1.0)
    cost = base + Decimal(str(extra_weight)) * per_kg
    return cost


# ── Core: find best rate for a method + province + city + weight ───────────

def _find_best_rate(
    method: ShippingMethod,
    province: Province,
    city: Optional[City],
    total_weight_kg: float,
) -> Optional[ShippingRate]:
    base_qs = ShippingRate.objects.filter(
        shipping_method=method,
        province=province,
        is_active=True,
        weight_min__lte=total_weight_kg,
        weight_max__gte=total_weight_kg,
    )

    if city:
        city_rate = base_qs.filter(city=city).first()
        if city_rate:
            return city_rate

    province_rate = base_qs.filter(city__isnull=True).first()
    if province_rate:
        return province_rate

    return None


# ── Core shipping cost calculator ──────────────────────────────────────────

def calculate_shipping_cost_v2(
    shipping_method_id: int,
    province_id: int,
    city_id: Optional[int],
    total_weight_kg: float,
    order_total: Optional[Decimal] = None,
) -> Decimal:
    try:
        method = ShippingMethod.objects.get(pk=shipping_method_id, is_active=True)
    except ShippingMethod.DoesNotExist:
        raise NotFoundError(f"ShippingMethod با id={shipping_method_id} یافت نشد یا غیرفعال است.")

    try:
        province = Province.objects.get(pk=province_id, is_active=True)
    except Province.DoesNotExist:
        raise NotFoundError(f"استان با id={province_id} یافت نشد.")

    city = None
    if city_id:
        city = City.objects.filter(pk=city_id, province=province, is_active=True).first()

    # Pik: فقط مشهد
    if method.method_type == "pik" and not _is_mashhad(province):
        raise NotFoundError("پیک فقط برای مشهد فعال است.")

    # 1. چک free_above
    total = order_total or Decimal("0")
    if method.free_above is not None and total >= method.free_above:
        return Decimal("0")

    # 2. چک fixed_price (پیک)
    if method.fixed_price is not None:
        return method.fixed_price

    # 3. جستجوی ShippingRate دقیق (شهری → استانی → وزنی)
    rate = _find_best_rate(method, province, city, total_weight_kg)
    if rate:
        return rate.cost

    # 4. fallback zone-based formula
    return _calc_zone_cost(method, province, total_weight_kg, total)


def calculate_shipping_cost_by_name(
    method: ShippingMethod,
    province_name: str,
    city_name: Optional[str],
    total_weight_kg: float,
    order_total: Decimal,
) -> Decimal:
    if method.free_above is not None and order_total >= method.free_above:
        return Decimal("0")

    if method.fixed_price is not None:
        return method.fixed_price

    province_id, city_id = _resolve_province_city_ids(province_name, city_name)

    if province_id:
        province = Province.objects.get(pk=province_id)
        city = City.objects.get(pk=city_id) if city_id else None

        rate = _find_best_rate(method, province, city, total_weight_kg)
        if rate:
            return rate.cost

        return _calc_zone_cost(method, province, total_weight_kg, order_total)

    return _calc_zone_cost(method, None, total_weight_kg, order_total)


def calculate_shipping_options_v2(
    province_id: int,
    city_id: Optional[int],
    total_weight_kg: float,
    order_total: Decimal,
) -> list:
    try:
        province = Province.objects.get(pk=province_id, is_active=True)
    except Province.DoesNotExist:
        return []

    methods = ShippingMethod.objects.filter(is_active=True)
    is_mashhad = _is_mashhad(province)
    results = []

    for method in methods:
        # پیک فقط برای مشهد
        if method.method_type == "pik" and not is_mashhad:
            continue

        try:
            cost = calculate_shipping_cost_v2(
                shipping_method_id=method.pk,
                province_id=province_id,
                city_id=city_id,
                total_weight_kg=total_weight_kg,
                order_total=order_total,
            )
            results.append({
                "id": method.pk,
                "name": method.name,
                "slug": method.slug,
                "carrier_name": method.carrier_name,
                "tracking_url_template": method.tracking_url_template,
                "cost": cost,
                "min_days": method.min_days,
                "max_days": method.max_days,
                "method_type": method.method_type,
            })
        except Exception:
            continue

    return sorted(results, key=lambda x: x["cost"])


# ── Legacy: Public API (backward compatible) ───────────────────────────────

def calculate_shipping_options(
    province: str,
    total_weight_kg: float,
    order_total: Decimal,
) -> list:
    province_obj = Province.objects.filter(name__iexact=province.strip(), is_active=True).first()
    if not province_obj:
        return []

    methods = ShippingMethod.objects.filter(is_active=True)
    is_mashhad = _is_mashhad(province_obj)
    results = []

    for method in methods:
        if method.method_type == "pik" and not is_mashhad:
            continue

        cost = _calc_zone_cost(method, province_obj, total_weight_kg, order_total)
        results.append({
            "id": method.pk,
            "name": method.name,
            "cost": cost,
            "min_days": method.min_days,
            "max_days": method.max_days,
        })

    return sorted(results, key=lambda x: x["cost"])


def calculate_shipping_cost(
    method_id_or_obj,
    total_weight: Optional[float] = None,
    order_total: Optional[Decimal] = None,
    province_name: Optional[str] = None,
    city_name: Optional[str] = None,
) -> Decimal:
    if isinstance(method_id_or_obj, ShippingMethod):
        method = method_id_or_obj
    else:
        try:
            method = ShippingMethod.objects.get(pk=method_id_or_obj, is_active=True)
        except ShippingMethod.DoesNotExist:
            raise NotFoundError(
                f"ShippingMethod با id={method_id_or_obj} یافت نشد یا غیرفعال است."
            )

    weight = total_weight if total_weight is not None else 0.0
    total = order_total if order_total is not None else Decimal("0")

    if method.fixed_price is not None:
        return method.fixed_price

    if province_name:
        return calculate_shipping_cost_by_name(
            method=method,
            province_name=province_name,
            city_name=city_name,
            total_weight_kg=weight,
            order_total=total,
        )

    province_obj = Province.objects.filter(name__iexact=MASHHAD_PROVINCE_NAME).first()
    return _calc_zone_cost(method, province_obj, weight, total)


# ── Rate CRUD helpers ──────────────────────────────────────────────────────

def get_shipping_rates_for_method(method_id: int) -> List[ShippingRate]:
    return list(
        ShippingRate.objects
        .filter(shipping_method_id=method_id)
        .select_related("province", "city", "shipping_method")
        .order_by("province__name", "city__name", "weight_min")
    )


def create_shipping_rate(
    shipping_method_id: int,
    province_id: int,
    city_id: Optional[int],
    weight_min: Decimal,
    weight_max: Decimal,
    cost: Decimal,
) -> ShippingRate:
    method = ShippingMethod.objects.get(pk=shipping_method_id)
    province = Province.objects.get(pk=province_id)
    city = City.objects.get(pk=city_id) if city_id else None

    return ShippingRate.objects.create(
        shipping_method=method,
        province=province,
        city=city,
        weight_min=weight_min,
        weight_max=weight_max,
        cost=cost,
    )

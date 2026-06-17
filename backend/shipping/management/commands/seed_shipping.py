"""
Seed shipping methods and zone-based rates.

Zone 1 (خراسان رضوی — همان استان):
  → پست پیشتاز: ۳۵,۰۰۰ + ۱۲,۰۰۰/kg
  → پست عادی:   ۲۵,۰۰۰ + ۸,۰۰۰/kg
  → تیپاکس:     ۴۵,۰۰۰ + ۱۵,۰۰۰/kg
  → پیک:        ۵۰,۰۰۰ ثابت (فقط مشهد)

Zone 2 (همجوار — خراسان شمالی/جنوبی، سمنان، گلستان، مازندران):
  → پست پیشتاز: ۴۵,۰۰۰ + ۱۵,۰۰۰/kg
  → پست عادی:   ۳۲,۰۰۰ + ۱۰,۰۰۰/kg
  → تیپاکس:     ۶۰,۰۰۰ + ۱۸,۰۰۰/kg

Zone 3 (دور — سایر استان‌ها):
  → پست پیشتاز: ۵۵,۰۰۰ + ۱۸,۰۰۰/kg
  → پست عادی:   ۴۰,۰۰۰ + ۱۲,۰۰۰/kg
  → تیپاکس:     ۷۵,۰۰۰ + ۲۲,۰۰۰/kg

Usage:
    python manage.py seed_shipping
"""
import sys
import io
from decimal import Decimal
from django.core.management.base import BaseCommand
from shipping.models import ShippingMethod, ShippingRate, Province

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


METHODS = [
    {
        "name": "پست پیشتاز",
        "slug": "post-pishtaz",
        "method_type": "pishtaz",
        "carrier_name": "شرکت پست",
        "tracking_url_template": "https://tracking.post.ir/?code={tracking_code}",
        "base_cost": 35000,
        "cost_per_kg": 12000,
        "free_above": None,
        "fixed_price": None,
        "min_days": 1,
        "max_days": 3,
    },
    {
        "name": "پست عادی",
        "slug": "post-sefareshi",
        "method_type": "sefareshi",
        "carrier_name": "شرکت پست",
        "tracking_url_template": "https://tracking.post.ir/?code={tracking_code}",
        "base_cost": 25000,
        "cost_per_kg": 8000,
        "free_above": None,
        "fixed_price": None,
        "min_days": 5,
        "max_days": 7,
    },
    {
        "name": "تیپاکس",
        "slug": "tipax",
        "method_type": "tipax",
        "carrier_name": "تیپاکس",
        "tracking_url_template": "https://tipaxco.com/tracking?code={tracking_code}",
        "base_cost": 45000,
        "cost_per_kg": 15000,
        "free_above": None,
        "fixed_price": None,
        "min_days": 1,
        "max_days": 2,
    },
    {
        "name": "پیک مشهد",
        "slug": "pik-mashhad",
        "method_type": "pik",
        "carrier_name": "پیک",
        "tracking_url_template": "",
        "base_cost": 0,
        "cost_per_kg": 0,
        "free_above": None,
        "fixed_price": 50000,
        "min_days": 0,
        "max_days": 1,
    },
]


ZONE_RATES = {
    1: {
        "base": {"post-pishtaz": 35000, "post-sefareshi": 25000, "tipax": 45000},
        "per_kg": {"post-pishtaz": 12000, "post-sefareshi": 8000, "tipax": 15000},
    },
    2: {
        "base": {"post-pishtaz": 45000, "post-sefareshi": 32000, "tipax": 60000},
        "per_kg": {"post-pishtaz": 15000, "post-sefareshi": 10000, "tipax": 18000},
    },
    3: {
        "base": {"post-pishtaz": 55000, "post-sefareshi": 40000, "tipax": 75000},
        "per_kg": {"post-pishtaz": 18000, "post-sefareshi": 12000, "tipax": 22000},
    },
}


class Command(BaseCommand):
    help = "ساخت شیوه‌های ارسال و تعرفه‌های zone-based برای همه استان‌ها"

    def handle(self, *args, **options):
        self.stdout.write("-" * 50)
        self.stdout.write("Seeding shipping methods...")

        methods = {}
        for m in METHODS:
            obj, created = ShippingMethod.objects.update_or_create(
                slug=m["slug"],
                defaults=m,
            )
            methods[m["slug"]] = obj
            status = "created" if created else "updated"
            self.stdout.write(f"  {m['name']} - {status}")

        self.stdout.write("")
        self.stdout.write("Seeding zone-based rates...")

        method_slugs = list(methods.keys())
        deleted, _ = ShippingRate.objects.filter(
            shipping_method__slug__in=method_slugs,
            city__isnull=True,
        ).delete()
        self.stdout.write(f"  Cleared {deleted} existing province-level rates.")

        provinces = Province.objects.all()
        created_count = 0

        for province in provinces:
            zone = province.zone_number
            if zone not in ZONE_RATES:
                self.stdout.write(self.style.WARNING(
                    f"  Province '{province.name}' invalid zone ({zone}) - skipped"
                ))
                continue

            zone_data = ZONE_RATES[zone]
            for method_slug, base_cost in zone_data["base"].items():
                method = methods[method_slug]

                _, created = ShippingRate.objects.get_or_create(
                    shipping_method=method,
                    province=province,
                    city=None,
                    weight_min=Decimal("0"),
                    defaults={
                        "weight_max": Decimal("9999"),
                        "cost": base_cost,
                        "is_active": True,
                    },
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {len(METHODS)} shipping methods, {created_count} rates created."
        ))
        self.stdout.write("")
        self.stdout.write(" Zone 1 (Khorasan Razavi):  Post Pishtaz 35k + 12k/kg")
        self.stdout.write(" Zone 2 (Neighboring):      Post Pishtaz 45k + 15k/kg")
        self.stdout.write(" Zone 3 (Far):              Post Pishtaz 55k + 18k/kg")
        self.stdout.write(" Pik Mashhad:               50,000 Toman fixed")

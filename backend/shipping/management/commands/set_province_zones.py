"""
Set zone_number for all provinces relative to Mashhad.

Zone 1: Khorasan Razavi (same province)
Zone 2: Khorasan Shomali/Jonoubi, Semnan, Golestan, Mazandaran (neighboring)
Zone 3: all other provinces

Usage:
    python manage.py set_province_zones
"""
import sys
import io
from django.core.management.base import BaseCommand
from shipping.models import Province

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


ZONE_1 = ["خراسان رضوی"]

ZONE_2 = [
    "خراسان شمالی",
    "خراسان جنوبی",
    "سمنان",
    "گلستان",
    "مازندران",
]


class Command(BaseCommand):
    help = "Set zone_number for provinces relative to Mashhad"

    def handle(self, *args, **options):
        updated = 0

        for name in ZONE_1:
            count = Province.objects.filter(name__icontains=name).update(zone_number=1)
            updated += count
            if count:
                self.stdout.write(f"  Zone 1: {name}")

        for name in ZONE_2:
            count = Province.objects.filter(name__icontains=name).update(zone_number=2)
            updated += count
            if count:
                self.stdout.write(f"  Zone 2: {name}")

        count = Province.objects.exclude(
            name__icontains="خراسان رضوی"
        ).exclude(
            name__in=ZONE_2
        ).update(zone_number=3)
        updated += count

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {updated} provinces updated."
        ))

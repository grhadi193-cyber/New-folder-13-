"""
python manage.py sync_products_to_pb
python manage.py sync_products_to_pb --force
"""
import logging
from django.core.management.base import BaseCommand
from store.models import Product
from store.signals import _pb_login, _pb_find, _pb_sync, PB_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'همه محصولات Django را با PocketBase sync میکند'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='رکوردهای موجود را هم آپدیت کن')

    def handle(self, *args, **options):
        if not PB_URL:
            self.stderr.write('❌  PB_URL در .env تنظیم نشده')
            return

        _, auth_header = _pb_login()
        if not auth_header:
            self.stderr.write('❌  نمیشه به PocketBase لاگین کرد — PB_ADMIN_EMAIL/PB_ADMIN_PASSWORD رو چک کن')
            return

        products = Product.objects.select_related('category').all()
        total = products.count()
        self.stdout.write(f'🔄  {total} محصول پیدا شد...\n')

        ok = skip = fail = 0
        for p in products:
            existing = _pb_find(auth_header, p.pk)
            if existing and not options['force']:
                self.stdout.write(f'  ⏭  #{p.pk} {p.name} — از قبل موجوده')
                skip += 1
                continue
            try:
                _pb_sync(p, 'updated' if existing else 'created')
                self.stdout.write(f'  ✅  #{p.pk} {p.name}')
                ok += 1
            except Exception as e:
                self.stderr.write(f'  ❌  #{p.pk} {p.name}: {e}')
                fail += 1

        self.stdout.write(f'\n✅ {ok} sync | ⏭ {skip} رد شد | ❌ {fail} خطا')

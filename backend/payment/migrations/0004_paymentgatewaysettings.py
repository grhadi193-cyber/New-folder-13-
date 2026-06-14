# Generated migration for PaymentGatewaySettings model

from django.db import migrations, models


def create_default_payment_settings(apps, schema_editor):
    """Create default payment gateway settings on migration."""
    PaymentGatewaySettings = apps.get_model('payment', 'PaymentGatewaySettings')
    if not PaymentGatewaySettings.objects.exists():
        PaymentGatewaySettings.objects.create(
            pk=1,
            mode='sandbox',
            zarinpal_merchant_code='sandbox',
            auto_verify=True,
            callback_base_url='',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_transaction_callback_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentGatewaySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zarinpal_merchant_code', models.CharField(blank=True, default='sandbox', help_text='کد مرچنت دریافتی از پنل زرین‌پال (برای سندباکس: sandbox)', max_length=50, verbose_name='کد مرچنت زرین‌پال')),
                ('mode', models.CharField(choices=[('sandbox', 'حالت سندباکس (پرداخت شبیه‌سازی شده)'), ('production', 'حالت واقعی (پرداخت واقعی با زرین‌پال)')], default='sandbox', help_text='در حالت سندباکس، پرداخت واقعی انجام نمی‌شود', max_length=20, verbose_name='حالت عملیات')),
                ('callback_base_url', models.URLField(blank=True, help_text='آدرس پایه برای بازگشت از درگاه (مثلاً: https://yourdomain.com/api/payment/callback)', verbose_name='آدرس پایه کالبک')),
                ('auto_verify', models.BooleanField(default=True, help_text='در حالت سندباکس تراکنش‌ها به صورت خودکار تایید می‌شوند', verbose_name='تایید خودکار تراکنش')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')),
            ],
            options={
                'verbose_name': 'تنظیمات درگاه پرداخت',
                'verbose_name_plural': 'تنظیمات درگاه پرداخت',
            },
        ),
        migrations.RunPython(create_default_payment_settings, reverse_code=migrations.RunPython.noop),
    ]

# Generated migration for SMSSettings model

from django.db import migrations, models


def create_default_sms_settings(apps, schema_editor):
    """Create default SMS settings on migration."""
    SMSSettings = apps.get_model('sms', 'SMSSettings')
    if not SMSSettings.objects.exists():
        SMSSettings.objects.create(
            pk=1,
            mode='test',
            kavenegar_api_key='',
            sender_number='',
            otp_template_name='',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMSSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kavenegar_api_key', models.CharField(blank=True, help_text='کلید API دریافتی از پنل Kavenegar', max_length=100, verbose_name='API Key کاوه نگار')),
                ('sender_number', models.CharField(blank=True, help_text='شماره خط اختصاصی (مثلاً: 1000596446)', max_length=20, verbose_name='شماره ارسال‌کننده')),
                ('mode', models.CharField(choices=[('test', 'حالت تست (لاگ در دیتابیس + نمایش در کنسول)'), ('production', 'حالت واقعی (ارسال از طریق Kavenegar)')], default='test', help_text='در حالت تست، پیامک واقعی ارسال نمی‌شود و فقط لاگ می‌شود', max_length=20, verbose_name='حالت عملیات')),
                ('otp_template_name', models.CharField(blank=True, default='', help_text='نام الگوی OTP ثبت‌شده در پنل Kavenegar (اختیاری)', max_length=100, verbose_name='قالب OTP (نام الگو در Kavenegar)')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')),
            ],
            options={
                'verbose_name': 'تنظیمات پیامک',
                'verbose_name_plural': 'تنظیمات پیامک',
            },
        ),
        migrations.AddField(
            model_name='smslog',
            name='is_test_mode',
            field=models.BooleanField(default=False, verbose_name='حالت تست'),
        ),
        migrations.AddField(
            model_name='smslog',
            name='provider_response',
            field=models.TextField(blank=True, default='', verbose_name='پاسخ پرووایدر'),
        ),
        migrations.RunPython(create_default_sms_settings, reverse_code=migrations.RunPython.noop),
    ]

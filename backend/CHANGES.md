# Changelog - تغییرات

## تغییرات اعمال شده

### 1. رفع ایرادات بحرانی

#### 1.1. رفع باگ `PAYMENT_CALLBACK_URL` در ZarinpalProvider
- **مشکل:** در فایل `payment/providers/zarinpal.py` از `settings.PAYMENT_CALLBACK_URL` استفاده شده بود که در فایل settings تعریف نشده بود
- **راه‌حل:** به جای آن از `PaymentGatewaySettings.get_callback_base_url()` استفاده شد که اولویت را به تنظیمات ادمین می‌دهد

#### 1.2. عدم انعطاف‌پذیری در انتخاب حالت تست/واقعی
- **مشکل:** سیستم پیامک و پرداخت صرفاً بر اساس `settings.DEBUG` تصمیم می‌گرفتند که در حالت تست یا واقعی کار کنند
- **راه‌حل:** حالت تست/واقعی از طریق Django Admin قابل کنترل شد

---

### 2. سیستم پیامک (Kavenegar)

#### 2.1. مدل جدید: `SMSSettings`
- مسیر: `/admin/sms/smssettings/1/change/`
- قابلیت‌ها:
  - انتخاب حالت **تست** یا **واقعی**
  - تنظیم **API Key** کاوه نگار
  - تنظیم **شماره ارسال‌کننده** (Sender)
  - تنظیم **نام قالب OTP** (برای ارسال از طریق Lookup Kavenegar)

#### 2.2. مشاهده لاگ پیامک‌ها
- مسیر: `/admin/sms/smslog/`
- در حالت تست، تمام پیامک‌ها (شامل OTP) در اینجا لاگ می‌شوند و در کنسول چاپ می‌شوند
- فیلد جدید `is_test_mode` مشخص می‌کند که پیامک در حالت تست بوده یا واقعی
- فیلد جدید `provider_response` پاسخ پرووایدر یا خطا را ذخیره می‌کند

#### 2.3. حالت تست (Test Mode)
- پیامک واقعی ارسال **نمی‌شود**
- پیامک در دیتابیس **لاگ** می‌شود
- پیامک در **کنسول** چاپ می‌شود
- برای مشاهده OTP ارسالی: به `/admin/sms/smslog/` بروید

#### 2.4. حالت واقعی (Production Mode)
- پیامک از طریق **Kavenegar** ارسال می‌شود
- نیاز به تنظیم API Key معتبر

---

### 3. سیستم پرداخت (Zarinpal)

#### 3.1. مدل جدید: `PaymentGatewaySettings`
- مسیر: `/admin/payment/paymentgatewaysettings/1/change/`
- قابلیت‌ها:
  - انتخاب حالت **سندباکس** یا **واقعی**
  - تنظیم **کد مرچنت** زرین‌پال
  - تنظیم **آدرس کالبک** (Callback URL)
  - تنظیم **تایید خودکار** تراکنش در سندباکس

#### 3.2. حالت سندباکس (Sandbox Mode)
- پرداخت واقعی انجام **نمی‌شود**
- تراکنش به صورت **خودکار تایید** می‌شود (با `auto_verify=True`)
- برای تست کامل فلو پرداخت بدون نیاز به درگاه واقعی

#### 3.3. حالت واقعی (Production Mode)
- پرداخت از طریق **زرین‌پال** انجام می‌شود
- نیاز به کد مرچنت معتبر و آدرس کالبک HTTPS

---

### 4. Migration های جدید

```bash
python manage.py migrate
```

- `sms/migrations/0002_smssettings_smslog_is_test_mode_smslog_provider_response.py`
  - ایجاد جدول `SMSSettings`
  - اضافه کردن فیلدهای `is_test_mode` و `provider_response` به `SMSLog`
  - ایجاد ردیف پیش‌فرض تنظیمات

- `payment/migrations/0004_paymentgatewaysettings.py`
  - ایجاد جدول `PaymentGatewaySettings`
  - ایجاد ردیف پیش‌فرض تنظیمات

---

### 5. API Documentation به‌روز شده

فایل `API_DOCUMENTATION.md` به‌روز شده و شامل:
- بخش **SMS Configuration** با توضیحات کامل
- بخش **Payment Configuration** با توضیحات کامل
- بخش **Admin Panel Quick Reference** برای دسترسی سریع
- توضیحات حالت تست و سندباکس برای هر endpoint مرتبط

---

### 6. فایل‌های تغییر داده شده

| فایل | تغییر |
|------|-------|
| `sms/models.py` | اضافه شدن `SMSSettings`، فیلدهای جدید به `SMSLog` |
| `sms/admin.py` | ثبت `SMSSettings` در ادمین |
| `sms/services.py` | استفاده از `SMSSettings` به جای `settings.DEBUG` |
| `payment/models.py` | اضافه شدن `PaymentGatewaySettings` |
| `payment/admin.py` | ثبت `PaymentGatewaySettings` در ادمین |
| `payment/orchestrator.py` | استفاده از `PaymentGatewaySettings`، auto-verify سندباکس |
| `payment/providers/zarinpal.py` | استفاده از تنظیمات ادمین برای مرچنت و کالبک |
| `payment/providers/mock.py` | بهبود لاگ‌ها و استفاده از تنظیمات ادمین |
| `API_DOCUMENTATION.md` | به‌روز رسانی کامل |

---

## دستورالعمل استفاده

### مرحله 1: اعمال Migration ها
```bash
python manage.py migrate
```

### مرحله 2: ساخت سوپریوزر (اگر ندارید)
```bash
python manage.py createsuperuser
```

### مرحله 3: ورود به پنل ادمین
```
http://your-domain.com/admin/
```

### مرحله 4: تنظیمات پیامک
1. به `/admin/sms/smssettings/1/change/` بروید
2. حالت را روی **"حالت تست"** بگذارید (برای توسعه)
3. یا حالت را روی **"حالت واقعی"** بگذارید و API Key را وارد کنید

### مرحله 5: تنظیمات پرداخت
1. به `/admin/payment/paymentgatewaysettings/1/change/` بروید
2. حالت را روی **"حالت سندباکس"** بگذارید (برای توسعه)
3. یا حالت را روی **"حالت واقعی"** بگذارید و کد مرچنت + آدرس کالبک HTTPS را وارد کنید

### مرحله 6: تست OTP
```bash
# ارسال OTP (در حالت تست، پیامک واقعی ارسال نمی‌شود)
curl -X POST http://localhost:8000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09123456789"}'

# مشاهده OTP در لاگ ادمین:
# بروید به /admin/sms/smslog/

# تایید OTP
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09123456789", "code": "<CODE_FROM_LOG>"}'
```

### مرحله 7: تست پرداخت (سندباکس)
```bash
# 1. ساخت سفارش
curl -X POST http://localhost:8000/api/orders \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"address_id": 1, "shipping_method_id": 1, "items": [{"product_id": 1, "quantity": 1}]}'

# 2. شروع پرداخت
curl -X POST http://localhost:8000/api/payment/initiate \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1}'

# 3. پرداخت خودکار با باز کردن لینک payment_url در مرورگر
# تراکنش خودکار تایید می‌شود!
```

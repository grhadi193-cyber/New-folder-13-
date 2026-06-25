# راهنمای دیپلوی با SSH — مرحله به مرحله

## اطلاعات سرورها
| سرور | SSH | سرویس |
|------|-----|--------|
| Backend | ubuntu@95.38.161.104 | Django + PostgreSQL + Nginx |
| Frontend | ubuntu@95.38.161.205 | Next.js + Nginx |

---

## مرحله ۱: دیپلوی Backend

### ۱.۱ — اجرای اسکریپت آپلود (از کامپیوتر خودت)
```powershell
cd "C:\Users\PC-01\Downloads\New folder (13)"
.\deploy-backend.ps1
```
> پسورد SSH رو وارد کن وقتی پرسید

### ۱.۲ — ورود به سرور بک‌اند
```bash
ssh ubuntu@95.38.161.104
```

### ۱.۳ — تنظیم فایل .env
```bash
cd /home/ubuntu/backend-deploy
nano .env
```

محتوای `.env` (دو خط زیر رو عوض کن):
```env
POSTGRES_PASSWORD=اینجا_یه_رمز_قوی_بنویس
SECRET_KEY=اینجا_یه_کلید_50_کاراکتری_بنویس
```

> برای ساخت SECRET_KEY این دستور رو توی سرور بزن:
> ```bash
> python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```
> اگه python3 نبود:
> ```bash
> sudo apt install python3 -y
> ```

ذخیره: `Ctrl+O` → Enter → `Ctrl+X`

### ۱.۴ — بیلد و اجرا
```bash
docker compose build --no-cache
docker compose up -d
```

### ۱.۵ — بررسی وضعیت
```bash
docker compose ps
```
باید ۳ سرویس ببینی: `db`, `backend`, `nginx` — همه `running`

### ۱.۶ — تست سلامت
```bash
curl http://localhost/api/health
```
جواب باید باشه: `{"status": "ok"}`

### ۱.۷ — دیدن لاگ‌ها
```bash
docker compose logs -f
```
> Ctrl+C برای خروج از لاگ

---

## مرحله ۲: دیپلوی Frontend

### ۲.۱ — اجرای اسکریپت آپلود (از کامپیوتر خودت)
```powershell
cd "C:\Users\PC-01\Downloads\New folder (13)"
.\deploy-frontend.ps1
```

### ۲.۲ — ورود به سرور فرانت
```bash
ssh ubuntu@95.38.161.205
```

### ۲.۳ — بیلد و اجرا
```bash
cd /home/ubuntu/frontend-deploy
docker compose build --no-cache
docker compose up -d
```

### ۲.۴ — بررسی وضعیت
```bash
docker compose ps
```
باید ۲ سرویس ببینی: `frontend`, `nginx` — همه `running`

### ۲.۵ — تست
مرورگر رو باز کن: `http://95.38.161.205`

---

## مرحله ۳: تست نهایی

| لینک | چی باید ببینی |
|------|---------------|
| `http://95.38.161.104/api/health` | `{"status": "ok"}` |
| `http://95.38.161.104/admin/` | صفحه لاگین Django Admin |
| `http://95.38.161.205` | صفحه اصلی سایت |

---

## عیب‌یابی

### پورت 80 اشغاله
```bash
sudo lsof -i :80
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### بیلد Docker fail شد
```bash
docker system prune -a
docker compose build --no-cache
```

### بک‌اند به دیتابیس وصل نمیشه
```bash
docker compose logs db
docker compose restart db
```

### فرانت به بک‌اند وصل نمیشه
IP بک‌اند رو چک کن:
```bash
grep API_URL docker-compose.yml
```

---

## آپدیت‌های بعدی

### Backend:
```bash
ssh ubuntu@95.38.161.104
cd /home/ubuntu/backend-deploy
# فایل‌های جدید رو scp کن
docker compose build --no-cache
docker compose up -d
```

### Frontend:
```bash
ssh ubuntu@95.38.161.205
cd /home/ubuntu/frontend-deploy
# فایل‌های جدید رو scp کن
docker compose build --no-cache
docker compose up -d
```

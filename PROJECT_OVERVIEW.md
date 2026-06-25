# 📦 Project Overview — ATi Farzam Iranian (GPS Tracker Shop)

> **Purpose of this file:** A single source of truth about the project's architecture, conventions, and structure. Read this once instead of re-discovering the codebase for every task.
>
> **Last reviewed:** 2026-06-25

---

## 1. What is this project?

A full-stack **e-commerce platform for GPS tracker devices** (فروشگاه دستگاه‌های ردیاب GPS), targeting the **Iranian market**.

- **Brand name:** ATi Farzam Iranian (آتی فرزام ایرانی)
- **Language:** RTL Persian (فارسی) UI, with Persian/Farsi comments throughout the code
- **Currency:** Iranian Toman (integer, `decimal_places=0`)
- **Auth:** Phone-number + **OTP** based (SMS via Kavenegar), password is optional/secondary
- **Payment:** **Zarinpal** (Iranian gateway) via `az-iranian-bank-gateways` library
- **Shipping:** Post/chapar/etc. with province→city structure + volumetric weight calc

---

## 2. Tech Stack

### Backend (`/backend`) — Django
| Concern | Choice |
|---------|--------|
| Framework | **Django 4.2+ (<5.0)** |
| API | **django-ninja** (Pydantic v2 schemas, FastAPI-like) |
| DB | **PostgreSQL** (SQLite fallback for dev) |
| Auth tokens | **djangorestframework-simplejwt** (JWT, 7-day access) |
| Settings/env | **django-environ** + **dj-database-url** |
| CORS | `django-cors-headers` |
| Static | **WhiteNoise** |
| Payment | **az-iranian-bank-gateways** (Zarinpal) |
| SMS | **kavenegar** |
| Server | **Gunicorn** (3 workers, runs as non-root `django` user) |
| Python | 3.12 |

### Frontend (`/frontend`) — Next.js
| Concern | Choice |
|---------|--------|
| Framework | **Next.js 15** (App Router, `output: 'standalone'`) |
| React | **19** |
| Styling | **Tailwind CSS 3.4** + `tailwindcss-animate` |
| UI primitives | **Radix UI** + `class-variance-authority` (shadcn pattern in `components/ui/`) |
| State | **Zustand** (with `persist` middleware — localStorage) |
| Server state | **TanStack React Query 5** |
| Forms | **react-hook-form** + **zod** |
| Animation | **framer-motion**, **lenis** (smooth scroll), **swiper** |
| CMS/editor | **@puckeditor/core** (admin visual page editor at `/editor`) |
| Toasts | **sonner** |
| Icons | **lucide-react** + custom `components/shared/icons/` |
| Language | TypeScript |

---

## 3. Repository Layout

```
New folder (13)/
├── backend/                    # Django project
│   ├── config/                 # Project settings
│   │   ├── settings/{base,local,production}.py
│   │   ├── urls.py             # URL routing (NinjaAPI mounted at /api)
│   │   └── wsgi.py
│   ├── accounts/               # User, OTP, Address, auth endpoints
│   ├── core/                   # SiteSettings (singleton), Banner, Partner, Page, Contact
│   ├── store/                  # Category, Product(+images/features/specs/faqs/reviews), Order
│   ├── shipping/               # ShippingMethod, Province, City
│   ├── payment/                # Transaction, Zarinpal orchestrator + providers
│   ├── sms/                    # Kavenegar SMS service
│   ├── notifications/          # Queued push/SMS notifications
│   ├── blog/                   # Blog posts
│   ├── chatbot/                # AI chat widget backend
│   ├── admin_panel/            # Admin-only endpoints
│   ├── requirements/{base,local,production}.txt
│   ├── Dockerfile + entrypoint.sh
│   └── manage.py
├── frontend/                   # Next.js project
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/         # login, forgot-password
│   │   │   ├── (main)/         # home, products, cart, checkout, profile, blog, contact, about
│   │   │   ├── editor/         # Puck visual page editor (admin-only, prod→404)
│   │   │   ├── api/chatbot/    # Next.js route handlers proxying chatbot
│   │   │   └── api/editor/     # Next.js route handlers for CMS pages
│   │   ├── components/         # UI (see §6)
│   │   └── lib/
│   │       ├── api/{django,pages,pocketbase}.ts   # data layer
│   │       ├── store/          # zustand stores (auth, cart, ...)
│   │       └── utils.ts
│   ├── Dockerfile
│   └── next.config.ts
├── docker-compose.yml          # db + backend + frontend (full stack)
├── deploy/                     # server deploy artifacts (nginx etc.)
├── deploy-{backend,frontend}.ps1   # PowerShell SCP upload scripts
├── DEPLOY-GUIDE.md             # Persian step-by-step deploy guide (2 servers)
└── README.md
```

---

## 4. Backend Deep-Dive

### 4.1 Django Apps (in `INSTALLED_APPS` order)
`core, sms, notifications, accounts, store, shipping, payment, blog, admin_panel, chatbot`

### 4.2 API Routing (`config/urls.py`)
A single **NinjaAPI** is mounted at `/api` with sub-routers:

| Router | Prefix | Notes |
|--------|--------|-------|
| core | `/api/` | settings, banners, partners, pages, contact |
| accounts | `/api/auth/` | OTP, login, profile, addresses, user orders |
| store | `/api/` | `/categories`, `/products`, `/products/{id|slug}`, `/orders` |
| shipping | `/api/shipping/` | provinces, cities, calculate |
| payment | `/api/payment/` | `/initiate`, `/callback` (gateway redirect) |
| blog | `/api/blog/` | posts |
| admin | `/api/admin/` | admin-only |
| notifications | `/api/notifications/` | |
| chatbot | `/api/chatbot/` | AI chat |

Other URLs: `admin/`, `api/health`, `api/media/<path>` + `media/<path>` (custom media server), `bankgateways/` (azbankgateways callback), `chatbot/`.

- **API Docs:** `/docs` (Ninja Swagger)
- **Health check:** `GET /api/health → {"status":"ok"}`

### 4.3 Auth Model
- Custom user: `accounts.User` (`AUTH_USER_MODEL = "accounts.User"`)
- **`USERNAME_FIELD = "phone_number"`** (NOT email/username)
- Fields: `phone_number` (unique), `full_name`, `email`, `national_id` (validated Iranian کد ملی), `is_staff`, `is_active`
- **OTP flow:** `send-otp` → `verify-otp` → JWT issued (`RefreshToken.for_user`)
- OTP model: `OTPRecord` (code, expires_at, rate-limited 60s between sends, default 2-min expiry via `OTP_EXPIRY_MINUTES`)
- **Test mode:** when `DEBUG`/`TEST_MODE`/`SiteSettings.otp_test_mode` → OTP code returned in `send-otp` response (`otp_code` field)
- JWT auth via Ninja `AuthBearer()` (Bearer token in `Authorization` header)

### 4.4 Key Models
- **`core.SiteSettings`** — singleton (`pk=1`, via `.get()`). Holds site name/logo/colors, `shop_enabled`, `max_order_quantity`, `otp_test_mode`, hero/about/software content, lots of image slots. **This is the CMS replacement for PocketBase.**
- **`store.Product`** — category (PROTECT), name/slug, price + discount_price, stock, dimensions (for volumetric weight), image + gallery (`ProductImage`), `features`, `specifications`, `faqs`, `reviews`. Properties: `effective_price`, `volumetric_weight` (L×W×H÷5000), `effective_shipping_weight`.
- **`store.Order`** — status (`pending→paid→processing→shipped→delivered` or `cancelled`), total_price, shipping_cost, tracking_number (auto `ORD-000001`), snapshot of address, `OrderStatusHistory` log. `OrderItem` has `product_name_snapshot`.
- **`payment.Transaction`** — tracks gateway txns; `PaymentGatewaySettings` (singleton, sandbox/auto-verify flags).
- **`shipping.ShippingMethod`**, `Province`, `City` (seeded via management commands `load_provinces_cities`, `set_province_zones`, `seed_shipping`).

### 4.5 Payment Flow
1. `POST /api/orders` creates order + auto-initiates payment → returns `payment_url`.
2. `POST /api/payment/initiate` re-initiates for an existing unpaid order.
3. `start_payment()` → provider (`MockProvider` in sandbox, `ZarinpalProvider` in prod) creates a `Transaction`, returns gateway URL.
4. Gateway redirects to `GET /api/payment/callback?...` → `verify_payment()` → marks order `paid` → triggers notifications + success SMS.
5. On success/failure, backend **redirects to frontend** `/payment-result?status=paid|failed&...`.
6. **Sandbox mode auto-verifies** (no real gateway needed) — controlled by `PaymentGatewaySettings`.

### 4.6 Settings Structure
- `config/settings/base.py` — shared (DB, apps, middleware, JWT, OTP, SMS, payment dict, CORS_ALLOW_ALL=True for dev)
- `local.py` — dev overrides (debug toolbar)
- `production.py` — **all secrets from env** (`SECRET_KEY`, `DATABASE_URL` raise if missing); WhiteNoise static; rotating file logs at `/app/logs`; SSL/HSTS gated on `USE_SSL`.

### 4.7 Entrypoint (`entrypoint.sh`) — runs as root, drops to `django` user
1. Wait for Postgres (60 retries, exponential backoff)
2. Run migrations (skip if `SKIP_MIGRATE=true`)
3. Create + chown media dirs
4. `collectstatic`
5. Seed provinces/cities + zones + shipping (idempotent)
6. Gunicorn (port `$PORT` or 8000, 3 workers, 120s timeout)

---

## 5. Frontend Deep-Dive

### 5.1 Route Groups (App Router)
- `(auth)/` — minimal layout: login, forgot-password
- `(main)/` — full site chrome (Navbar/Footer): home, products, cart, checkout, profile (+ sub-routes), blog, contact, about, software, payment-result
- `editor/` + `page/[slug]/` — Puck visual editor (admin-only; **redirected to /404 in production**)
- `api/` — Next.js route handlers proxying chatbot & editor to backend

### 5.2 Data Layer (`src/lib/api/`)
- **`django.ts`** — primary API client. Server-side uses `INTERNAL_API_URL` (Docker internal `http://backend:8000`), client-side uses relative `/api` (proxied by Next rewrites → `NEXT_PUBLIC_API_URL`).
  - Auth endpoints: `sendOtp`, `verifyOtp`, `login`, `getProfile`, `updateProfile`, `changePassword`, `forgotPassword`, `resetPassword`
  - **IMPORTANT field-name conventions:** backend uses `phone_number` (not `phone`), `new_password` (not `password` for reset). These are commented in the code.
  - `djangoImageUrl` / `publicImageUrl` — normalize media URLs (strip backend origin so they go through Next proxy)
- `pages.ts`, `pocketbase.ts` — legacy/secondary (PocketBase was the old CMS, now migrated to Django `Page` model)

### 5.3 State (`src/lib/store/`) — Zustand + persist
- **`auth.ts`** — `token`, `user`, `setAuth`, `logout`. On set, writes cookie `afi_token` (for SSR/middleware). Persisted as `afi_auth`.
- **`cart.ts`** — `items[]`, add/remove/update/clear, enforces `maxOrderQuantity` (from SiteSettings, default 999). Persisted as `afi_cart`.
- `cart-drawer.ts`, `login-modal.ts`, `shop-status.tsx`, `user-trail.ts` — UI-toggle stores.

### 5.4 next.config.ts
- `output: 'standalone'`, `reactStrictMode`
- `images.remotePatterns` whitelists localhost:8000, internal IPs, `farzam.runflare.run`
- **Rewrites:** `/api/*` and `/media/*` → backend (enables client-side relative fetch)
- **Redirects:** `/editor` → `/404` in production

### 5.5 Component Organization (`src/components/`)
- `ui/` — shadcn-style primitives (button, dialog, select, alert-dialog, ...)
- `auth/` — LoginModal, OtpForm, OtpInput, PasswordForm, CountdownTimer
- `cart/` — CartDrawer, CartItem, CartSummary
- `checkout/` — AddressStep, ShippingStep, ConfirmStep, StepIndicator, PaymentReceipt
- `product/` — ProductCard, AddToCartButton, ImageSlider, QuantitySelector
- `home/` — HeroSlider, PartnersMarquee, StatsCounter, TestimonialsCarousel, NewsletterForm, TrustBar
- `layout/` — Navbar, Footer, MobileMenu, CmdKSearch, FloatingActions, CursorFollower
- `blog/`, `contact/`, `profile/`, `chatbot/`, `editor/`, `tracking/`, `trail/`, `shared/` (animations, icons, breadcrumb, pagination, LenisProvider)
- `Providers.tsx` — top-level providers (React Query, etc.)

---

## 6. Deployment

### Environments (from DEPLOY-GUIDE.md)
Two **self-hosted Ubuntu servers** (SSH-based Docker Compose):
| Role | IP | Stack |
|------|----|-------|
| Backend | `95.38.161.104` | Django + PostgreSQL + Nginx |
| Frontend | `95.38.161.205` | Next.js + Nginx |

Deploy scripts: `deploy-backend.ps1` / `deploy-frontend.ps1` (SCP the `*-deploy.zip` → server runs `docker compose build --no-cache && up -d`).

There's also a **Runflare** deployment path (see `.env.example` domains `*.runflare.run` and `runflare.yaml`).

### Critical Environment Variables
| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret (required in prod, raises if missing) |
| `DATABASE_URL` | Postgres connection (required in prod) |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DEBUG` / `TEST_MODE` | both `False` in prod |
| `ALLOWED_HOSTS` | comma-separated |
| `CORS_ALLOWED_ORIGINS` | frontend URL |
| `CSRF_TRUSTED_ORIGINS` | |
| `FRONTEND_BASE_URL` | for payment redirects |
| `PAYMENT_CALLBACK_BASE_URL` | backend callback URL |
| `ZARINPAL_MERCHANT_CODE` / `PAYMENT_SANDBOX` | payment |
| `KAVENEGAR_API_KEY` / `SMS_SENDER` | SMS/OTP |
| `OTP_EXPIRY_MINUTES` | default 2 |
| `USE_SSL` | toggles secure cookies + HSTS |
| Frontend: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SITE_URL`, `INTERNAL_API_URL` | API addressing |

---

## 7. Conventions & Gotchas (read before editing)

1. **Persian is the domain language** — UI text, model `verbose_name`, and most code comments are in فارسی. Match this when adding strings.
2. **Phone-number is the identity**, not email. Auth payload field is **`phone_number`**.
3. **Prices are integers (Toman)** — `decimal_places=0`.
4. **Error response shape is uniform:** `{"error": true, "code": "<slug>", "message": "..."}` with proper HTTP status. Follow this for new endpoints.
5. **`SiteSettings` is a singleton (`pk=1`)** — access via `SiteSettings.get()`. It gates `shop_enabled` (order creation) and `otp_test_mode`.
6. **Images:** backend serves `/media/...` itself (custom `serve_media` view); frontend normalizes via `djangoImageUrl()` and proxies `/media/*` through Next rewrites. Set image URLs relative.
7. **Cart limit** comes from `SiteSettings.max_order_quantity` (default 20) — enforced both backend (`create_order`) and frontend cart store.
8. **OTP rate-limit:** 60s between sends (`OTP_RATE_LIMIT_SECONDS`); 2-min expiry by default.
9. **Migrations:** the latest commit history shows migration/entrypoint pain (`0007` made idempotent) — be careful with migration ordering; `SKIP_MIGRATE=true` can bypass in a pinch.
10. **`/editor`** (Puck visual editor) is dev/admin-only and hard-redirects to 404 in production.
11. **Frontend API client** (`django.ts`) uses bare `fetch`, not axios. Auth = `Authorization: Bearer <token>`. Token also mirrored to `afi_token` cookie for middleware.
12. **Docker entrypoint runs as root** (to chown media/static) then drops to `django` user for Gunicorn — don't add a `USER` directive to the Dockerfile.
13. **State persistence:** Zustand keys are `afi_auth`, `afi_cart` (localStorage). The `afi_` prefix is the project convention.

---

## 8. Quick Commands

```bash
# Backend (local)
cd backend
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements/local.txt
python manage.py migrate
python manage.py runserver

# Frontend (local)
cd frontend
npm install
npm run dev          # http://localhost:3000

# Full stack (Docker)
docker-compose up --build

# Deploy (from project root, Windows)
.\deploy-backend.ps1     # then ssh ubuntu@95.38.161.104
.\deploy-frontend.ps1    # then ssh ubuntu@95.38.161.205

# Production migrate bypass (emergency)
SKIP_MIGRATE=true docker compose up -d
```

---

*This file is the orientation doc. Keep it updated if the architecture changes materially.*

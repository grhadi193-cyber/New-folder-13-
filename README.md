# ATi Farzam Iranian — GPS Tracker Shop

E-commerce platform for GPS tracker devices.

## Stack

- **Backend:** Django 4.x, Django Ninja, PostgreSQL, Redis
- **Frontend:** Next.js 15, React, Tailwind CSS
- **Payments:** Zarinpal (Iranian payment gateway)
- **SMS:** Kavenegar

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL (or SQLite for quick start)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/local.txt
cp .env.example .env  # Edit with your values
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # Edit with your values
npm run dev
```

## Docker (Full Stack)

```bash
cp .env.example .env  # Edit with your values
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## Railway Deployment

### Backend Service

1. Create a new service on Railway
2. Connect your GitHub repo
3. Set root directory to `backend`
4. Railway will detect the `Dockerfile` and `railway.json`
5. Add environment variables from `.env.example`
6. Add a PostgreSQL database (Railway provides `DATABASE_URL` automatically)

### Frontend Service

1. Create another service on Railway
2. Connect your GitHub repo
3. Set root directory to `frontend`
4. Set environment variables:
   - `NEXT_PUBLIC_API_URL` = your backend Railway URL
   - `NEXT_PUBLIC_SITE_URL` = your frontend Railway URL

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key (32+ chars) | Yes |
| `DEBUG` | `False` for production | Yes |
| `TEST_MODE` | `False` for production | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes (auto on Railway) |
| `ALLOWED_HOSTS` | Comma-separated hostnames | Yes |
| `CORS_ALLOWED_ORIGINS` | Frontend URL for CORS | Yes |
| `FRONTEND_BASE_URL` | Frontend URL for payment redirects | Yes |
| `PAYMENT_CALLBACK_BASE_URL` | Backend callback URL | Yes |
| `KAVENEGAR_API_KEY` | Kavenegar SMS API key | For SMS |
| `ZARINPAL_MERCHANT_CODE` | Zarinpal merchant code | For payments |

## API Health Check

```
GET /api/health
→ {"status": "ok"}
```

## Project Structure

```
├── backend/
│   ├── config/          # Django settings, URLs, WSGI
│   ├── accounts/        # User auth (OTP, profiles)
│   ├── store/           # Products, orders, cart
│   ├── payment/         # Zarinpal integration
│   ├── shipping/        # Shipping methods
│   ├── blog/            # Blog posts
│   ├── notifications/   # Push/SMS notifications
│   ├── sms/             # Kavenegar SMS service
│   └── requirements/    # Pip requirements
├── frontend/
│   ├── src/
│   │   ├── app/         # Next.js App Router pages
│   │   ├── components/  # React components
│   │   ├── lib/         # Utilities, API, stores
│   │   └── styles/      # Global CSS
│   └── public/          # Static assets
├── docker-compose.yml
└── .env.example
```

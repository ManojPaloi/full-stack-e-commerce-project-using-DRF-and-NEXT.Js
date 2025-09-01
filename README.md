# Full‑Stack E‑Commerce – Django REST Framework + Next.js

> Production‑ready monorepo for a modern store: JWT auth, carts, checkout, orders, payments, admin, and more. Built with **Django REST Framework** (API) and **Next.js** (frontend) using clean architecture, type‑safe clients, and a beautiful UI.

<p align="center">
  <img src="https://raw.githubusercontent.com/ManojPaloi/full-stack-e-commerce-project-using-DRF-and-NEXT.Js/main/docs/cover.png" alt="Project cover" width="840"/>
</p>




<p align="center">
  <a href="#features"><img alt="features" src="https://img.shields.io/badge/feature‑rich-yes-brightgreen"></a>
  <a href="#tech-stack"><img alt="stack" src="https://img.shields.io/badge/stack-DRF%20%2B%20Next.js-blue"></a>
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-black"></a>
  <a href="#ci"><img alt="github actions" src="https://img.shields.io/badge/CI-GitHub%20Actions-%232088FF"></a>
</p>

## Live Demo

* **Frontend (Next.js)**: `https://your‑vercel‑domain.vercel.app`
* **API (DRF)**: `https://your‑backend-domain/api/`
* **API Docs (Swagger/Redoc)**: `/api/schema/swagger/` and `/api/schema/redoc/`

> Replace with your deployed links.

---

## Repository

📦 GitHub Repo: [ManojPaloi/full-stack-e-commerce-project-using-DRF-and-NEXT.Js](https://github.com/ManojPaloi/full-stack-e-commerce-project-using-DRF-and-NEXT.Js.git)

Clone the repository:

```bash
git clone https://github.com/ManojPaloi/full-stack-e-commerce-project-using-DRF-and-NEXT.Js.git
cd full-stack-e-commerce-project-using-DRF-and-NEXT.Js
```

---

## Table of Contents

* [Features](#features)
* [Architecture](#architecture)
* [Tech Stack](#tech-stack)
* [Project Structure](#project-structure)
* [Getting Started](#getting-started)

  * [Prerequisites](#prerequisites)
  * [Environment Variables](#environment-variables)
  * [Backend Setup (DRF)](#backend-setup-drf)
  * [Frontend Setup (Nextjs)](#frontend-setup-nextjs)
  * [Docker (one command)](#docker-one-command)
  * [Seeding Demo Data](#seeding-demo-data)
* [API Documentation](#api-documentation)
* [Payments](#payments)
* [Emails](#emails)
* [Caching & Background Jobs](#caching--background-jobs)
* [Security](#security)
* [Performance](#performance)
* [Accessibility & i18n](#accessibility--i18n)
* [Testing](#testing)
* [Linting & Formatting](#linting--formatting)
* [CI/CD](#ci)
* [Deployment](#deployment)
* [Troubleshooting](#troubleshooting)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)

---

## Features

**Core store**

* Product catalog (categories, variants/SKUs, inventory, images)
* Search, filters, sort, pagination
* Cart & wishlist (guest + authenticated users)
* Checkout with address & shipping, coupon codes
* Orders, order history, invoices
* Payment integration (Stripe) + webhooks

**Accounts & auth**

* JWT (access/refresh) with rotation & blacklist via `django‑rest‑framework‑simplejwt`
* Email/password login, password reset, email verification
* Admin roles (staff) & permissioned endpoints

**Operational excellence**

* Type‑safe API client generated from OpenAPI schema
* Robust error handling with problem details
* Celery workers for async tasks (emails, webhooks, reports)
* Redis for caching & rate limiting
* Ready‑to‑deploy Docker Compose (API, Web, DB, Redis, Worker, Nginx)

**Frontend polish**

* Next.js App Router + TypeScript
* Tailwind CSS + shadcn/ui + Lucide icons
* Responsive, accessible, fast (Core Web Vitals‑friendly)
* Optimistic UI for cart actions, skeleton loaders

---

## Architecture

```text
┌───────────────────────────── Monorepo Root ─────────────────────────────┐
│ .env, docker-compose.yml, Makefile, README.md                           │
│                                                                         │
│  apps/backend  (Django + DRF)             apps/frontend  (Next.js)      │
│  ────────────                              ─────────────                │
│  api, users, catalog, orders, payments     app/, components/, lib/      │
│  celery worker, Redis cache                shadcn/ui, hooks, store      │
│                                                                         │
│  Postgres  ─── Redis  ─── Celery Worker ── Nginx (reverse proxy)        │
│             │           └─ async emails, webhooks                        │
│             └─ DRF cache + rate limit                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

**Backend**: Python 3.12, Django 5, DRF, SimpleJWT, Postgres, Redis, Celery, drf‑spectacular, django‑storages

**Frontend**: Next.js 14/15 (App Router), TypeScript, Tailwind, shadcn/ui, React Query (TanStack), Zod, Axios/Fetch, Next Auth (optional)

**DevOps**: Docker, docker‑compose, Nginx, GitHub Actions, Vercel (FE), Render/Fly.io/AWS (BE)

---

## Project Structure

```bash
full-stack-e-commerce-project-using-DRF-and-NEXT.Js/
├── apps/
│   ├── backend/
│   │   ├── manage.py
│   │   ├── pyproject.toml
│   │   ├── drfcommerce/
│   │   │   ├── settings/
│   │   │   │   ├── base.py
│   │   │   │   ├── local.py
│   │   │   │   └── production.py
│   │   │   ├── urls.py
│   │   │   └── celery.py
│   │   ├── apps/
│   │   │   ├── users/
│   │   │   ├── catalog/
│   │   │   ├── cart/
│   │   │   ├── orders/
│   │   │   └── payments/
│   │   └── requirements.txt
│   └── frontend/
│       ├── package.json
│       ├── next.config.js
│       ├── app/
│       ├── components/
│       └── public/
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Getting Started

### Prerequisites

* **Node.js** ≥ 18, **pnpm** or **npm**
* **Python** ≥ 3.11 (3.12 recommended)
* **PostgreSQL** ≥ 14
* **Redis** ≥ 6
* **Stripe** account (test mode)
* **Docker** (optional but recommended)

### Environment Variables

Create a root `.env` for Docker Compose and per‑app env files.

**Backend (`apps/backend/.env`):**

```env
# Django
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=*

# Database
POSTGRES_DB=ecommerce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
ACCESS_TOKEN_LIFETIME_MIN=60
REFRESH_TOKEN_LIFETIME_DAYS=7
ROTATE_REFRESH_TOKENS=True
BLACKLIST_AFTER_ROTATION=True

# Email
DEFAULT_FROM_EMAIL=Store <no-reply@yourdomain.com>
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Storage (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=
```

**Frontend (`apps/frontend/.env.local`):**

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

> Tip: When deploying, set `DEBUG=False`, tighten `ALLOWED_HOSTS`, and configure a real email backend + object storage.

### Backend Setup (DRF)

```bash
cd apps/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

**Key endpoints**

* `POST /api/accounts/register/` – create account
* `POST /api/accounts/login/` – JWT (access, refresh)
* `POST /api/accounts/token/refresh/` – refresh access token
* `GET  /api/products/` – list products (filters: `?q=&category=&sort=`)
* `POST /api/cart/items/` – add to cart
* `POST /api/checkout/` – start checkout, create PaymentIntent
* `POST /api/stripe/webhook/` – handle Stripe webhooks

### Frontend Setup (Next.js)

```bash
cd apps/frontend
pnpm install       # or npm install / yarn
pnpm dev           # http://localhost:3000
```

**Frontend highlights**

* App Router with server actions for secure mutations
* `@tanstack/react-query` for data fetching & cache
* `zod` + forms with validation
* `shadcn/ui` components & Tailwind for a clean, accessible UI

### Docker (one command)

With Docker installed, from repo root:

```bash
cp .env.example .env   # if provided
docker compose up --build
```

This launches **Postgres**, **Redis**, **Backend**, **Frontend**, **Celery worker**, **Nginx**. Visit `http://localhost:3000` (web) and `http://localhost:8000/api/` (API).

### Seeding Demo Data

```bash
cd apps/backend
python manage.py loaddata fixtures/demo.json
# or
python manage.py seed_demo_store  # custom management command (products, categories, coupons)
```

---

## API Documentation

OpenAPI schema is generated with **drf‑spectacular**:

* JSON schema: `/api/schema/`
* Swagger UI: `/api/schema/swagger/`
* Redoc: `/api/schema/redoc/`

Use the schema to generate a **type‑safe client** for the frontend (e.g., `openapi-typescript`, `orval`).

---

## Payments

* **Stripe** Payment Intents flow
* Test cards: `4242 4242 4242 4242` any future date, any CVC
* Webhook endpoint: `/api/stripe/webhook/` – verify with `STRIPE_WEBHOOK_SECRET`

> Never trust amounts from the client. The API calculates totals server‑side from products, inventory, shipping and coupons.

---

## Emails

* Dev: console backend (prints to terminal)
* Prod: plug Mailgun/SendGrid/Resend and switch `EMAIL_BACKEND`
* Templates stored in `templates/emails/` and rendered by Celery tasks

---

## Caching & Background Jobs

* **Redis** cache for product lists, home page, and rate limiting
* **Celery** workers for sending emails, clearing stale carts, syncing inventory, processing webhooks

Run workers locally:

```bash
cd apps/backend
celery -A drfcommerce worker -l INFO
celery -A drfcommerce beat -l INFO
```

---

## Security

* HTTPS everywhere in production
* Secure cookies for SSR pages, CSRF for session views
* JWT rotation + blacklist, short‑lived access tokens
* Django `SECURE_*` settings (HSTS, referrer policy, content type nosniff)
* Strict CORS (restrict to your domains)
* Validate all inputs with DRF serializers/Zod

---

## Performance

* Postgres indexes for frequent filters/sorts
* DRF pagination, `select_related/prefetch_related`
* Redis caching for heavy endpoints
* Next.js image optimization, code splitting, RSC

---

## Accessibility & i18n

* Components meet WCAG AA (labels, focus states, keyboard nav)
* `next-intl` (or `@lingui`) ready for translations

---

## Testing

**Backend**

```bash
cd apps/backend
pytest -q
```

* Factories with `factory_boy`, API tests with `pytest-django`

**Frontend**

```bash
cd apps/frontend
pnpm test        # vitest / jest
pnpm test:e2e    # Playwright (optional)
```

---

## Linting & Formatting

* **Backend**: `ruff`, `black`, `mypy`
* **Frontend**: ESLint, TypeScript, Prettier

Run all:

```bash
make lint
make format
```

Set up **pre-commit** hooks:

```bash
pre-commit install
```

---

## CI/CD

* **GitHub Actions**: lint, test, build, docker
* Example workflow files in `.github/workflows/`
* Deploy: **Vercel** for Next.js, **Render/Fly.io/AWS** for Django API

Badges (replace with your repo):

```
[![CI](https://github.com/ManojPaloi/full-stack-e-commerce-project-using-DRF-and-NEXT.Js/actions/workflows/ci.yml/badge.svg)](https://github.com/ManojPaloi/full-stack-e-commerce-project-using-DRF-and-NEXT.Js/actions)
[![Deploy](https://github.com/ManojPaloi/full-stack-e-commerce-project-using-DRF-and-NEXT.Js/actions/workflows/deploy.yml/badge.svg)](https://github.com/ManojPaloi/full-stack-e-commerce-project-using-DRF-and-NEXT.Js/actions)
```

---

## Deployment

**Frontend (Vercel)**

* Import repo, set `NEXT_PUBLIC_API_BASE_URL` & `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`

**Backend (Render/Fly/AWS/Heroku)**

* Set env vars from `apps/backend/.env`
* Provision **Postgres** and **Redis** services
* Run `python manage.py migrate` on deploy
* Add **Stripe** webhook pointing to `/api/stripe/webhook/`
* Serve via **Gunicorn + Nginx** (see `docker/` configs)

**Object Storage (media)**

* Configure S3 compatible storage with `django-storages`

---

## Troubleshooting

* **401 Unauthorized**: Missing/expired JWT. Refresh token at `/api/accounts/token/refresh/`.
* **CORS errors**: Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL and `CSRF_TRUSTED_ORIGINS` is set.
* **Stripe webhook 400**: Verify `STRIPE_WEBHOOK_SECRET` and raw body handling is enabled in the Django view.
* **Images not loading**: Configure Next.js `images.domains` and S3 credentials in backend.

---

## Roadmap

* [ ] Admin dashboard (sales, inventory, analytics)
* [ ] Multi‑tenant stores / marketplaces
* [ ] Internationalization (prices per currency, tax)
* [ ] Advanced search (Elastic/Meilisearch)
* [ ] Subscriptions

---

## Contributing

1. Fork the repo and create a new branch from `main`
2. Write tests for your changes
3. Run `make lint && make test`
4. Open a PR with a clear description and screenshots

Please read our [CODE\_OF\_CONDUCT.md](CODE_OF_CONDUCT.md) and [CONTRIBUTING.md](CONTRIBUTING.md) (add these files in your repo).

---

## License

MIT © [Manoj Paloi](https://github.com/ManojPaloi)

---

## Screenshots

Add images under `apps/frontend/public/` or `docs/` and link them here:

| Home                       | PDP                       | Cart                       | Checkout                       |
| -------------------------- | ------------------------- | -------------------------- | ------------------------------ |
| ![](docs/screens/home.png) | ![](docs/screens/pdp.png) | ![](docs/screens/cart.png) | ![](docs/screens/checkout.png) |

---

### Maintainers

* \[Manoj Paloi]\([https://github.com](https://github.com)

# CoreInventory

**Enterprise Inventory Management Platform**  
A production-ready, full-stack inventory management system built with FastAPI, PostgreSQL, and React.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 · FastAPI · SQLAlchemy (async) · Alembic |
| Database | PostgreSQL 15 |
| Caching | Redis (optional, for dashboard TTL) |
| Authentication | JWT (HS256) · bcrypt |
| Frontend | React 18 · Vite · Axios · Recharts |
| Testing | pytest · pytest-asyncio · httpx · SQLite in-memory |

---

## Project Structure

```
CoreInventory/
├── backend/
│   ├── alembic/               # Database migrations
│   ├── auth/                  # JWT, hashing, RBAC dependencies
│   ├── middleware/            # Logging + global error handler
│   ├── models/                # SQLAlchemy ORM models (12 tables)
│   ├── routes/                # FastAPI routers (all /api/v1/*)
│   ├── schemas/               # Pydantic v2 request/response schemas
│   ├── services/              # Business logic layer
│   ├── tests/                 # pytest test suite (33 test cases)
│   ├── utils/                 # OTP helpers, pagination
│   ├── config.py              # Pydantic Settings from .env
│   ├── database.py            # Async SQLAlchemy engine
│   ├── main.py                # FastAPI app entry point
│   ├── schema.sql             # Raw PostgreSQL DDL (reference)
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios client (all endpoints)
│   │   ├── components/        # Sidebar, Navbar, DataTable, Modal, StatsCard
│   │   ├── context/           # AuthContext, NotificationContext
│   │   └── pages/             # 12 pages (Login → Dashboard → Operations)
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── .env.example
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

---

### 1. Clone & Configure

```bash
git clone https://github.com/DeathRay00/CoreInventory-.git
cd CoreInventory
cp .env.example .env
```

Edit `.env` with your real values:

```
DATABASE_URL=postgresql+asyncpg://youruser:yourpass@localhost:5432/coreinventory
JWT_SECRET_KEY=change-this-to-a-strong-random-secret
```

---

### 2. Set Up the Database

```sql
-- Run in psql as a superuser:
CREATE USER coreinventory WITH PASSWORD 'yourpass';
CREATE DATABASE coreinventory OWNER coreinventory;
```

---

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**

---

### 4. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

The web dashboard will be available at **http://localhost:3000**

---

## API Endpoints

All routes are versioned under `/api/v1/`.

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Create account |
| POST | `/auth/login` | Public | Get JWT token |
| GET | `/auth/me` | Any | Current user info |
| GET/POST | `/products` | Any/Manager | List / create products |
| PUT/DELETE | `/products/{id}` | Manager | Update / delete product |
| GET/POST | `/categories` | Any/Manager | List / create categories |
| GET/POST | `/warehouses` | Any/Manager | List / create warehouses |
| GET/POST | `/locations` | Any/Manager | List / create locations |
| GET/POST | `/receipts` | Any/Staff | List / create receipts |
| POST | `/receipts/{id}/validate` | Staff | Validate → adds stock |
| GET/POST | `/deliveries` | Any/Staff | List / create deliveries |
| POST | `/deliveries/{id}/validate` | Staff | Validate → deducts stock |
| GET/POST | `/transfers` | Any/Staff | List / execute transfers |
| GET/POST | `/adjustments` | Any/Staff | List / apply adjustments |
| GET | `/stock` | Any | Current stock levels |
| GET | `/ledger` | Manager | Immutable movement history |
| GET | `/dashboard` | Manager | Aggregated KPI metrics |
| GET | `/health` | Public | Service health check |

### Swagger UI (interactive docs)
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

---

## Standard Error Response

All errors return a consistent JSON envelope:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Product not found",
    "details": null
  }
}
```

| Code | HTTP Status |
|---|---|
| `INVALID_CREDENTIALS` | 401 |
| `UNAUTHORIZED` | 401 |
| `FORBIDDEN` | 403 |
| `RESOURCE_NOT_FOUND` | 404 |
| `VALIDATION_ERROR` | 400 / 422 |
| `INTERNAL_SERVER_ERROR` | 500 |

---

## Roles & Permissions

| Permission | Inventory Manager | Warehouse Staff |
|---|:---:|:---:|
| View dashboard | ✅ | ❌ |
| Manage products & categories | ✅ | ❌ |
| Manage warehouses & locations | ✅ | ❌ |
| View stock ledger | ✅ | ❌ |
| Create & validate receipts | ✅ | ✅ |
| Create & validate deliveries | ✅ | ✅ |
| Execute transfers | ✅ | ✅ |
| Apply adjustments | ✅ | ✅ |
| View stock levels | ✅ | ✅ |

---

## Running Tests

The test suite uses an **in-memory SQLite database** — no PostgreSQL required.

```bash
cd backend
pip install -r requirements.txt     # if not already installed

pytest -v
```

Expected output:

```
tests/test_auth.py         ·········   9 passed
tests/test_products.py     ·············  13 passed
tests/test_inventory.py    ···········  11 passed
=================== 33 passed in X.XXs ===================
```

---

## Environment Variables Reference

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async connection string | — |
| `JWT_SECRET_KEY` | Secret key for signing JWTs | — |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes | `60` |
| `SMTP_HOST` | SMTP server for OTP emails | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP login email | — |
| `SMTP_PASSWORD` | SMTP login password | — |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `RATE_LIMIT` | slowapi request limit | `100/minute` |

---

## Key Design Decisions

- **Async throughout** — SQLAlchemy `asyncpg` + `httpx` for zero-blocking I/O
- **Modular architecture** — routes → services → models with no cross-layer leakage
- **No negative stock** — `stock_service.upsert_stock()` raises 400 before any DB write
- **Immutable ledger** — `stock_ledger` rows are never updated or deleted
- **Background alerts** — FastAPI `BackgroundTasks` so alert creation never blocks the HTTP response
- **RBAC via dependency injection** — `require_role()` factory used as a FastAPI `Depends` parameter

---

## License

MIT — see [LICENSE](LICENSE)

# CoreInventory 🚀

**Enterprise Inventory Management Platform**  
A production-ready, full-stack inventory management system built to handle everything from stock tracking to multi-warehouse transfers.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 · Vite · HTML5/Vanilla CSS · Recharts (Dashboards) |
| **Backend**  | Python 3.11 · FastAPI · Pydantic v2 |
| **Database** | PostgreSQL 15 · SQLAlchemy (async) · Alembic (Migrations) |
| **Caching**  | Redis |
| **Auth**     | JWT (HS256) · bcrypt · SMTP OTP Verification |
| **Deploy**   | Docker Compose (Nginx for Frontend, Uvicorn for Backend) |

---

## 🌟 Features

* **Role-Based Access Control (RBAC)**: Distinct permissions for `Manager` and `Staff`.
* **Real-time Dashboard**: Track total stock, pending receipts/deliveries/transfers, out-of-stock items, and recent ledger history intuitively.
* **OTP Authentication**: Secure login flow with email OTP verification.
* **Warehouse Management**: Track inventory accurately across multiple physical storage locations.
* **Core Operations**: 
  - **Receipts**: Inbound logistics (adding stock).
  - **Deliveries**: Outbound logistics (deducting stock).
  - **Transfers**: Moving items between warehouses.
  - **Adjustments**: Manual stock overrides for audits / physical counts.
* **Immutable Ledger**: A permanent history of every single unit added, removed, or moved.
* **Automated Alerts**: Real-time notifications for Low Stock and Out of Stock triggers based on reorder thresholds.

---

## 🐳 Quick Start (Docker — Recommended)

The application is dockerized and ready to spin up with a single command. 

### Prerequisites
* Docker Desktop installed and running
* Git

### 1. Clone & Configure

```bash
git clone https://github.com/DeathRay00/CoreInventory-.git
cd CoreInventory
cp .env.example .env
```

Edit your `.env` file to provide real SMTP credentials for the OTP to work:
```env
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Start Services

Use Docker Compose to build and start the entire stack (PostgreSQL, Redis, Backend API, Frontend Nginx):

```bash
docker compose up --build -d
```

### 3. Seed Database with Sample Data

Once the containers are running and healthy, you can populate the database with sample products, warehouses, and users:

```bash
docker compose exec backend python seed_data.py
```

### 4. Access the Application

* **Frontend Web App**: [http://localhost:3000](http://localhost:3000)
* **Backend API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

**Sample Credentials** (Added by the seed script):
* **Manager**: `amal@company.com` / Password: `Admin@123`
* **Staff**: `priya@company.com` / Password: `Staff@123`

*(Note: In development, the OTP defaults to `000000` if the SMTP is not configured or fails to send, but in production, real OTPs are required).*

### Stopping Services
```bash
docker compose down
```

---

## 🏗️ Project Structure

```text
CoreInventory/
├── backend/
│   ├── alembic/               # Database migrations
│   ├── auth/                  # JWT logic, OTP service, RBAC
│   ├── models/                # SQLAlchemy ORM models
│   ├── routes/                # FastAPI endpoint routers (/api/v1/*)
│   ├── schemas/               # Pydantic v2 validation models
│   ├── services/              # Core business logic (ops, stock updates)
│   ├── database.py            # Async PostgreSQL connection logic
│   ├── seed_data.py           # Populates the DB with dummy data
│   └── main.py                # App entry point
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios API client functions
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route-level React views
│   │   └── App.jsx            # React Router & Layout
│   ├── index.css              # Custom styling / Dark theme implementation
│   └── vite.config.js
├── docker-compose.yml         # Container orchestration
└── .env                       # Environment configs
```

---

## 💻 Local Development (Without Docker)

If you prefer to run the application components individually:

### 1. Database & Redis
Ensure PostgreSQL and Redis are running on your local machine.

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS / Linux

pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Roles & Operations Matrix

| Operation | Inventory Manager | Warehouse Staff |
|---|:---:|:---:|
| View Dashboard & KPIs | ✅ | ❌ |
| Add/Edit Products | ✅ | ❌ |
| Setup Warehouses | ✅ | ❌ |
| View Ledger History | ✅ | ❌ |
| Create & Validate Receipts | ✅ | ✅ |
| Create & Validate Deliveries | ✅ | ✅ |
| Execute Stock Transfers | ✅ | ✅ |
| View Stock Levels | ✅ | ✅ |

---

## 📝 License
MIT License

import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import engine, Base
from middleware import (
    LoggingMiddleware,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# Import routes
from routes import auth, products, warehouses
from routes.receipts import router as receipts_router
from routes.deliveries import router as deliveries_router
from routes.operations import router as operations_router
from routes.stock import router as stock_router
from routes.dashboard import router as dashboard_router


# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger("coreinventory")

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ── App lifespan ──────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('{"event": "startup", "message": "CoreInventory API starting"}')
    # Tables are managed by Alembic; this is just a safety net in dev
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    logger.info('{"event": "shutdown", "message": "CoreInventory API stopped"}')


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="CoreInventory API",
    description="Enterprise Inventory Management Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Rate limiter state ────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Custom middleware ─────────────────────────────────────────────────────────
app.add_middleware(LoggingMiddleware)

# ── Global exception handlers ─────────────────────────────────────────────────
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router,       prefix=API_PREFIX)
app.include_router(products.router,   prefix=API_PREFIX)
app.include_router(warehouses.router, prefix=API_PREFIX)
app.include_router(receipts_router,   prefix=API_PREFIX)
app.include_router(deliveries_router, prefix=API_PREFIX)
app.include_router(operations_router, prefix=API_PREFIX)
app.include_router(stock_router,      prefix=API_PREFIX)
app.include_router(dashboard_router,  prefix=API_PREFIX)



# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    from sqlalchemy import text
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "database": db_status, "version": "1.0.0"}

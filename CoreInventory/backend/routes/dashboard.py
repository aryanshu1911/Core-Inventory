from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from database import get_db
from models.stock import Stock
from models.product import Product
from models.receipt import Receipt
from models.delivery import Delivery
from models.transfer import Transfer
from models.alert import Alert
from schemas.inventory import DashboardOut
from auth.dependencies import require_role

router = APIRouter(tags=["Dashboard"])
ManagerDep = Depends(require_role("inventory_manager"))


@router.get("/dashboard", response_model=DashboardOut, dependencies=[ManagerDep])
async def get_dashboard(db: Annotated[AsyncSession, Depends(get_db)]):
    # Total distinct products in stock (qty > 0)
    total_prods = await db.execute(
        select(func.count(distinct(Stock.product_id))).where(Stock.quantity > 0)
    )
    total_products = total_prods.scalar() or 0

    # Total units across all stock
    total_units = await db.execute(select(func.coalesce(func.sum(Stock.quantity), 0)))
    total_stock_value = total_units.scalar() or 0

    # Low stock: stock qty > 0 but <= product reorder_level
    low_stock = await db.execute(
        select(func.count()).select_from(Stock).join(Product, Product.id == Stock.product_id).where(
            Stock.quantity > 0, Stock.quantity <= Product.reorder_level
        )
    )
    low_stock_count = low_stock.scalar() or 0

    # Out of stock: stock qty = 0 or no record
    out_of_stock = await db.execute(
        select(func.count()).select_from(Stock).where(Stock.quantity == 0)
    )
    out_of_stock_count = out_of_stock.scalar() or 0

    # Pending receipts (draft)
    pending_receipts_q = await db.execute(
        select(func.count()).select_from(Receipt).where(Receipt.status == "draft")
    )
    pending_receipts = pending_receipts_q.scalar() or 0

    # Pending deliveries (draft or packed)
    pending_deliveries_q = await db.execute(
        select(func.count()).select_from(Delivery).where(Delivery.status.in_(["draft", "packed"]))
    )
    pending_deliveries = pending_deliveries_q.scalar() or 0

    # Pending transfers
    pending_transfers_q = await db.execute(
        select(func.count()).select_from(Transfer).where(Transfer.status == "pending")
    )
    pending_transfers = pending_transfers_q.scalar() or 0

    # Active unresolved alerts
    active_alerts_q = await db.execute(
        select(func.count()).select_from(Alert).where(Alert.is_resolved == False)  # noqa: E712
    )
    active_alerts = active_alerts_q.scalar() or 0

    return DashboardOut(
        total_products=total_products,
        total_stock_value=total_stock_value,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        pending_receipts=pending_receipts,
        pending_deliveries=pending_deliveries,
        pending_transfers=pending_transfers,
        active_alerts=active_alerts,
    )

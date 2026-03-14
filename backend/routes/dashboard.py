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
    # Total products in system
    all_prods = await db.execute(select(func.count(Product.id)))
    num_total_products = all_prods.scalar() or 0

    # Products with any stock > 0
    in_stock_sub = select(Stock.product_id).where(Stock.quantity > 0).distinct()
    in_stock_q = await db.execute(select(func.count()).select_from(in_stock_sub.subquery()))
    num_in_stock = in_stock_q.scalar() or 0

    # Total units across all stock
    total_units = await db.execute(select(func.coalesce(func.sum(Stock.quantity), 0)))
    total_stock_value = total_units.scalar() or 0

    # Low stock: product whose TOTAL qty across all warehouses is > 0 and <= reorder_level
    # Or more simply, count products that have at least one warehouse where it is low stock
    low_stock_sub = (
        select(Stock.product_id)
        .join(Product, Product.id == Stock.product_id)
        .where(Stock.quantity > 0, Stock.quantity <= Product.reorder_level)
        .distinct()
    )
    low_stock_q = await db.execute(select(func.count()).select_from(low_stock_sub.subquery()))
    low_stock_count = low_stock_q.scalar() or 0

    # Out of stock count
    out_of_stock_count = num_total_products - num_in_stock

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
        total_products=num_total_products,
        total_stock_value=total_stock_value,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        pending_receipts=pending_receipts,
        pending_deliveries=pending_deliveries,
        pending_transfers=pending_transfers,
        active_alerts=active_alerts,
    )

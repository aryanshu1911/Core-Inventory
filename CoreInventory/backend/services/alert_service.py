import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.alert import Alert
from models.product import Product
from models.stock import Stock


async def check_and_create_alert(
    db: AsyncSession,
    product_id: uuid.UUID,
    warehouse_id: uuid.UUID,
) -> Alert | None:
    # Get current stock quantity
    stock_result = await db.execute(
        select(Stock.quantity).where(
            Stock.product_id == product_id,
            Stock.warehouse_id == warehouse_id,
        )
    )
    current_qty = stock_result.scalar_one_or_none() or 0

    # Get product reorder level
    prod_result = await db.execute(select(Product.reorder_level).where(Product.id == product_id))
    reorder_level = prod_result.scalar_one_or_none() or 0

    if current_qty <= reorder_level:
        # Check for existing unresolved alert
        existing = await db.execute(
            select(Alert).where(
                Alert.product_id == product_id,
                Alert.warehouse_id == warehouse_id,
                Alert.is_resolved == False,  # noqa: E712
            )
        )
        if not existing.scalar_one_or_none():
            alert = Alert(
                product_id=product_id,
                warehouse_id=warehouse_id,
                current_stock=current_qty,
                reorder_level=reorder_level,
            )
            db.add(alert)
            await db.flush()
            return alert
    return None

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.stock import Stock
from fastapi import HTTPException


async def get_stock_quantity(db: AsyncSession, product_id: uuid.UUID, warehouse_id: uuid.UUID) -> int:
    result = await db.execute(
        select(Stock.quantity).where(Stock.product_id == product_id, Stock.warehouse_id == warehouse_id)
    )
    qty = result.scalar_one_or_none()
    return qty or 0


async def upsert_stock(
    db: AsyncSession,
    product_id: uuid.UUID,
    warehouse_id: uuid.UUID,
    quantity_delta: int,
    location_id: uuid.UUID | None = None,
) -> Stock:
    result = await db.execute(
        select(Stock).where(Stock.product_id == product_id, Stock.warehouse_id == warehouse_id)
    )
    stock = result.scalar_one_or_none()

    if stock:
        new_qty = stock.quantity + quantity_delta
        if new_qty < 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": f"Insufficient stock. Available: {stock.quantity}, requested: {abs(quantity_delta)}",
                    "details": None,
                },
            )
        stock.quantity = new_qty
    else:
        if quantity_delta < 0:
            raise HTTPException(
                status_code=400,
                detail={"code": "VALIDATION_ERROR", "message": "No stock record exists to deduct from", "details": None},
            )
        stock = Stock(
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            quantity=quantity_delta,
        )
        db.add(stock)

    await db.flush()
    return stock

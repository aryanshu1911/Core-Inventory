import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.product import CategoryCreate, CategoryOut, ProductCreate, ProductUpdate, ProductOut
from services.product_service import (
    create_category, list_categories,
    create_product, list_products, get_product, update_product, delete_product,
)
from auth.dependencies import get_current_user, require_role
from models.user import User

router = APIRouter(tags=["Products & Categories"])
ManagerDep = Depends(require_role("inventory_manager"))
AnyDep = Depends(require_role("inventory_manager", "warehouse_staff"))


# ── Categories ────────────────────────────────────────────────────────────────

@router.post("/categories", response_model=CategoryOut, status_code=201, dependencies=[ManagerDep])
async def create_cat(data: CategoryCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await create_category(db, data)


@router.get("/categories", response_model=list[CategoryOut], dependencies=[AnyDep])
async def get_cats(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await list_categories(db, limit, offset)


# ── Products ──────────────────────────────────────────────────────────────────

@router.post("/products", response_model=ProductOut, status_code=201, dependencies=[ManagerDep])
async def create_prod(data: ProductCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await create_product(db, data)


@router.get("/products", response_model=list[ProductOut], dependencies=[AnyDep])
async def get_prods(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Optional[str] = Query(None),
    category_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await list_products(db, search, category_id, limit, offset)


@router.get("/products/{product_id}", response_model=ProductOut, dependencies=[AnyDep])
async def get_prod(product_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_product(db, product_id)


@router.put("/products/{product_id}", response_model=ProductOut, dependencies=[ManagerDep])
async def update_prod(product_id: uuid.UUID, data: ProductUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await update_product(db, product_id, data)


@router.delete("/products/{product_id}", status_code=204, dependencies=[ManagerDep])
async def delete_prod(product_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    await delete_product(db, product_id)

import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.warehouse import WarehouseCreate, WarehouseOut, LocationCreate, LocationOut
from services.warehouse_service import (
    create_warehouse, list_warehouses, get_warehouse,
    create_location, list_locations,
)
from auth.dependencies import require_role

router = APIRouter(tags=["Warehouses & Locations"])
ManagerDep = Depends(require_role("inventory_manager"))
AnyDep = Depends(require_role("inventory_manager", "warehouse_staff"))


@router.post("/warehouses", response_model=WarehouseOut, status_code=201, dependencies=[ManagerDep])
async def create_wh(data: WarehouseCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await create_warehouse(db, data)


@router.get("/warehouses", response_model=list[WarehouseOut], dependencies=[AnyDep])
async def list_wh(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await list_warehouses(db, limit, offset)


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseOut, dependencies=[AnyDep])
async def get_wh(warehouse_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_warehouse(db, warehouse_id)


@router.post("/locations", response_model=LocationOut, status_code=201, dependencies=[ManagerDep])
async def create_loc(data: LocationCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await create_location(db, data)


@router.get("/locations", response_model=list[LocationOut], dependencies=[AnyDep])
async def list_locs(
    db: Annotated[AsyncSession, Depends(get_db)],
    warehouse_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await list_locations(db, warehouse_id, limit, offset)

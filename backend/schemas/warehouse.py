import uuid
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class WarehouseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    address: Optional[str] = None


class WarehouseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    address: Optional[str] = None


class LocationCreate(BaseModel):
    warehouse_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=150)
    rack_code: Optional[str] = Field(None, max_length=50)


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    warehouse_id: uuid.UUID
    name: str
    rack_code: Optional[str] = None

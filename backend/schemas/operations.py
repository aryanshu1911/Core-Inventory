import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReceiptItemCreate(BaseModel):
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class ReceiptCreate(BaseModel):
    supplier: str = Field(..., min_length=1, max_length=255)
    items: List[ReceiptItemCreate]


class ReceiptItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity: int


class ReceiptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    supplier: str
    status: str
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    items: List[ReceiptItemOut] = []


class DeliveryItemCreate(BaseModel):
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class DeliveryCreate(BaseModel):
    customer: str = Field(..., min_length=1, max_length=255)
    items: List[DeliveryItemCreate]


class DeliveryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity: int


class DeliveryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer: str
    status: str
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    items: List[DeliveryItemOut] = []

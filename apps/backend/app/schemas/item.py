from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ItemCategory(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    furniture = "furniture"
    vehicles = "vehicles"
    sports = "sports"
    books = "books"
    other = "other"


class ItemTag(str, Enum):
    new = "new"
    used = "used"
    refurbished = "refurbished"
    negotiable = "negotiable"
    urgent = "urgent"
    bundle = "bundle"


class ItemStatus(str, Enum):
    available = "available"
    on_hold = "on_hold"
    sold = "sold"


class ItemCreate(BaseModel):
    title: str = Field(max_length=120)
    description: str = Field(max_length=2000)
    category: ItemCategory
    tags: list[ItemTag] = []
    seller_id: UUID  # replaced by auth token once auth is implemented


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    category: ItemCategory | None = None
    tags: list[ItemTag] | None = None


class ItemResponse(BaseModel):
    id: UUID
    title: str
    description: str
    category: ItemCategory
    status: ItemStatus
    tags: list[ItemTag]
    seller_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItemSummary(BaseModel):
    id: UUID
    title: str
    category: ItemCategory
    status: ItemStatus
    tags: list[ItemTag]
    seller_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    items: list[ItemSummary]
    total: int
    page: int
    limit: int

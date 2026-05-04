from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.item import ItemStatus


class HoldCreate(BaseModel):
    buyer_id: UUID  # replaced by auth token once auth is implemented


class SellerContact(BaseModel):
    seller_id: UUID
    display_name: str
    email: str


class HoldResponse(BaseModel):
    id: UUID
    item_id: UUID
    held_by: UUID
    held_at: datetime
    buyer_confirmed: bool
    seller_confirmed: bool
    buyer_confirmed_at: datetime | None
    seller_confirmed_at: datetime | None
    seller_contact: SellerContact | None = None

    model_config = {"from_attributes": True}


class ConfirmRequest(BaseModel):
    confirmer_id: UUID  # replaced by auth token once auth is implemented


class HoldReleaseResponse(BaseModel):
    item_id: UUID
    status: ItemStatus


class ConfirmResponse(BaseModel):
    item_id: UUID
    confirmed_by: str  # "buyer" | "seller"
    buyer_confirmed: bool
    seller_confirmed: bool
    status: ItemStatus

import uuid
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from app.schemas.hold import HoldResponse
from app.schemas.item import ItemCreate, ItemResponse, ItemStatus, ItemUpdate


class InMemoryItemRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, ItemResponse] = {}

    async def create(self, data: ItemCreate) -> ItemResponse:
        now = datetime.now(timezone.utc)
        item = ItemResponse(
            id=uuid.uuid4(),
            title=data.title,
            description=data.description,
            category=data.category,
            status=ItemStatus.available,
            tags=data.tags,
            seller_id=data.seller_id,
            created_at=now,
            updated_at=now,
        )
        self._store[item.id] = item
        return deepcopy(item)

    async def get_by_id(self, item_id: UUID) -> ItemResponse | None:
        item = self._store.get(item_id)
        return deepcopy(item) if item else None

    async def update(self, item_id: UUID, data: ItemUpdate) -> ItemResponse | None:
        item = self._store.get(item_id)
        if not item:
            return None
        patch = data.model_dump(exclude_none=True)
        updated = item.model_copy(
            update={**patch, "updated_at": datetime.now(timezone.utc)}
        )
        self._store[item_id] = updated
        return deepcopy(updated)

    async def delete(self, item_id: UUID) -> bool:
        return self._store.pop(item_id, None) is not None

    async def update_status(
        self, item_id: UUID, status: ItemStatus
    ) -> ItemResponse | None:
        item = self._store.get(item_id)
        if not item:
            return None
        updated = item.model_copy(
            update={"status": status, "updated_at": datetime.now(timezone.utc)}
        )
        self._store[item_id] = updated
        return deepcopy(updated)


class InMemoryHoldRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, HoldResponse] = {}  # keyed by item_id

    async def create(self, item_id: UUID, buyer_id: UUID) -> HoldResponse:
        hold = HoldResponse(
            id=uuid.uuid4(),
            item_id=item_id,
            held_by=buyer_id,
            held_at=datetime.now(timezone.utc),
            buyer_confirmed=False,
            seller_confirmed=False,
            buyer_confirmed_at=None,
            seller_confirmed_at=None,
        )
        self._store[item_id] = hold
        return deepcopy(hold)

    async def get_by_item_id(self, item_id: UUID) -> HoldResponse | None:
        hold = self._store.get(item_id)
        return deepcopy(hold) if hold else None

    async def confirm(self, item_id: UUID, role: str) -> HoldResponse:
        hold = self._store[item_id]
        now = datetime.now(timezone.utc)
        if role == "buyer":
            updated = hold.model_copy(
                update={"buyer_confirmed": True, "buyer_confirmed_at": now}
            )
        else:
            updated = hold.model_copy(
                update={"seller_confirmed": True, "seller_confirmed_at": now}
            )
        self._store[item_id] = updated
        return deepcopy(updated)

    async def release(self, item_id: UUID) -> bool:
        return self._store.pop(item_id, None) is not None

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hold import Hold
from app.models.item import Item
from app.schemas.hold import HoldResponse
from app.schemas.item import ItemCreate, ItemResponse, ItemStatus, ItemUpdate


class PostgresItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: ItemCreate) -> ItemResponse:
        item = Item(
            title=data.title,
            description=data.description,
            category=data.category.value,
            tags=[t.value for t in data.tags],
            seller_id=data.seller_id,
        )
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return ItemResponse.model_validate(item)

    async def get_by_id(self, item_id: UUID) -> ItemResponse | None:
        result = await self._session.get(Item, item_id)
        return ItemResponse.model_validate(result) if result else None

    async def update(self, item_id: UUID, data: ItemUpdate) -> ItemResponse | None:
        item = await self._session.get(Item, item_id)
        if not item:
            return None
        patch = data.model_dump(exclude_none=True)
        for key, value in patch.items():
            if key == "tags":
                setattr(item, key, [t.value for t in value])
            elif key == "category":
                setattr(item, key, value.value)
            else:
                setattr(item, key, value)
        item.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(item)
        return ItemResponse.model_validate(item)

    async def delete(self, item_id: UUID) -> bool:
        item = await self._session.get(Item, item_id)
        if not item:
            return False
        await self._session.delete(item)
        await self._session.commit()
        return True

    async def update_status(
        self, item_id: UUID, status: ItemStatus
    ) -> ItemResponse | None:
        item = await self._session.get(Item, item_id)
        if not item:
            return None
        item.status = status.value
        item.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(item)
        return ItemResponse.model_validate(item)


class PostgresHoldRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, item_id: UUID, buyer_id: UUID) -> HoldResponse:
        hold = Hold(item_id=item_id, held_by=buyer_id)
        self._session.add(hold)
        await self._session.commit()
        await self._session.refresh(hold)
        return HoldResponse.model_validate(hold)

    async def get_by_item_id(self, item_id: UUID) -> HoldResponse | None:
        result = await self._session.execute(
            select(Hold).where(Hold.item_id == item_id)
        )
        hold = result.scalar_one_or_none()
        return HoldResponse.model_validate(hold) if hold else None

    async def confirm(self, item_id: UUID, role: str) -> HoldResponse:
        result = await self._session.execute(
            select(Hold).where(Hold.item_id == item_id)
        )
        hold = result.scalar_one()
        now = datetime.now(timezone.utc)
        if role == "buyer":
            hold.buyer_confirmed = True
            hold.buyer_confirmed_at = now
        else:
            hold.seller_confirmed = True
            hold.seller_confirmed_at = now
        await self._session.commit()
        await self._session.refresh(hold)
        return HoldResponse.model_validate(hold)

    async def release(self, item_id: UUID) -> bool:
        result = await self._session.execute(
            select(Hold).where(Hold.item_id == item_id)
        )
        hold = result.scalar_one_or_none()
        if not hold:
            return False
        await self._session.delete(hold)
        await self._session.commit()
        return True

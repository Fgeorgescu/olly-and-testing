import uuid

import pytest

from app.repositories.postgres import PostgresHoldRepository, PostgresItemRepository
from app.schemas.item import ItemCategory, ItemCreate, ItemStatus, ItemTag, ItemUpdate


def _item(title, description, category, tags=None):
    return ItemCreate(
        title=title,
        description=description,
        category=category,
        tags=tags or [],
    )


@pytest.mark.integration
async def test_create_and_get_item(db_session):
    repo = PostgresItemRepository(db_session)
    data = _item(
        "Keyboard",
        "Mechanical",
        ItemCategory.electronics,
        tags=[ItemTag.used, ItemTag.negotiable],
    )
    created = await repo.create(data, uuid.uuid4())
    assert created.id is not None
    assert created.status == ItemStatus.available

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.title == "Keyboard"
    assert ItemTag.used in fetched.tags


@pytest.mark.integration
async def test_update_item(db_session):
    repo = PostgresItemRepository(db_session)
    item = await repo.create(_item("Monitor", "4K", ItemCategory.electronics), uuid.uuid4())
    updated = await repo.update(item.id, ItemUpdate(title="4K Monitor"))
    assert updated.title == "4K Monitor"


@pytest.mark.integration
async def test_update_status(db_session):
    repo = PostgresItemRepository(db_session)
    item = await repo.create(_item("Desk", "Wooden", ItemCategory.furniture), uuid.uuid4())
    updated = await repo.update_status(item.id, ItemStatus.on_hold)
    assert updated.status == ItemStatus.on_hold


@pytest.mark.integration
async def test_delete_item(db_session):
    repo = PostgresItemRepository(db_session)
    item = await repo.create(_item("Lamp", "LED", ItemCategory.furniture), uuid.uuid4())
    deleted = await repo.delete(item.id)
    assert deleted is True
    assert await repo.get_by_id(item.id) is None


@pytest.mark.integration
async def test_hold_lifecycle(db_session):
    item_repo = PostgresItemRepository(db_session)
    hold_repo = PostgresHoldRepository(db_session)

    item = await item_repo.create(_item("Sofa", "Comfy", ItemCategory.furniture), uuid.uuid4())
    buyer = uuid.uuid4()

    hold = await hold_repo.create(item.id, buyer)
    assert hold.held_by == buyer
    assert not hold.buyer_confirmed

    confirmed = await hold_repo.confirm(item.id, "buyer")
    assert confirmed.buyer_confirmed
    assert not confirmed.seller_confirmed

    released = await hold_repo.release(item.id)
    assert released is True
    assert await hold_repo.get_by_item_id(item.id) is None

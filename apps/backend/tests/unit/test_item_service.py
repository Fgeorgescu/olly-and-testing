import uuid

import pytest

from app.schemas.item import ItemCategory, ItemCreate, ItemStatus, ItemTag, ItemUpdate


@pytest.mark.unit
async def test_create_item(item_service):
    data = ItemCreate(
        title="Laptop",
        description="Good condition",
        category=ItemCategory.electronics,
        tags=[ItemTag.used],
    )
    item = await item_service.create(data, uuid.uuid4())
    assert item.title == "Laptop"
    assert item.status == ItemStatus.available


@pytest.mark.unit
async def test_get_item(item_service):
    seller = uuid.uuid4()
    created = await item_service.create(
        ItemCreate(title="Book", description="Novel", category=ItemCategory.books),
        seller,
    )
    fetched = await item_service.get(created.id)
    assert fetched.id == created.id


@pytest.mark.unit
async def test_get_item_not_found(item_service):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await item_service.get(uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.unit
async def test_update_item(item_service):
    seller = uuid.uuid4()
    item = await item_service.create(
        ItemCreate(title="Chair", description="Wooden", category=ItemCategory.furniture),
        seller,
    )
    updated = await item_service.update(item.id, ItemUpdate(title="Oak Chair"), seller)
    assert updated.title == "Oak Chair"


@pytest.mark.unit
async def test_update_item_wrong_owner(item_service):
    from fastapi import HTTPException

    seller = uuid.uuid4()
    item = await item_service.create(
        ItemCreate(title="Chair", description="Wooden", category=ItemCategory.furniture),
        seller,
    )
    with pytest.raises(HTTPException) as exc:
        await item_service.update(item.id, ItemUpdate(title="X"), uuid.uuid4())
    assert exc.value.status_code == 403


@pytest.mark.unit
async def test_delete_on_hold_rejected(item_service, hold_service):
    from fastapi import HTTPException

    seller = uuid.uuid4()
    buyer = uuid.uuid4()
    item = await item_service.create(
        ItemCreate(title="Bike", description="Fast", category=ItemCategory.sports),
        seller,
    )
    await hold_service.place_hold(item.id, buyer)

    with pytest.raises(HTTPException) as exc:
        await item_service.delete(item.id, seller)
    assert exc.value.status_code == 409

import uuid

import pytest
from fastapi import HTTPException

from app.schemas.item import ItemCategory, ItemCreate, ItemStatus


async def _item(item_service, seller=None):
    return await item_service.create(
        ItemCreate(title="Sofa", description="Comfy", category=ItemCategory.furniture),
        seller or uuid.uuid4(),
    )


@pytest.mark.unit
async def test_place_hold(item_service, hold_service):
    seller = uuid.uuid4()
    buyer = uuid.uuid4()
    item = await _item(item_service, seller)

    hold = await hold_service.place_hold(item.id, buyer)
    assert hold.held_by == buyer
    assert hold.seller_contact is not None

    refreshed = await item_service.get(item.id)
    assert refreshed.status == ItemStatus.on_hold


@pytest.mark.unit
async def test_cannot_hold_own_listing(item_service, hold_service):
    seller = uuid.uuid4()
    item = await _item(item_service, seller)
    with pytest.raises(HTTPException) as exc:
        await hold_service.place_hold(item.id, seller)
    assert exc.value.status_code == 409


@pytest.mark.unit
async def test_cannot_double_hold(item_service, hold_service):
    seller = uuid.uuid4()
    item = await _item(item_service, seller)
    await hold_service.place_hold(item.id, uuid.uuid4())
    with pytest.raises(HTTPException) as exc:
        await hold_service.place_hold(item.id, uuid.uuid4())
    assert exc.value.status_code == 409


@pytest.mark.unit
async def test_release_hold_by_buyer(item_service, hold_service):
    seller = uuid.uuid4()
    buyer = uuid.uuid4()
    item = await _item(item_service, seller)
    await hold_service.place_hold(item.id, buyer)

    result = await hold_service.release(item.id, buyer)
    assert result.status == ItemStatus.available


@pytest.mark.unit
async def test_release_hold_by_seller(item_service, hold_service):
    seller = uuid.uuid4()
    buyer = uuid.uuid4()
    item = await _item(item_service, seller)
    await hold_service.place_hold(item.id, buyer)

    result = await hold_service.release(item.id, seller)
    assert result.status == ItemStatus.available


@pytest.mark.unit
async def test_mutual_confirm_marks_sold(item_service, hold_service):
    seller = uuid.uuid4()
    buyer = uuid.uuid4()
    item = await _item(item_service, seller)
    await hold_service.place_hold(item.id, buyer)

    r1 = await hold_service.confirm(item.id, buyer)
    assert r1.status == ItemStatus.on_hold  # one side not enough

    r2 = await hold_service.confirm(item.id, seller)
    assert r2.status == ItemStatus.sold


@pytest.mark.unit
async def test_double_confirm_rejected(item_service, hold_service):
    seller = uuid.uuid4()
    buyer = uuid.uuid4()
    item = await _item(item_service, seller)
    await hold_service.place_hold(item.id, buyer)
    await hold_service.confirm(item.id, buyer)

    with pytest.raises(HTTPException) as exc:
        await hold_service.confirm(item.id, buyer)
    assert exc.value.status_code == 409


@pytest.mark.unit
async def test_third_party_cannot_confirm(item_service, hold_service):
    seller = uuid.uuid4()
    buyer = uuid.uuid4()
    item = await _item(item_service, seller)
    await hold_service.place_hold(item.id, buyer)

    with pytest.raises(HTTPException) as exc:
        await hold_service.confirm(item.id, uuid.uuid4())
    assert exc.value.status_code == 403

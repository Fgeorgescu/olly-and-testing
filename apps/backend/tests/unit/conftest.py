import pytest

from app.repositories.memory import InMemoryHoldRepository, InMemoryItemRepository
from app.services.hold_service import HoldService
from app.services.item_service import ItemService


@pytest.fixture
def item_repo():
    return InMemoryItemRepository()


@pytest.fixture
def hold_repo():
    return InMemoryHoldRepository()


@pytest.fixture
def item_service(item_repo):
    return ItemService(item_repo)


@pytest.fixture
def hold_service(item_repo, hold_repo):
    return HoldService(item_repo, hold_repo)

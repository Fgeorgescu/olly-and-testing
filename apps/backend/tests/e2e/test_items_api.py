import pytest


@pytest.mark.e2e
async def test_create_and_get_item(client):
    resp = await client.post(
        "/api/v1/items",
        json={
            "title": "Camera",
            "description": "DSLR, great condition",
            "category": "electronics",
            "tags": ["used"],
        },
    )
    assert resp.status_code == 201
    item = resp.json()
    assert item["status"] == "available"

    get_resp = await client.get(f"/api/v1/items/{item['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Camera"


@pytest.mark.e2e
async def test_search_returns_item(client):
    await client.post(
        "/api/v1/items",
        json={
            "title": "Vintage Lamp",
            "description": "Art deco style",
            "category": "furniture",
            "tags": [],
        },
    )
    resp = await client.get("/api/v1/items?q=vintage")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any("Vintage" in i["title"] for i in data["items"])


@pytest.mark.e2e
async def test_hold_and_dual_confirm(client):
    buyer = "00000000-0000-0000-0000-000000000002"

    create = await client.post(
        "/api/v1/items",
        json={"title": "Guitar", "description": "Acoustic", "category": "other", "tags": []},
    )
    item_id = create.json()["id"]
    seller = create.json()["seller_id"]  # set by the server (current user)

    hold = await client.post(f"/api/v1/items/{item_id}/hold", json={"buyer_id": buyer})
    assert hold.status_code == 201
    assert hold.json()["seller_contact"] is not None

    r1 = await client.post(
        f"/api/v1/items/{item_id}/confirm", json={"confirmer_id": buyer}
    )
    assert r1.json()["status"] == "on_hold"

    r2 = await client.post(
        f"/api/v1/items/{item_id}/confirm", json={"confirmer_id": seller}
    )
    assert r2.json()["status"] == "sold"


@pytest.mark.e2e
async def test_release_hold(client):
    buyer = "00000000-0000-0000-0000-000000000002"

    create = await client.post(
        "/api/v1/items",
        json={"title": "Scooter", "description": "Electric", "category": "vehicles", "tags": []},
    )
    item_id = create.json()["id"]

    await client.post(f"/api/v1/items/{item_id}/hold", json={"buyer_id": buyer})
    release = await client.delete(f"/api/v1/items/{item_id}/hold?caller_id={buyer}")
    assert release.status_code == 200
    assert release.json()["status"] == "available"

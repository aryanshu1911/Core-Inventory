"""
Tests for product and category endpoints:
  POST   /api/v1/categories
  GET    /api/v1/categories
  POST   /api/v1/products
  GET    /api/v1/products
  GET    /api/v1/products/{id}
  PUT    /api/v1/products/{id}
  DELETE /api/v1/products/{id}
"""
import pytest
from tests.conftest import auth


@pytest.fixture
async def category(client, manager_token):
    """Create a test category and return its data."""
    res = await client.post("/api/v1/categories", json={"name": "Electronics", "description": "Electronic goods"}, headers=auth(manager_token))
    assert res.status_code == 201
    return res.json()


@pytest.fixture
async def product(client, manager_token, category):
    """Create a test product and return its data."""
    res = await client.post("/api/v1/products", json={
        "name": "Laptop Pro", "sku": "LAP-001",
        "unit_of_measure": "pcs", "reorder_level": 5,
        "category_id": category["id"],
    }, headers=auth(manager_token))
    assert res.status_code == 201
    return res.json()


@pytest.mark.asyncio
class TestCategories:
    async def test_create_category(self, client, manager_token):
        res = await client.post("/api/v1/categories", json={"name": "Office Supplies"}, headers=auth(manager_token))
        assert res.status_code == 201
        assert res.json()["name"] == "Office Supplies"

    async def test_create_category_unauthorized(self, client):
        res = await client.post("/api/v1/categories", json={"name": "Unauthorized"})
        assert res.status_code == 401

    async def test_staff_cannot_create_category(self, client, staff_token):
        res = await client.post("/api/v1/categories", json={"name": "Staff Cat"}, headers=auth(staff_token))
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "FORBIDDEN"

    async def test_list_categories(self, client, manager_token, category):
        res = await client.get("/api/v1/categories", headers=auth(manager_token))
        assert res.status_code == 200
        assert len(res.json()) >= 1


@pytest.mark.asyncio
class TestProducts:
    async def test_create_product(self, client, manager_token, category):
        res = await client.post("/api/v1/products", json={
            "name": "USB Hub", "sku": "USB-001",
            "unit_of_measure": "pcs", "reorder_level": 10,
            "category_id": category["id"],
        }, headers=auth(manager_token))
        assert res.status_code == 201
        body = res.json()
        assert body["sku"] == "USB-001"
        assert body["name"] == "USB Hub"

    async def test_create_product_duplicate_sku(self, client, manager_token, product):
        res = await client.post("/api/v1/products", json={
            "name": "Another Product", "sku": product["sku"],
            "unit_of_measure": "pcs", "reorder_level": 0,
        }, headers=auth(manager_token))
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_list_products(self, client, manager_token, product):
        res = await client.get("/api/v1/products", headers=auth(manager_token))
        assert res.status_code == 200
        assert len(res.json()) >= 1

    async def test_search_products(self, client, manager_token, product):
        res = await client.get(f"/api/v1/products?search={product['name'][:5]}", headers=auth(manager_token))
        assert res.status_code == 200
        assert any(p["id"] == product["id"] for p in res.json())

    async def test_get_product(self, client, manager_token, product):
        res = await client.get(f"/api/v1/products/{product['id']}", headers=auth(manager_token))
        assert res.status_code == 200
        assert res.json()["id"] == product["id"]

    async def test_get_product_not_found(self, client, manager_token):
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = await client.get(f"/api/v1/products/{fake_id}", headers=auth(manager_token))
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"

    async def test_update_product(self, client, manager_token, product):
        res = await client.put(f"/api/v1/products/{product['id']}", json={"reorder_level": 25}, headers=auth(manager_token))
        assert res.status_code == 200
        assert res.json()["reorder_level"] == 25

    async def test_delete_product(self, client, manager_token):
        created = await client.post("/api/v1/products", json={
            "name": "Deletable", "sku": "DEL-001", "unit_of_measure": "pcs", "reorder_level": 0
        }, headers=auth(manager_token))
        pid = created.json()["id"]
        res = await client.delete(f"/api/v1/products/{pid}", headers=auth(manager_token))
        assert res.status_code == 204

    async def test_staff_cannot_delete_product(self, client, staff_token, product):
        res = await client.delete(f"/api/v1/products/{product['id']}", headers=auth(staff_token))
        assert res.status_code == 403

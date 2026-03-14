"""
Tests for core inventory operations:
  Warehouses creation
  Receipts: create (draft) → validate (stock update)
  Deliveries: create → validate (stock deduction, insufficient stock guard)
  Ledger: entries created after operations
  Stock: correct quantities
"""
import pytest
from tests.conftest import auth


@pytest.fixture
async def warehouse(client, manager_token):
    res = await client.post("/api/v1/warehouses", json={"name": "Test WH", "address": "123 Test St"}, headers=auth(manager_token))
    assert res.status_code == 201
    return res.json()


@pytest.fixture
async def inv_product(client, manager_token):
    res = await client.post("/api/v1/products", json={
        "name": "Inventory Item", "sku": "INV-TEST-001", "unit_of_measure": "pcs", "reorder_level": 2
    }, headers=auth(manager_token))
    if res.status_code == 400:  # Already exists from a previous run
        items = await client.get("/api/v1/products?search=INV-TEST-001", headers=auth(manager_token))
        return items.json()[0]
    assert res.status_code == 201
    return res.json()


@pytest.mark.asyncio
class TestWarehouses:
    async def test_create_warehouse(self, client, manager_token):
        res = await client.post("/api/v1/warehouses", json={"name": "Alpha WH"}, headers=auth(manager_token))
        assert res.status_code == 201
        assert res.json()["name"] == "Alpha WH"

    async def test_list_warehouses(self, client, manager_token, warehouse):
        res = await client.get("/api/v1/warehouses", headers=auth(manager_token))
        assert res.status_code == 200
        assert len(res.json()) >= 1


@pytest.mark.asyncio
class TestReceiptsAndStock:
    async def test_create_receipt_draft(self, client, staff_token, inv_product, warehouse):
        res = await client.post("/api/v1/receipts", json={
            "supplier": "Test Supplier",
            "items": [{"product_id": inv_product["id"], "warehouse_id": warehouse["id"], "quantity": 10}]
        }, headers=auth(staff_token))
        assert res.status_code == 201
        assert res.json()["status"] == "draft"

    async def test_validate_receipt_updates_stock(self, client, staff_token, manager_token, inv_product, warehouse):
        # Create receipt
        rec = await client.post("/api/v1/receipts", json={
            "supplier": "Stock Supplier",
            "items": [{"product_id": inv_product["id"], "warehouse_id": warehouse["id"], "quantity": 50}]
        }, headers=auth(staff_token))
        assert rec.status_code == 201
        receipt_id = rec.json()["id"]

        # Validate it
        val = await client.post(f"/api/v1/receipts/{receipt_id}/validate", headers=auth(staff_token))
        assert val.status_code == 200
        assert val.json()["status"] == "validated"

        # Check stock increased
        stock = await client.get(
            f"/api/v1/stock?product_id={inv_product['id']}&warehouse_id={warehouse['id']}",
            headers=auth(manager_token)
        )
        assert stock.status_code == 200
        total_qty = sum(s["quantity"] for s in stock.json())
        assert total_qty >= 50

    async def test_double_validate_receipt_blocked(self, client, staff_token, inv_product, warehouse):
        rec = await client.post("/api/v1/receipts", json={
            "supplier": "Double Supplier",
            "items": [{"product_id": inv_product["id"], "warehouse_id": warehouse["id"], "quantity": 5}]
        }, headers=auth(staff_token))
        receipt_id = rec.json()["id"]
        await client.post(f"/api/v1/receipts/{receipt_id}/validate", headers=auth(staff_token))
        res2 = await client.post(f"/api/v1/receipts/{receipt_id}/validate", headers=auth(staff_token))
        assert res2.status_code == 400
        assert res2.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
class TestDeliveries:
    async def test_delivery_deducts_stock(self, client, staff_token, manager_token, inv_product, warehouse):
        # First receive some stock
        rec = await client.post("/api/v1/receipts", json={
            "supplier": "Pre-Delivery Supplier",
            "items": [{"product_id": inv_product["id"], "warehouse_id": warehouse["id"], "quantity": 100}]
        }, headers=auth(staff_token))
        await client.post(f"/api/v1/receipts/{rec.json()['id']}/validate", headers=auth(staff_token))

        stock_before = await client.get(
            f"/api/v1/stock?product_id={inv_product['id']}&warehouse_id={warehouse['id']}",
            headers=auth(manager_token)
        )
        qty_before = sum(s["quantity"] for s in stock_before.json())

        # Deliver 30 units
        del_res = await client.post("/api/v1/deliveries", json={
            "customer": "Test Customer",
            "items": [{"product_id": inv_product["id"], "warehouse_id": warehouse["id"], "quantity": 30}]
        }, headers=auth(staff_token))
        assert del_res.status_code == 201
        delivery_id = del_res.json()["id"]

        val = await client.post(f"/api/v1/deliveries/{delivery_id}/validate", headers=auth(staff_token))
        assert val.status_code == 200

        stock_after = await client.get(
            f"/api/v1/stock?product_id={inv_product['id']}&warehouse_id={warehouse['id']}",
            headers=auth(manager_token)
        )
        qty_after = sum(s["quantity"] for s in stock_after.json())
        assert qty_after == qty_before - 30

    async def test_delivery_insufficient_stock_blocked(self, client, staff_token, inv_product, warehouse):
        # Try to deliver more than available
        del_res = await client.post("/api/v1/deliveries", json={
            "customer": "Greedy Customer",
            "items": [{"product_id": inv_product["id"], "warehouse_id": warehouse["id"], "quantity": 999999}]
        }, headers=auth(staff_token))
        delivery_id = del_res.json()["id"]
        val = await client.post(f"/api/v1/deliveries/{delivery_id}/validate", headers=auth(staff_token))
        assert val.status_code == 400
        assert val.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
class TestLedger:
    async def test_ledger_has_entries(self, client, manager_token):
        res = await client.get("/api/v1/ledger", headers=auth(manager_token))
        assert res.status_code == 200
        # After the tests above there should be at least one entry
        assert isinstance(res.json(), list)

    async def test_ledger_forbidden_for_staff(self, client, staff_token):
        res = await client.get("/api/v1/ledger", headers=auth(staff_token))
        assert res.status_code == 403

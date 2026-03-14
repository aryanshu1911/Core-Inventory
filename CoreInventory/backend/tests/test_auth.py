"""
Tests for authentication endpoints:
  POST /api/v1/auth/register
  POST /api/v1/auth/login
  GET  /api/v1/auth/me
"""
import pytest
from tests.conftest import auth


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client):
        res = await client.post("/api/v1/auth/register", json={
            "name": "Alice",
            "email": "alice@test.com",
            "password": "Password123!",
            "role": "warehouse_staff",
        })
        assert res.status_code == 201
        body = res.json()
        assert body["email"] == "alice@test.com"
        assert body["role"] == "warehouse_staff"
        assert "password_hash" not in body

    async def test_register_duplicate_email(self, client):
        payload = {"name": "Bob", "email": "bob@test.com", "password": "Pass123!", "role": "warehouse_staff"}
        await client.post("/api/v1/auth/register", json=payload)
        res = await client.post("/api/v1/auth/register", json=payload)
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_register_invalid_email(self, client):
        res = await client.post("/api/v1/auth/register", json={
            "name": "Bad", "email": "not-an-email", "password": "Pass123!", "role": "warehouse_staff"
        })
        assert res.status_code == 422
        assert res.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client):
        await client.post("/api/v1/auth/register", json={
            "name": "Carol", "email": "carol@test.com", "password": "Pass123!", "role": "inventory_manager"
        })
        res = await client.post("/api/v1/auth/login", json={
            "email": "carol@test.com", "password": "Pass123!"
        })
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_wrong_password(self, client):
        await client.post("/api/v1/auth/register", json={
            "name": "Dave", "email": "dave@test.com", "password": "RealPass123!", "role": "warehouse_staff"
        })
        res = await client.post("/api/v1/auth/login", json={
            "email": "dave@test.com", "password": "WrongPass!"
        })
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"

    async def test_login_unknown_email(self, client):
        res = await client.post("/api/v1/auth/login", json={
            "email": "nobody@nowhere.com", "password": "Pass123!"
        })
        assert res.status_code == 401


@pytest.mark.asyncio
class TestMe:
    async def test_me_authenticated(self, client, manager_token):
        res = await client.get("/api/v1/auth/me", headers=auth(manager_token))
        assert res.status_code == 200
        assert res.json()["email"] == "manager@ci.test"

    async def test_me_unauthenticated(self, client):
        res = await client.get("/api/v1/auth/me")
        assert res.status_code == 401

    async def test_me_invalid_token(self, client):
        res = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer tampered.token.here"})
        assert res.status_code == 401

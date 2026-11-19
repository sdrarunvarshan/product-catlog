import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_customer(auth_client: AsyncClient):
    """Test customer registration."""
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "customer@test.com",
            "password": "password123",
            "full_name": "Test Customer"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "customer@test.com"
    assert data["user"]["role"] == "CUSTOMER"


@pytest.mark.asyncio
async def test_register_duplicate_email(auth_client: AsyncClient):
    """Test registration with duplicate email."""
    # First registration
    await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@test.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )

    # Second registration with same email
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@test.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_customer(auth_client: AsyncClient):
    """Test customer login."""
    # Register first
    await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@test.com",
            "password": "password123",
            "full_name": "Login User"
        }
    )

    # Login
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@test.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login@test.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials(auth_client: AsyncClient):
    """Test login with invalid credentials."""
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(auth_client: AsyncClient):
    """Test getting current user profile."""
    # Register and login
    register_response = await auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "profile@test.com",
            "password": "password123",
            "full_name": "Profile User"
        }
    )
    token = register_response.json()["access_token"]

    # Get current user
    response = await auth_client.get(
        f"/api/v1/auth/me?token={token}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@test.com"
    assert data["full_name"] == "Profile User"


@pytest.mark.asyncio
async def test_logout(auth_client: AsyncClient):
    """Test logout endpoint."""
    response = await auth_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

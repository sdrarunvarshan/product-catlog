import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_product(product_client: AsyncClient):
    """Test creating a product."""
    response = await product_client.post(
        "/api/v1/products/",
        json={
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "stock_quantity": 10
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == 99.99
    assert data["stock_quantity"] == 10


@pytest.mark.asyncio
async def test_list_products(product_client: AsyncClient):
    """Test listing products."""
    # Create a product first
    await product_client.post(
        "/api/v1/products/",
        json={
            "name": "List Test Product",
            "description": "Test",
            "price": 49.99,
            "stock_quantity": 5
        }
    )

    # List products
    response = await product_client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) > 0


@pytest.mark.asyncio
async def test_get_product(product_client: AsyncClient):
    """Test getting a specific product."""
    # Create a product
    create_response = await product_client.post(
        "/api/v1/products/",
        json={
            "name": "Get Test Product",
            "description": "Test",
            "price": 29.99,
            "stock_quantity": 3
        }
    )
    product_id = create_response.json()["id"]

    # Get the product
    response = await product_client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Get Test Product"


@pytest.mark.asyncio
async def test_get_nonexistent_product(product_client: AsyncClient):
    """Test getting a nonexistent product."""
    response = await product_client.get(f"/api/v1/products/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_product(product_client: AsyncClient):
    """Test updating a product."""
    # Create a product
    create_response = await product_client.post(
        "/api/v1/products/",
        json={
            "name": "Update Test Product",
            "description": "Original description",
            "price": 19.99,
            "stock_quantity": 2
        }
    )
    product_id = create_response.json()["id"]

    # Update the product
    response = await product_client.put(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Updated Product",
            "description": "Updated description",
            "price": 29.99,
            "stock_quantity": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["price"] == 29.99


@pytest.mark.asyncio
async def test_delete_product(product_client: AsyncClient):
    """Test deleting a product (soft delete)."""
    # Create a product
    create_response = await product_client.post(
        "/api/v1/products/",
        json={
            "name": "Delete Test Product",
            "description": "To be deleted",
            "price": 9.99,
            "stock_quantity": 1
        }
    )
    product_id = create_response.json()["id"]

    # Delete the product
    response = await product_client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204

    # Verify it's soft deleted (not in active list)
    list_response = await product_client.get("/api/v1/products/?active_only=true")
    products = list_response.json()["products"]
    assert not any(p["id"] == product_id for p in products)

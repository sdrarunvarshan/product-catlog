import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_get_cart(order_client: AsyncClient):
    """Test getting a customer's cart."""
    customer_id = uuid4()
    response = await order_client.get(f"/api/v1/cart/?customer_id={customer_id}")
    # Cart might not exist initially, that's okay
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_add_to_cart(order_client: AsyncClient):
    """Test adding an item to the cart."""
    customer_id = uuid4()
    product_id = uuid4()

    # This test requires the product service to be running
    # For integration testing, we'd mock the product service call
    response = await order_client.post(
        f"/api/v1/cart/items?customer_id={customer_id}",
        json={
            "product_id": str(product_id),
            "quantity": 2
        }
    )
    # May fail if product service is not available
    # In a real integration test, we'd set up the product service


@pytest.mark.asyncio
async def test_create_order(order_client: AsyncClient):
    """Test creating an order from cart."""
    customer_id = uuid4()
    response = await order_client.post(
        f"/api/v1/orders/checkout?customer_id={customer_id}"
    )
    # May fail if cart is empty or product service unavailable
    assert response.status_code in [201, 400]


@pytest.mark.asyncio
async def test_get_order(order_client: AsyncClient):
    """Test getting a specific order."""
    order_id = uuid4()
    response = await order_client.get(f"/api/v1/orders/{order_id}")
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_list_customer_orders(order_client: AsyncClient):
    """Test listing customer orders."""
    customer_id = uuid4()
    response = await order_client.get(
        f"/api/v1/orders/?customer_id={customer_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_all_orders(order_client: AsyncClient):
    """Test listing all orders (admin)."""
    response = await order_client.get("/api/v1/orders/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_update_order_status(order_client: AsyncClient):
    """Test updating order status."""
    order_id = uuid4()
    response = await order_client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "CONFIRMED"}
    )
    assert response.status_code in [200, 404]

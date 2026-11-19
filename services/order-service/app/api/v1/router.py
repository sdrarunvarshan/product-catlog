from fastapi import APIRouter
from app.api.v1 import cart_routes, order_routes

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(cart_routes.router, prefix="/cart", tags=["Cart"])
api_router.include_router(order_routes.router, prefix="/orders", tags=["Orders"])

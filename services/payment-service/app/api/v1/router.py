from fastapi import APIRouter
from app.api.v1 import payment_routes

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(payment_routes.router, prefix="/payments", tags=["Payments"])

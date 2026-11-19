from fastapi import APIRouter
from app.api.v1 import auth_routes

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])

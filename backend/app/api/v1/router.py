"""API v1 router - MVP endpoints only."""
from fastapi import APIRouter

from app.api.v1 import products, mockups, scenes

api_router = APIRouter()

# MVP endpoints
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(mockups.router, prefix="/mockups", tags=["mockups"])
api_router.include_router(scenes.router, prefix="/scenes", tags=["scenes"])

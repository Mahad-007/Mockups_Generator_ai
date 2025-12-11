"""API v1 router - all endpoints."""
from fastapi import APIRouter

from app.api.v1 import (
    products,
    mockups,
    scenes,
    chat,
    exports,
    batch,
    brands,
    auth,
    users,
    teams,
)

api_router = APIRouter()

# Auth / Users
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])

# Core endpoints
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(mockups.router, prefix="/mockups", tags=["mockups"])
api_router.include_router(scenes.router, prefix="/scenes", tags=["scenes"])

# Phase 3: Chat/Refinement
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# Phase 4: Batch generation & Export
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])
api_router.include_router(exports.router, prefix="/export", tags=["export"])

# Phase 5: Brand DNA
api_router.include_router(brands.router, prefix="/brands", tags=["brands"])

"""Pydantic schemas."""
from app.schemas.product import ProductBase, ProductCreate, ProductResponse
from app.schemas.mockup import MockupGenerateRequest, MockupResponse, MockupUpdateRequest, GenerationStatus
from app.schemas.chat import (
    ChatSessionCreate,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    RefinementSuggestion,
    RefinementSuggestionsResponse,
)
from app.schemas.brand import (
    BrandBase,
    BrandCreate,
    BrandUpdate,
    BrandResponse,
    BrandExtractRequest,
    BrandExtractResponse,
    BrandPromptResponse,
    BrandScenesResponse,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
    AuthResponse,
    UsageResponse,
)

__all__ = [
    "ProductBase",
    "ProductCreate",
    "ProductResponse",
    "MockupGenerateRequest",
    "MockupResponse",
    "MockupUpdateRequest",
    "GenerationStatus",
    "ChatSessionCreate",
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatSessionResponse",
    "RefinementSuggestion",
    "RefinementSuggestionsResponse",
    # Brand schemas
    "BrandBase",
    "BrandCreate",
    "BrandUpdate",
    "BrandResponse",
    "BrandExtractRequest",
    "BrandExtractResponse",
    "BrandPromptResponse",
    "BrandScenesResponse",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    "AuthResponse",
    "UsageResponse",
]

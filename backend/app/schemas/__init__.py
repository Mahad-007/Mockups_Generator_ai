"""Pydantic schemas."""
from app.schemas.product import ProductBase, ProductCreate, ProductResponse
from app.schemas.mockup import MockupGenerateRequest, MockupResponse, GenerationStatus
from app.schemas.chat import (
    ChatSessionCreate,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    RefinementSuggestion,
    RefinementSuggestionsResponse,
)

__all__ = [
    "ProductBase",
    "ProductCreate",
    "ProductResponse",
    "MockupGenerateRequest",
    "MockupResponse",
    "GenerationStatus",
    "ChatSessionCreate",
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatSessionResponse",
    "RefinementSuggestion",
    "RefinementSuggestionsResponse",
]

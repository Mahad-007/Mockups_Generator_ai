"""Chat schemas for refinement conversations."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatSessionCreate(BaseModel):
    """Request to create a new chat session."""
    mockup_id: str


class ChatMessageRequest(BaseModel):
    """Request to send a message in a chat session."""
    content: str


class ChatMessageResponse(BaseModel):
    """Response schema for a chat message."""
    id: str
    role: str
    content: str
    image_url: Optional[str] = None
    refinement_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """Response schema for a chat session."""
    id: str
    mockup_id: str
    current_image_url: str
    messages: List[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RefinementSuggestion(BaseModel):
    """A suggested refinement for the user."""
    label: str
    prompt: str
    category: str  # lighting, color, surface, style, position


class RefinementSuggestionsResponse(BaseModel):
    """Response with refinement suggestions."""
    suggestions: List[RefinementSuggestion]

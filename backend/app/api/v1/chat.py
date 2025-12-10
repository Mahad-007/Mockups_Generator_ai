from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    image_url: Optional[str] = None


class CreateSessionRequest(BaseModel):
    mockup_id: str


class SendMessageRequest(BaseModel):
    message: str


@router.post("/sessions")
async def create_chat_session(request: CreateSessionRequest):
    """Create a new chat session for mockup refinement."""
    # TODO: Implement session creation
    # 1. Get mockup from database
    # 2. Create new chat session
    # 3. Initialize with system prompt for refinement

    return {
        "session_id": "session-123",
        "mockup_id": request.mockup_id,
        "messages": [],
    }


@router.post("/sessions/{session_id}/message")
async def send_message(session_id: str, request: SendMessageRequest):
    """Send a refinement message and get AI response."""
    # TODO: Implement message handling
    # 1. Get session and history
    # 2. Parse user intent (lighting, background, color, etc.)
    # 3. Generate refinement prompt
    # 4. Call Gemini for image modification
    # 5. Return updated mockup

    # Example refinement commands:
    # - "Make the background warmer"
    # - "Add morning sunlight from the left"
    # - "Change to a wooden table"
    # - "Make it more minimal"
    # - "Add some plants in the background"

    return {
        "session_id": session_id,
        "response": "I'll adjust the lighting for you...",
        "updated_mockup_url": None,  # New mockup after refinement
        "suggestions": [
            "Make it brighter",
            "Add more contrast",
            "Try a different angle",
        ],
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get chat session history."""
    # TODO: Implement session retrieval
    return {
        "session_id": session_id,
        "messages": [],
    }

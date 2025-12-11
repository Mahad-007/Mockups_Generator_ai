"""Chat API endpoints for conversational mockup refinement."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.storage import get_image, save_image
from app.core.gemini import gemini_client
from app.core.utils import get_image_url
from app.models import Mockup, ChatSession, ChatMessage, User
from app.schemas import (
    ChatSessionCreate,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    RefinementSuggestion,
    RefinementSuggestionsResponse,
)

router = APIRouter()

# Pre-defined refinement suggestions
REFINEMENT_SUGGESTIONS = [
    # Lighting
    RefinementSuggestion(
        label="Make it warmer",
        prompt="Add warmer, golden lighting to the scene",
        category="lighting"
    ),
    RefinementSuggestion(
        label="Make it cooler",
        prompt="Add cooler, blue-toned lighting",
        category="lighting"
    ),
    RefinementSuggestion(
        label="Add morning light",
        prompt="Add soft morning sunlight from the side",
        category="lighting"
    ),
    RefinementSuggestion(
        label="Dramatic shadows",
        prompt="Add more dramatic shadows for depth",
        category="lighting"
    ),
    # Background
    RefinementSuggestion(
        label="Blur background",
        prompt="Make the background more blurry for depth of field effect",
        category="background"
    ),
    RefinementSuggestion(
        label="Simplify background",
        prompt="Make the background cleaner and more minimal",
        category="background"
    ),
    # Surface
    RefinementSuggestion(
        label="Wooden surface",
        prompt="Change the surface to natural wood",
        category="surface"
    ),
    RefinementSuggestion(
        label="Marble surface",
        prompt="Change the surface to elegant marble",
        category="surface"
    ),
    # Style
    RefinementSuggestion(
        label="More minimal",
        prompt="Make the overall style more minimal and clean",
        category="style"
    ),
    RefinementSuggestion(
        label="More premium",
        prompt="Make it look more luxurious and premium",
        category="style"
    ),
    # Props
    RefinementSuggestion(
        label="Add plants",
        prompt="Add some small decorative plants in the background",
        category="add_element"
    ),
    RefinementSuggestion(
        label="Add shadows",
        prompt="Add more natural shadows under the product",
        category="add_element"
    ),
]


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    request: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new chat session for refining a mockup.

    - Takes mockup ID
    - Initializes conversation with the mockup image
    - Returns session with initial state
    """
    # Get the mockup
    result = await db.execute(
        select(Mockup).where(
            Mockup.id == request.mockup_id,
            Mockup.user_id == current_user.id,
        )
    )
    mockup = result.scalar_one_or_none()

    if not mockup:
        raise HTTPException(status_code=404, detail="Mockup not found")

    # Create session
    session = ChatSession(
        mockup_id=mockup.id,
        current_image_path=mockup.image_path,
    )
    db.add(session)

    # Add system message
    system_msg = ChatMessage(
        session_id=session.id,
        role="system",
        content="Chat session started. You can now refine your mockup using natural language.",
        image_path=mockup.image_path,
    )
    db.add(system_msg)

    await db.flush()
    await db.refresh(session)

    # Load messages
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session.id)
        .options(selectinload(ChatSession.messages))
    )
    session = result.scalar_one()

    return _build_session_response(session)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a chat session with all messages."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .options(selectinload(ChatSession.messages))
        .join(Mockup, Mockup.id == ChatSession.mockup_id)
        .where(Mockup.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return _build_session_response(session)


@router.post("/sessions/{session_id}/message", response_model=ChatMessageResponse)
async def send_message(
    session_id: str,
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Send a refinement message and get an updated mockup.

    - Takes natural language refinement instruction
    - Uses AI to understand and apply the change
    - Returns the new message with refined image
    """
    # Get session with messages
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .join(Mockup, Mockup.id == ChatSession.mockup_id)
        .where(Mockup.user_id == current_user.id)
        .options(selectinload(ChatSession.messages))
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.content,
    )
    db.add(user_msg)

    # Parse refinement intent
    intent = await gemini_client.parse_refinement_intent(request.content)

    # Get current image
    current_image = get_image(session.current_image_path)

    # Build conversation history for context
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in session.messages
        if msg.role in ("user", "assistant")
    ]

    # Refine the mockup
    refined_image = await gemini_client.refine_mockup(
        current_image=current_image,
        refinement_instruction=request.content,
        conversation_history=history,
    )

    if not refined_image:
        # If refinement failed, add error message
        error_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content="I couldn't apply that refinement. Please try a different instruction.",
        )
        db.add(error_msg)
        await db.flush()
        await db.refresh(error_msg)

        return ChatMessageResponse(
            id=error_msg.id,
            role=error_msg.role,
            content=error_msg.content,
            image_url=None,
            refinement_type=None,
            created_at=error_msg.created_at,
        )

    # Save refined image
    refined_path = save_image(refined_image, "refinements")

    # Update session's current image
    session.current_image_path = refined_path

    # Create assistant response
    response_content = _generate_response_text(intent)
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response_content,
        image_path=refined_path,
        refinement_type=intent.get("type"),
        refinement_params=intent.get("specific_params"),
    )
    db.add(assistant_msg)

    await db.flush()
    await db.refresh(assistant_msg)

    return ChatMessageResponse(
        id=assistant_msg.id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        image_url=get_image_url(assistant_msg.image_path),
        refinement_type=assistant_msg.refinement_type,
        created_at=assistant_msg.created_at,
    )


@router.get("/sessions/{session_id}/undo", response_model=ChatMessageResponse)
async def undo_last_refinement(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Undo the last refinement and revert to previous image.

    Returns the previous state.
    """
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .join(Mockup, Mockup.id == ChatSession.mockup_id)
        .where(Mockup.user_id == current_user.id)
        .options(selectinload(ChatSession.messages))
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Find messages with images (excluding system)
    image_messages = [
        m for m in session.messages
        if m.image_path and m.role != "system"
    ]

    if len(image_messages) < 2:
        raise HTTPException(status_code=400, detail="Nothing to undo")

    # Get the previous image
    previous_msg = image_messages[-2]
    session.current_image_path = previous_msg.image_path

    # Add undo message
    undo_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content="Reverted to previous version.",
        image_path=previous_msg.image_path,
    )
    db.add(undo_msg)

    await db.flush()
    await db.refresh(undo_msg)

    return ChatMessageResponse(
        id=undo_msg.id,
        role=undo_msg.role,
        content=undo_msg.content,
        image_url=get_image_url(undo_msg.image_path),
        refinement_type="undo",
        created_at=undo_msg.created_at,
    )


@router.get("/suggestions", response_model=RefinementSuggestionsResponse)
async def get_refinement_suggestions():
    """Get pre-defined refinement suggestions for quick actions."""
    return RefinementSuggestionsResponse(suggestions=REFINEMENT_SUGGESTIONS)


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    mockup_id: str = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List chat sessions, optionally filtered by mockup."""
    query = (
        select(ChatSession)
        .join(Mockup, Mockup.id == ChatSession.mockup_id)
        .where(Mockup.user_id == current_user.id)
        .options(selectinload(ChatSession.messages))
        .order_by(ChatSession.updated_at.desc())
        .limit(limit)
    )

    if mockup_id:
        query = query.where(ChatSession.mockup_id == mockup_id)

    result = await db.execute(query)
    sessions = result.scalars().all()

    return [_build_session_response(s) for s in sessions]


def _build_session_response(session: ChatSession) -> ChatSessionResponse:
    """Build a ChatSessionResponse from a ChatSession model."""
    return ChatSessionResponse(
        id=session.id,
        mockup_id=session.mockup_id,
        current_image_url=get_image_url(session.current_image_path),
        messages=[
            ChatMessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                image_url=get_image_url(m.image_path) if m.image_path else None,
                refinement_type=m.refinement_type,
                created_at=m.created_at,
            )
            for m in session.messages
        ],
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _generate_response_text(intent: dict) -> str:
    """Generate a friendly response based on the refinement intent."""
    refinement_type = intent.get("type", "other")
    description = intent.get("description", "the requested changes")

    responses = {
        "lighting": f"I've adjusted the lighting: {description}",
        "color": f"I've modified the colors: {description}",
        "background": f"I've updated the background: {description}",
        "surface": f"I've changed the surface: {description}",
        "style": f"I've adjusted the style: {description}",
        "position": f"I've repositioned elements: {description}",
        "add_element": f"I've added elements: {description}",
        "remove_element": f"I've removed elements: {description}",
        "other": f"I've applied the changes: {description}",
    }

    return responses.get(refinement_type, f"Done! {description}")

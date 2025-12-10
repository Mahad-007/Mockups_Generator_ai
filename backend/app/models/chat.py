"""Chat models - stores conversation sessions for mockup refinement."""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class MessageRole(str, enum.Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSession(Base):
    """A chat session for refining a mockup."""
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mockup_id = Column(String, ForeignKey("mockups.id"), nullable=False)

    # Current state
    current_image_path = Column(String, nullable=False)  # Latest refined image

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    mockup = relationship("Mockup", backref="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """A single message in a chat session."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)

    # Message content
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # If this message resulted in a new image
    image_path = Column(String, nullable=True)

    # Refinement metadata (what was changed)
    refinement_type = Column(String, nullable=True)  # lighting, color, surface, etc.
    refinement_params = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

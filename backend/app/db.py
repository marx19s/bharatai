from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from app.config import settings

Base = declarative_base()

class DocumentMetadata(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    status = Column(String, default="processing")  # processing, completed, failed
    summary = Column(Text, nullable=True)
    summary_punjabi = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    messages = relationship("ChatMessage", back_populates="document", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="document")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    document = relationship("DocumentMetadata", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    has_search = Column(Boolean, default=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    document = relationship("DocumentMetadata", back_populates="messages")


# Database engine setup
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

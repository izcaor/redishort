from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database.database import Base

class WorkflowState(str, enum.Enum):
    NEW = "new"
    DRAFTING = "drafting"
    PENDING_APPROVAL = "pending_approval"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    projects = relationship("VideoProject", back_populates="user")
    sources = relationship("ContentSource", back_populates="user")

class ContentSource(Base):
    __tablename__ = "content_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_type = Column(String, index=True, nullable=False)
    source_url = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="sources")

class VideoProject(Base):
    __tablename__ = "video_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_id = Column(String, index=True, nullable=False)
    source_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content_text = Column(Text, nullable=False)
    author = Column(String, nullable=True)
    metadata_json = Column(JSON, default={})
    status = Column(Enum(WorkflowState), default=WorkflowState.NEW, nullable=False)

    script = Column(Text, nullable=True)
    youtube_title = Column(String, nullable=True)
    youtube_desc = Column(Text, nullable=True)
    narrator_gender = Column(String, nullable=True)

    video_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="projects")

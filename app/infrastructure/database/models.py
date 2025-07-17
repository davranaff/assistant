"""
Database models for AutoPoster Bot
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


from infrastructure.database.base import BaseModel


class PostEntity(BaseModel):
    """Post entity for database"""
    __tablename__ = "posts"

    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    topic = Column(String(100), nullable=False)
    tags = Column(Text, nullable=False, default="[]")  # JSON as text
    user_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="draft")

    # Relationships
    publications = relationship("PublicationEntity", back_populates="post", cascade="all, delete-orphan")


class PublicationEntity(BaseModel):
    """Publication entity for database"""
    __tablename__ = "publications"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    platform = Column(String(20), nullable=False)
    success = Column(Boolean, nullable=False)
    platform_post_id = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    post = relationship("PostEntity", back_populates="publications")

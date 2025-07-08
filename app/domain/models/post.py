from datetime import datetime
from typing import Optional, List
from enum import Enum
from dataclasses import dataclass
from uuid import UUID


class PostStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PUBLISHED = "published"
    FAILED = "failed"


class Platform(str, Enum):
    MEDIUM = "medium"
    DEV_TO = "dev_to"
    REDDIT = "reddit"


@dataclass
class PostContent:
    title: str
    body: str
    topic: str
    tags: List[str]

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.body.strip():
            raise ValueError("Body cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title too long")


@dataclass
class PublicationResult:
    platform: Platform
    success: bool
    platform_post_id: Optional[str] = None
    url: Optional[str] = None
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None


class Post:
    def __init__(
        self,
        id: UUID,
        content: PostContent,
        user_id: int,
        status: PostStatus = PostStatus.DRAFT,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.content = content
        self.user_id = user_id
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.publications: List[PublicationResult] = []

    def confirm(self) -> None:
        """Confirm post for publication"""
        if self.status != PostStatus.DRAFT:
            raise ValueError("Only draft posts can be confirmed")
        self.status = PostStatus.CONFIRMED
        self.updated_at = datetime.utcnow()

    def add_publication_result(self, result: PublicationResult) -> None:
        """Add publication result"""
        self.publications.append(result)
        self.updated_at = datetime.utcnow()

    def mark_as_published(self) -> None:
        """Mark post as published"""
        if self.status != PostStatus.CONFIRMED:
            raise ValueError("Only confirmed posts can be published")

        successful_publications = [p for p in self.publications if p.success]
        if not successful_publications:
            raise ValueError("No successful publications found")

        self.status = PostStatus.PUBLISHED
        self.updated_at = datetime.utcnow()

    def mark_as_failed(self, error_message: str) -> None:
        """Mark post as failed"""
        self.status = PostStatus.FAILED
        self.updated_at = datetime.utcnow()

    def update_content(self, new_content: PostContent) -> None:
        """Update post content"""
        if self.status != PostStatus.DRAFT:
            raise ValueError("Only draft posts can be updated")
        self.content = new_content
        self.updated_at = datetime.utcnow()

    def get_successful_publications(self) -> List[PublicationResult]:
        """Get successful publications"""
        return [p for p in self.publications if p.success]

    def get_failed_publications(self) -> List[PublicationResult]:
        """Get failed publications"""
        return [p for p in self.publications if not p.success]

    def is_published_on_platform(self, platform: Platform) -> bool:
        """Check if post is published on specific platform"""
        return any(p.platform == platform and p.success for p in self.publications)
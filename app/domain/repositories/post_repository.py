from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.models.post import Post, PostStatus


class PostRepository(ABC):
    """Repository interface for Post aggregate"""

    @abstractmethod
    async def save(self, post: Post) -> Post:
        """Save post to storage"""
        pass

    @abstractmethod
    async def get_by_id(self, post_id: UUID) -> Optional[Post]:
        """Get post by ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[Post]:
        """Get all posts by user"""
        pass

    @abstractmethod
    async def get_by_status(self, status: PostStatus) -> List[Post]:
        """Get posts by status"""
        pass

    @abstractmethod
    async def delete(self, post_id: UUID) -> bool:
        """Delete post by ID"""
        pass

    @abstractmethod
    async def get_confirmed_posts(self) -> List[Post]:
        """Get all confirmed posts ready for publication"""
        pass

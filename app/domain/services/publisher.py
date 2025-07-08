from abc import ABC, abstractmethod
from typing import List, Dict
from app.domain.models.post import Post, Platform, PublicationResult


class Publisher(ABC):
    """Interface for content publishing service"""

    @abstractmethod
    async def publish(
        self,
        post: Post,
        platforms: List[Platform]
    ) -> Dict[Platform, PublicationResult]:
        """Publish post to specified platforms"""
        pass

    @abstractmethod
    async def get_supported_platforms(self) -> List[Platform]:
        """Get list of supported platforms"""
        pass

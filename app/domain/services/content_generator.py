from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.post import PostContent, Platform


class ContentGenerator(ABC):
    """Interface for content generation service"""

    @abstractmethod
    async def generate_content(
        self,
        topic: str,
        target_platform: Optional[Platform] = None,
        tags: Optional[List[str]] = None
    ) -> PostContent:
        """Generate content for given topic"""
        pass

    @abstractmethod
    async def regenerate_content(
        self,
        previous_content: PostContent,
        target_platform: Optional[Platform] = None
    ) -> PostContent:
        """Regenerate content based on previous version"""
        pass

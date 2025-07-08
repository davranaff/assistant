from typing import List, Optional
from uuid import uuid4
from dataclasses import dataclass

from app.domain.models.post import Post, PostContent, Platform
from app.domain.repositories.post_repository import PostRepository
from app.domain.services.content_generator import ContentGenerator
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CreatePostCommand:
    user_id: int
    topic: str
    target_platform: Optional[Platform] = None
    tags: Optional[List[str]] = None


@dataclass
class CreatePostResult:
    post_id: str
    content: PostContent
    success: bool
    error_message: Optional[str] = None


class CreatePostUseCase:
    def __init__(
        self,
        post_repository: PostRepository,
        content_generator: ContentGenerator
    ):
        self._post_repository = post_repository
        self._content_generator = content_generator

    async def execute(self, command: CreatePostCommand) -> CreatePostResult:
        """Execute create post use case"""
        try:
            logger.info(f"Creating post for user {command.user_id}, topic: {command.topic}")

            # Generate content
            content = await self._content_generator.generate_content(
                topic=command.topic,
                target_platform=command.target_platform,
                tags=command.tags or []
            )

            # Create post
            post = Post(
                id=uuid4(),
                content=content,
                user_id=command.user_id
            )

            # Save to repository
            saved_post = await self._post_repository.save(post)

            logger.info(f"Post created successfully: {saved_post.id}")

            return CreatePostResult(
                post_id=str(saved_post.id),
                content=content,
                success=True
            )

        except Exception as e:
            logger.error(f"Failed to create post: {e}")
            return CreatePostResult(
                post_id="",
                content=PostContent("", "", "", []),
                success=False,
                error_message=str(e)
            )

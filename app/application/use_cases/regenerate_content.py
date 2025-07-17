from typing import Optional, Callable
from uuid import UUID
from dataclasses import dataclass

from domain.models.post import Post, PostContent
from domain.repositories.post_repository import PostRepository
from domain.services.content_generator import ContentGenerator
from core.logging import get_logger

from infrastructure.database.session import AsyncSessionLocal
from infrastructure.repositories.sqlalchemy_post_repository import SqlAlchemyPostRepository

logger = get_logger(__name__)


@dataclass
class RegenerateContentCommand:
    post_id: str
    target_platform: Optional[str] = None


@dataclass
class RegenerateContentResult:
    success: bool
    content: Optional[PostContent] = None
    error_message: Optional[str] = None


class RegenerateContentUseCase:
    def __init__(
        self,
        post_repository_factory: Callable[[], type[PostRepository]],
        content_generator: ContentGenerator
    ):
        self._post_repository_factory = post_repository_factory
        self._content_generator = content_generator

    async def execute(self, command: RegenerateContentCommand) -> RegenerateContentResult:
        """Execute regenerate content use case"""
        try:
            logger.info(f"Regenerating content for post: {command.post_id}")

            # Create repository with session
            session = AsyncSessionLocal()
            try:
                repository = SqlAlchemyPostRepository(session)
                
                # Get post
                post = await repository.get_by_id(UUID(command.post_id))
                if not post:
                    return RegenerateContentResult(
                        success=False,
                        error_message="Post not found"
                    )

                # Check if post is in draft status
                if post.status.value != "draft":
                    return RegenerateContentResult(
                        success=False,
                        error_message="Only draft posts can be regenerated"
                    )

                # Regenerate content
                new_content = await self._content_generator.regenerate_content(
                    previous_content=post.content
                )

                # Update post content
                post.update_content(new_content)
                await repository.save(post)
                await session.commit()
            finally:
                await session.close()

            logger.info(f"Content regenerated successfully: {command.post_id}")

            return RegenerateContentResult(
                success=True,
                content=new_content
            )

        except Exception as e:
            logger.error(f"Failed to regenerate content: {e}")
            return RegenerateContentResult(
                success=False,
                error_message=str(e)
            )

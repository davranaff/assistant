from uuid import UUID
from dataclasses import dataclass
from typing import Optional

from app.domain.models.post import PostContent, Platform
from app.domain.repositories.post_repository import PostRepository
from app.domain.services.content_generator import ContentGenerator
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RegenerateContentCommand:
    post_id: UUID
    user_id: int
    target_platform: Optional[Platform] = None


@dataclass
class RegenerateContentResult:
    success: bool
    content: Optional[PostContent] = None
    error_message: Optional[str] = None


class RegenerateContentUseCase:
    def __init__(
        self,
        post_repository: PostRepository,
        content_generator: ContentGenerator
    ):
        self._post_repository = post_repository
        self._content_generator = content_generator

    async def execute(self, command: RegenerateContentCommand) -> RegenerateContentResult:
        """Execute regenerate content use case"""
        try:
            logger.info(f"Regenerating content for post {command.post_id}")

            # Get post from repository
            post = await self._post_repository.get_by_id(command.post_id)
            if not post:
                return RegenerateContentResult(
                    success=False,
                    error_message="Post not found"
                )

            # Check if user owns the post
            if post.user_id != command.user_id:
                return RegenerateContentResult(
                    success=False,
                    error_message="Access denied"
                )

            # Regenerate content
            new_content = await self._content_generator.regenerate_content(
                previous_content=post.content,
                target_platform=command.target_platform
            )

            # Update post with new content
            post.update_content(new_content)

            # Save updated post
            await self._post_repository.save(post)

            logger.info(f"Content regenerated successfully for post {post.id}")

            return RegenerateContentResult(
                success=True,
                content=new_content
            )

        except ValueError as e:
            logger.warning(f"Invalid operation: {e}")
            return RegenerateContentResult(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Failed to regenerate content for post {command.post_id}: {e}")
            return RegenerateContentResult(
                success=False,
                error_message=str(e)
            )

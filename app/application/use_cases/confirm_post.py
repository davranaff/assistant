from uuid import UUID
from dataclasses import dataclass
from typing import Optional

from app.domain.repositories.post_repository import PostRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConfirmPostCommand:
    post_id: UUID
    user_id: int


@dataclass
class ConfirmPostResult:
    success: bool
    error_message: Optional[str] = None


class ConfirmPostUseCase:
    def __init__(self, post_repository: PostRepository):
        self._post_repository = post_repository

    async def execute(self, command: ConfirmPostCommand) -> ConfirmPostResult:
        """Execute confirm post use case"""
        try:
            logger.info(f"Confirming post {command.post_id} for user {command.user_id}")

            # Get post from repository
            post = await self._post_repository.get_by_id(command.post_id)
            if not post:
                return ConfirmPostResult(
                    success=False,
                    error_message="Post not found"
                )

            # Check if user owns the post
            if post.user_id != command.user_id:
                return ConfirmPostResult(
                    success=False,
                    error_message="Access denied"
                )

            # Confirm the post
            post.confirm()

            # Save updated post
            await self._post_repository.save(post)

            logger.info(f"Post {post.id} confirmed successfully")

            return ConfirmPostResult(success=True)

        except ValueError as e:
            logger.warning(f"Invalid operation: {e}")
            return ConfirmPostResult(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Failed to confirm post {command.post_id}: {e}")
            return ConfirmPostResult(
                success=False,
                error_message=str(e)
            )

from typing import Optional, Callable
from uuid import UUID
from dataclasses import dataclass

from domain.models.post import Post, PostStatus
from domain.repositories.post_repository import PostRepository
from core.logging import get_logger

from infrastructure.database.session import AsyncSessionLocal
from infrastructure.repositories.sqlalchemy_post_repository import SqlAlchemyPostRepository

logger = get_logger(__name__)


@dataclass
class ConfirmPostCommand:
    post_id: str


@dataclass
class ConfirmPostResult:
    success: bool
    error_message: Optional[str] = None


class ConfirmPostUseCase:
    def __init__(self, post_repository_factory: Callable[[], type[PostRepository]]):
        self._post_repository_factory = post_repository_factory

    async def execute(self, command: ConfirmPostCommand) -> ConfirmPostResult:
        """Execute confirm post use case"""
        try:
            logger.info(f"Confirming post: {command.post_id}")

            # Create repository with session
            session = AsyncSessionLocal()
            try:
                repository = SqlAlchemyPostRepository(session)
                
                # Get post
                post = await repository.get_by_id(UUID(command.post_id))
                if not post:
                    return ConfirmPostResult(
                        success=False,
                        error_message="Post not found"
                    )

                # Confirm post
                post.confirm()
                await repository.save(post)
                await session.commit()
            finally:
                await session.close()

            logger.info(f"Post confirmed successfully: {command.post_id}")

            return ConfirmPostResult(success=True)

        except Exception as e:
            logger.error(f"Failed to confirm post: {e}")
            return ConfirmPostResult(
                success=False,
                error_message=str(e)
            )

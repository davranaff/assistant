from typing import List, Optional, Callable
from uuid import UUID
from dataclasses import dataclass

from domain.models.post import Post, PublicationResult, Platform
from domain.repositories.post_repository import PostRepository
from domain.services.publisher import Publisher
from core.logging import get_logger

from infrastructure.database.session import AsyncSessionLocal
from infrastructure.repositories.sqlalchemy_post_repository import SqlAlchemyPostRepository

logger = get_logger(__name__)


@dataclass
class PublishPostCommand:
    post_id: str
    platforms: Optional[List[Platform]] = None


@dataclass
class PublishPostResult:
    success: bool
    publication_results: List[PublicationResult]
    error_message: Optional[str] = None


class PublishPostUseCase:
    def __init__(
        self,
        post_repository_factory: Callable[[], type[PostRepository]],
        publisher: Publisher
    ):
        self._post_repository_factory = post_repository_factory
        self._publisher = publisher

    async def execute(self, command: PublishPostCommand) -> PublishPostResult:
        """Execute publish post use case"""
        try:
            logger.info(f"Publishing post: {command.post_id}")

            # Create repository with session
            session = AsyncSessionLocal()
            try:
                repository = SqlAlchemyPostRepository(session)

                # Get post
                post = await repository.get_by_id(UUID(command.post_id))
                if not post:
                    return PublishPostResult(
                        success=False,
                        publication_results=[],
                        error_message="Post not found"
                    )

                # Check if post is confirmed
                if post.status.value != "confirmed":
                    return PublishPostResult(
                        success=False,
                        publication_results=[],
                        error_message="Post must be confirmed before publishing"
                    )

                # Determine platforms to publish to
                platforms = command.platforms or [Platform.MEDIUM, Platform.DEV_TO]

                # Publish to platforms
                publication_results = []
                for platform in platforms:
                    try:
                        result = await self._publisher.publish(post, platform)
                        publication_results.append(result)

                        # Add publication result to post
                        post.add_publication_result(result)

                    except Exception as e:
                        logger.error(f"Failed to publish to {platform}: {e}")
                        publication_results.append(
                            PublicationResult(
                                platform=platform,
                                success=False,
                                error_message=str(e)
                            )
                        )

                # Save updated post with publication results
                await repository.save(post)
                await session.commit()
            finally:
                await session.close()

            # Check if any publication was successful
            successful_publications = [r for r in publication_results if r.success]
            if not successful_publications:
                return PublishPostResult(
                    success=False,
                    publication_results=publication_results,
                    error_message="Failed to publish to any platform"
                )

            logger.info(f"Post published successfully: {command.post_id}")

            return PublishPostResult(
                success=True,
                publication_results=publication_results
            )

        except Exception as e:
            logger.error(f"Failed to publish post: {e}")
            return PublishPostResult(
                success=False,
                publication_results=[],
                error_message=str(e)
            )

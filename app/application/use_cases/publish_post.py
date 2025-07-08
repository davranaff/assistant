from typing import List, Dict
from uuid import UUID
from dataclasses import dataclass

from app.domain.models.post import Platform, PublicationResult
from app.domain.repositories.post_repository import PostRepository
from app.domain.services.publisher import Publisher
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PublishPostCommand:
    post_id: UUID
    platforms: List[Platform]


@dataclass
class PublishPostResult:
    success: bool
    publication_results: Dict[Platform, PublicationResult]
    error_message: str = ""


class PublishPostUseCase:
    def __init__(
        self,
        post_repository: PostRepository,
        publisher: Publisher
    ):
        self._post_repository = post_repository
        self._publisher = publisher

    async def execute(self, command: PublishPostCommand) -> PublishPostResult:
        """Execute publish post use case"""
        try:
            logger.info(f"Publishing post {command.post_id} to platforms: {command.platforms}")

            # Get post from repository
            post = await self._post_repository.get_by_id(command.post_id)
            if not post:
                return PublishPostResult(
                    success=False,
                    publication_results={},
                    error_message="Post not found"
                )

            # Check if post is confirmed
            if post.status.value != "confirmed":
                return PublishPostResult(
                    success=False,
                    publication_results={},
                    error_message="Post must be confirmed before publishing"
                )

            # Publish to platforms
            results = await self._publisher.publish(post, command.platforms)

            # Update post with publication results
            for platform, result in results.items():
                post.add_publication_result(result)

            # Mark as published if any platform succeeded
            successful_results = [r for r in results.values() if r.success]
            if successful_results:
                post.mark_as_published()
                logger.info(f"Post {post.id} published successfully")
            else:
                post.mark_as_failed("All publications failed")
                logger.error(f"All publications failed for post {post.id}")

            # Save updated post
            await self._post_repository.save(post)

            return PublishPostResult(
                success=bool(successful_results),
                publication_results=results
            )

        except Exception as e:
            logger.error(f"Failed to publish post {command.post_id}: {e}")
            return PublishPostResult(
                success=False,
                publication_results={},
                error_message=str(e)
            )

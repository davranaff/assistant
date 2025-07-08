from typing import List, Dict
from datetime import datetime
from app.domain.models.post import Post, Platform, PublicationResult
from app.domain.services.publisher import Publisher
from app.infrastructure.services.platform_publishers import (
    MediumPublisher,
    DevToPublisher,
    RedditPublisher
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class MultiPlatformPublisher(Publisher):
    def __init__(
        self,
        medium_api_key: str = "",
        dev_to_api_key: str = "",
        reddit_config: Dict[str, str] = None
    ):
        self._publishers = {}

        # Initialize publishers based on available API keys
        if medium_api_key:
            self._publishers[Platform.MEDIUM] = MediumPublisher(medium_api_key)

        if dev_to_api_key:
            self._publishers[Platform.DEV_TO] = DevToPublisher(dev_to_api_key)

        if reddit_config:
            self._publishers[Platform.REDDIT] = RedditPublisher(
                client_id=reddit_config.get("client_id", ""),
                client_secret=reddit_config.get("client_secret", ""),
                username=reddit_config.get("username", ""),
                password=reddit_config.get("password", "")
            )

    async def publish(
        self,
        post: Post,
        platforms: List[Platform]
    ) -> Dict[Platform, PublicationResult]:
        """Publish post to multiple platforms"""
        logger.info(f"Publishing post {post.id} to platforms: {platforms}")

        results = {}

        for platform in platforms:
            if platform not in self._publishers:
                logger.warning(f"Publisher for {platform} not configured")
                results[platform] = PublicationResult(
                    platform=platform,
                    success=False,
                    error_message=f"Publisher for {platform} not configured"
                )
                continue

            try:
                logger.info(f"Publishing to {platform}...")
                result = await self._publishers[platform].publish(
                    title=post.content.title,
                    body=post.content.body,
                    tags=post.content.tags
                )
                results[platform] = result

                if result.success:
                    logger.info(f"Successfully published to {platform}: {result.url}")
                else:
                    logger.error(f"Failed to publish to {platform}: {result.error_message}")

            except Exception as e:
                logger.error(f"Error publishing to {platform}: {e}")
                results[platform] = PublicationResult(
                    platform=platform,
                    success=False,
                    error_message=str(e)
                )

        return results

    async def get_supported_platforms(self) -> List[Platform]:
        """Get list of supported platforms"""
        return list(self._publishers.keys())

    def is_platform_supported(self, platform: Platform) -> bool:
        """Check if platform is supported"""
        return platform in self._publishers

from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from core.container import register_service, register_async_service, get_container
from core.config import settings

# Domain repositories
from domain.repositories.post_repository import PostRepository

# Domain services
from domain.services.content_generator import ContentGenerator
from domain.services.publisher import Publisher

# Use cases
from application.use_cases.create_post import CreatePostUseCase
from application.use_cases.confirm_post import ConfirmPostUseCase
from application.use_cases.publish_post import PublishPostUseCase
from application.use_cases.regenerate_content import RegenerateContentUseCase

# Infrastructure implementations
from infrastructure.repositories.sqlalchemy_post_repository import SqlAlchemyPostRepository
from infrastructure.services.openai_content_generator import OpenAIContentGenerator
from infrastructure.services.multi_platform_publisher import MultiPlatformPublisher

# Database
from infrastructure.database.session import AsyncSessionLocal


def create_post_repository_factory():
    """Create factory for post repository"""
    def factory():
        # This will be called in async context
        return SqlAlchemyPostRepository
    return factory


def configure_dependencies():
    """Configure dependency injection container"""

    # Register domain services
    register_service(
        ContentGenerator,
        lambda: OpenAIContentGenerator(settings.together_api_key),
        singleton=True
    )

    register_service(
        Publisher,
        lambda: MultiPlatformPublisher(
            medium_api_key=settings.medium_api_key or "",
            dev_to_api_key=settings.dev_to_api_key or "",
            reddit_config={
                "client_id": settings.reddit_client_id or "",
                "client_secret": settings.reddit_client_secret or "",
                "username": settings.reddit_username or "",
                "password": settings.reddit_password or ""
            } if settings.reddit_client_id else None
        ),
        singleton=True
    )

    # Register use cases with repository factory
    register_service(
        CreatePostUseCase,
        lambda: CreatePostUseCase(
            post_repository_factory=create_post_repository_factory(),
            content_generator=get_container().resolve(ContentGenerator)
        ),
        singleton=False
    )

    register_service(
        ConfirmPostUseCase,
        lambda: ConfirmPostUseCase(
            post_repository_factory=create_post_repository_factory()
        ),
        singleton=False
    )

    register_service(
        PublishPostUseCase,
        lambda: PublishPostUseCase(
            post_repository_factory=create_post_repository_factory(),
            publisher=get_container().resolve(Publisher)
        ),
        singleton=False
    )

    register_service(
        RegenerateContentUseCase,
        lambda: RegenerateContentUseCase(
            post_repository_factory=create_post_repository_factory(),
            content_generator=get_container().resolve(ContentGenerator)
        ),
        singleton=False
    )


def bootstrap_application():
    """Bootstrap the application"""
    configure_dependencies()

    # Additional startup logic can be added here
    # - Database migrations
    # - Cache warming
    # - External service health checks
    # etc.
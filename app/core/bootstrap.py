from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import register_service, get_container
from app.core.config import settings

# Domain repositories
from app.domain.repositories.post_repository import PostRepository

# Domain services
from app.domain.services.content_generator import ContentGenerator
from app.domain.services.publisher import Publisher

# Use cases
from app.application.use_cases.create_post import CreatePostUseCase
from app.application.use_cases.confirm_post import ConfirmPostUseCase
from app.application.use_cases.publish_post import PublishPostUseCase
from app.application.use_cases.regenerate_content import RegenerateContentUseCase

# Infrastructure implementations
from app.infrastructure.repositories.sqlalchemy_post_repository import SqlAlchemyPostRepository
from app.infrastructure.services.openai_content_generator import OpenAIContentGenerator
from app.infrastructure.services.multi_platform_publisher import MultiPlatformPublisher

# Database
from app.infrastructure.database.session import get_db


def configure_dependencies():
    """Configure dependency injection container"""

    # Register repositories
    register_service(
        PostRepository,
        lambda: SqlAlchemyPostRepository(get_db().__next__()),
        singleton=False
    )

    # Register domain services
    register_service(
        ContentGenerator,
        lambda: OpenAIContentGenerator(settings.openai_api_key),
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

    # Register use cases
    register_service(
        CreatePostUseCase,
        lambda: CreatePostUseCase(
            post_repository=get_container().resolve(PostRepository),
            content_generator=get_container().resolve(ContentGenerator)
        ),
        singleton=False
    )

    register_service(
        ConfirmPostUseCase,
        lambda: ConfirmPostUseCase(
            post_repository=get_container().resolve(PostRepository)
        ),
        singleton=False
    )

    register_service(
        PublishPostUseCase,
        lambda: PublishPostUseCase(
            post_repository=get_container().resolve(PostRepository),
            publisher=get_container().resolve(Publisher)
        ),
        singleton=False
    )

    register_service(
        RegenerateContentUseCase,
        lambda: RegenerateContentUseCase(
            post_repository=get_container().resolve(PostRepository),
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
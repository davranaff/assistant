import json
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from domain.models.post import Post, PostContent, PostStatus, PublicationResult, Platform
from domain.repositories.post_repository import PostRepository
from infrastructure.database.models import PostEntity, PublicationEntity
from core.logging import get_logger

logger = get_logger(__name__)


class SqlAlchemyPostRepository(PostRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, post: Post) -> Post:
        """Save post to database"""
        logger.info(f"Saving post {post.id}")

        # Check if post exists
        result = await self._session.execute(
            select(PostEntity).where(PostEntity.id == post.id)
        )
        entity = result.scalars().first()

        if entity:
            # Update existing
            entity.title = post.content.title
            entity.body = post.content.body
            entity.topic = post.content.topic
            entity.tags = json.dumps(post.content.tags)
            entity.status = post.status.value
            entity.updated_at = post.updated_at
        else:
            # Create new
            entity = PostEntity(
                id=post.id,
                title=post.content.title,
                body=post.content.body,
                topic=post.content.topic,
                tags=json.dumps(post.content.tags),
                user_id=post.user_id,
                status=post.status.value,
                created_at=post.created_at,
                updated_at=post.updated_at
            )
            self._session.add(entity)

        # Save publications
        for publication in post.publications:
            pub_result = await self._session.execute(
                select(PublicationEntity).where(
                    PublicationEntity.post_id == post.id,
                    PublicationEntity.platform == publication.platform.value
                )
            )
            pub_entity = pub_result.scalars().first()

            if not pub_entity:
                pub_entity = PublicationEntity(
                    post_id=post.id,
                    platform=publication.platform.value,
                    success=publication.success,
                    platform_post_id=publication.platform_post_id,
                    url=publication.url,
                    error_message=publication.error_message,
                    published_at=publication.published_at
                )
                self._session.add(pub_entity)

        await self._session.commit()
        await self._session.refresh(entity)

        return self._entity_to_domain(entity)

    async def get_by_id(self, post_id: UUID) -> Optional[Post]:
        """Get post by ID"""
        result = await self._session.execute(
            select(PostEntity)
            .options(selectinload(PostEntity.publications))
            .where(PostEntity.id == post_id)
        )
        entity = result.scalars().first()

        if not entity:
            return None

        return self._entity_to_domain(entity)

    async def get_by_user_id(self, user_id: int) -> List[Post]:
        """Get posts by user ID"""
        result = await self._session.execute(
            select(PostEntity)
            .options(selectinload(PostEntity.publications))
            .where(PostEntity.user_id == user_id)
            .order_by(PostEntity.created_at.desc())
        )
        entities = result.scalars().all()

        return [self._entity_to_domain(entity) for entity in entities]

    async def get_by_status(self, status: PostStatus) -> List[Post]:
        """Get posts by status"""
        result = await self._session.execute(
            select(PostEntity)
            .options(selectinload(PostEntity.publications))
            .where(PostEntity.status == status.value)
            .order_by(PostEntity.created_at.desc())
        )
        entities = result.scalars().all()

        return [self._entity_to_domain(entity) for entity in entities]

    async def delete(self, post_id: UUID) -> bool:
        """Delete post by ID"""
        result = await self._session.execute(
            select(PostEntity).where(PostEntity.id == post_id)
        )
        entity = result.scalars().first()

        if not entity:
            return False

        await self._session.delete(entity)
        await self._session.commit()

        return True

    async def get_confirmed_posts(self) -> List[Post]:
        """Get confirmed posts ready for publication"""
        return await self.get_by_status(PostStatus.CONFIRMED)

    def _entity_to_domain(self, entity: PostEntity) -> Post:
        """Convert database entity to domain model"""
        try:
            tags = json.loads(entity.tags) if entity.tags else []
        except (json.JSONDecodeError, TypeError):
            tags = []

        content = PostContent(
            title=entity.title,
            body=entity.body,
            topic=entity.topic,
            tags=tags
        )

        post = Post(
            id=entity.id,
            content=content,
            user_id=entity.user_id,
            status=PostStatus(entity.status),
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

        # Add publications
        for pub_entity in entity.publications:
            publication = PublicationResult(
                platform=Platform(pub_entity.platform),
                success=pub_entity.success,
                platform_post_id=pub_entity.platform_post_id,
                url=pub_entity.url,
                error_message=pub_entity.error_message,
                published_at=pub_entity.published_at
            )
            post.publications.append(publication)

        return post

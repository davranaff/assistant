import httpx
from typing import List
from datetime import datetime
from app.domain.models.post import Platform, PublicationResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class MediumPublisher:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://api.medium.com/v1"

    async def publish(self, title: str, body: str, tags: List[str]) -> PublicationResult:
        """Publish to Medium"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self._api_key}"}

                # Get user info
                user_response = await client.get(f"{self._base_url}/me", headers=headers)
                if user_response.status_code != 200:
                    return PublicationResult(
                        platform=Platform.MEDIUM,
                        success=False,
                        error_message=f"Failed to get user info: {user_response.text}"
                    )

                user_data = user_response.json()
                user_id = user_data["data"]["id"]

                # Publish post
                post_data = {
                    "title": title,
                    "contentFormat": "markdown",
                    "content": body,
                    "publishStatus": "public",
                    "tags": tags[:5]  # Medium allows max 5 tags
                }

                post_response = await client.post(
                    f"{self._base_url}/users/{user_id}/posts",
                    headers=headers,
                    json=post_data
                )

                if post_response.status_code == 201:
                    response_data = post_response.json()
                    return PublicationResult(
                        platform=Platform.MEDIUM,
                        success=True,
                        platform_post_id=response_data["data"]["id"],
                        url=response_data["data"]["url"],
                        published_at=datetime.utcnow()
                    )
                else:
                    return PublicationResult(
                        platform=Platform.MEDIUM,
                        success=False,
                        error_message=f"Failed to publish: {post_response.text}"
                    )

        except Exception as e:
            logger.error(f"Medium publish error: {e}")
            return PublicationResult(
                platform=Platform.MEDIUM,
                success=False,
                error_message=str(e)
            )


class DevToPublisher:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://dev.to/api"

    async def publish(self, title: str, body: str, tags: List[str]) -> PublicationResult:
        """Publish to Dev.to"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "api-key": self._api_key,
                    "Content-Type": "application/json"
                }

                post_data = {
                    "article": {
                        "title": title,
                        "body_markdown": body,
                        "published": True,
                        "tags": tags[:4]  # Dev.to allows max 4 tags
                    }
                }

                response = await client.post(
                    f"{self._base_url}/articles",
                    headers=headers,
                    json=post_data
                )

                if response.status_code == 201:
                    response_data = response.json()
                    return PublicationResult(
                        platform=Platform.DEV_TO,
                        success=True,
                        platform_post_id=str(response_data["id"]),
                        url=response_data["url"],
                        published_at=datetime.utcnow()
                    )
                else:
                    return PublicationResult(
                        platform=Platform.DEV_TO,
                        success=False,
                        error_message=f"Failed to publish: {response.text}"
                    )

        except Exception as e:
            logger.error(f"Dev.to publish error: {e}")
            return PublicationResult(
                platform=Platform.DEV_TO,
                success=False,
                error_message=str(e)
            )


class RedditPublisher:
    def __init__(self, client_id: str, client_secret: str, username: str, password: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        self._base_url = "https://oauth.reddit.com"

    async def _get_access_token(self) -> str:
        """Get Reddit access token"""
        async with httpx.AsyncClient() as client:
            auth = httpx.BasicAuth(self._client_id, self._client_secret)
            data = {
                "grant_type": "password",
                "username": self._username,
                "password": self._password
            }
            headers = {"User-Agent": "AutoPoster/1.0"}

            response = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers
            )

            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                raise Exception(f"Failed to get Reddit access token: {response.text}")

    async def publish(self, title: str, body: str, tags: List[str], subreddit: str = "test") -> PublicationResult:
        """Publish to Reddit"""
        try:
            access_token = await self._get_access_token()

            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"bearer {access_token}",
                    "User-Agent": "AutoPoster/1.0"
                }

                post_data = {
                    "sr": subreddit,
                    "kind": "self",
                    "title": title,
                    "text": body,
                    "api_type": "json"
                }

                response = await client.post(
                    f"{self._base_url}/api/submit",
                    headers=headers,
                    data=post_data
                )

                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get("json", {}).get("errors"):
                        return PublicationResult(
                            platform=Platform.REDDIT,
                            success=False,
                            error_message=str(response_data["json"]["errors"])
                        )

                    return PublicationResult(
                        platform=Platform.REDDIT,
                        success=True,
                        platform_post_id=response_data["json"]["data"]["id"],
                        url=response_data["json"]["data"]["url"],
                        published_at=datetime.utcnow()
                    )
                else:
                    return PublicationResult(
                        platform=Platform.REDDIT,
                        success=False,
                        error_message=f"Failed to publish: {response.text}"
                    )

        except Exception as e:
            logger.error(f"Reddit publish error: {e}")
            return PublicationResult(
                platform=Platform.REDDIT,
                success=False,
                error_message=str(e)
            )

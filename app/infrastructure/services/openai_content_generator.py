from typing import List, Optional
import asyncio
from domain.models.post import PostContent, Platform
from domain.services.content_generator import ContentGenerator
from core.logging import get_logger
from together import Together

logger = get_logger(__name__)


class OpenAIContentGenerator(ContentGenerator):
    def __init__(self, api_key: str, model: str = "meta-llama/Llama-Vision-Free"):
        self._together_client = Together(api_key=api_key)
        self._model = model

    async def generate_content(
        self,
        topic: str,
        target_platform: Optional[Platform] = None,
        tags: Optional[List[str]] = None
    ) -> PostContent:
        """Generate content using Together AI"""
        logger.info(f"Generating content for topic: {topic}")

        platform_prompts = {
            Platform.MEDIUM: "Create a professional article for Medium",
            Platform.DEV_TO: "Create a technical article for Dev.to",
            Platform.REDDIT: "Create an interesting post for Reddit"
        }

        base_prompt = platform_prompts.get(target_platform, "Create an informative article")

        prompt = f"""
        {base_prompt} on the topic: "{topic}"

        Requirements:
        1. Title should be concise and attractive (up to 100 characters)
        2. Article should be structured and informative
        3. Length: 1000-1500 words
        4. Use markdown for formatting
        5. Add practical examples
        6. Article should be useful and interesting

        Respond in format:
        TITLE: [article title]

        CONTENT:
        [main article text]
        """

        try:
            # Run Together AI call in thread pool to avoid blocking
            response = await asyncio.to_thread(
                self._together_client.chat.completions.create,
                model=self._model,
                messages=[
                    {"role": "system", "content": "You are an experienced technical writer and blogger. You create quality content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )

            content = response.choices[0].message.content
            title, body = self._parse_response(content)

            return PostContent(
                title=title,
                body=body,
                topic=topic,
                tags=tags or []
            )

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            # Fallback content
            return PostContent(
                title=f"Article on topic: {topic}",
                body=f"# {topic}\n\nArticle on topic '{topic}' will be created later.",
                topic=topic,
                tags=tags or []
            )

    async def regenerate_content(
        self,
        previous_content: PostContent,
        target_platform: Optional[Platform] = None
    ) -> PostContent:
        """Regenerate content based on previous version"""
        logger.info(f"Regenerating content for topic: {previous_content.topic}")

        prompt = f"""
        Rewrite the article on topic: "{previous_content.topic}"

        Previous version:
        Title: {previous_content.title}
        Content: {previous_content.body[:500]}...

        Requirements:
        1. Create a new attractive title
        2. Use a different approach to the topic
        3. Add more practical examples
        4. Keep structure and length
        5. Make the article more interesting and dynamic

        Respond in format:
        TITLE: [new title]

        CONTENT:
        [new article text]
        """

        try:
            # Run Together AI call in thread pool to avoid blocking
            response = await asyncio.to_thread(
                self._together_client.chat.completions.create,
                model=self._model,
                messages=[
                    {"role": "system", "content": "You are an experienced technical writer and blogger. You create quality content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )

            content = response.choices[0].message.content
            title, body = self._parse_response(content)

            return PostContent(
                title=title,
                body=body,
                topic=previous_content.topic,
                tags=previous_content.tags
            )

        except Exception as e:
            logger.error(f"Together AI regeneration failed: {e}")
            # Fallback - return slightly modified version
            return PostContent(
                title=f"Updated article: {previous_content.topic}",
                body=f"# Updated article: {previous_content.topic}\n\n{previous_content.body}",
                topic=previous_content.topic,
                tags=previous_content.tags
            )

    def _parse_response(self, content: str) -> tuple[str, str]:
        """Parse Together AI response to extract title and body"""
        lines = content.split('\n')
        title = ""
        body = ""

        capturing_content = False
        for line in lines:
            if line.startswith("TITLE:") or line.startswith("ЗАГОЛОВОК:"):
                title = line.replace("TITLE:", "").replace("ЗАГОЛОВОК:", "").strip()
            elif line.startswith("CONTENT:") or line.startswith("КОНТЕНТ:"):
                capturing_content = True
            elif capturing_content:
                body += line + "\n"

        return (
            title or "Generated article",
            body.strip() or "Content will be added later"
        )

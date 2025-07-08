"""
Telegram Bot Handlers
"""
from typing import Dict, Set
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.core.container import get_container
from app.application.use_cases.create_post import CreatePostUseCase, CreatePostCommand
from app.application.use_cases.confirm_post import ConfirmPostUseCase, ConfirmPostCommand
from app.application.use_cases.publish_post import PublishPostUseCase, PublishPostCommand
from app.application.use_cases.regenerate_content import RegenerateContentUseCase, RegenerateContentCommand
from app.core.logging import get_logger

logger = get_logger(__name__)


class TelegramBotHandlers:
    """Telegram bot handlers"""

    def __init__(self):
        self._waiting_for_topic: Set[int] = set()
        self._user_posts: Dict[int, str] = {}  # user_id -> post_id

    def is_waiting_for_topic(self, user_id: int) -> bool:
        """Check if user is waiting for topic input"""
        return user_id in self._waiting_for_topic

    async def handle_start(self, message: types.Message):
        """Handle /start command"""
        welcome_text = (
            "🤖 **AutoPoster Bot** - AI-powered content generation\n\n"
            "I can help you create and publish articles using AI.\n\n"
            "**Available commands:**\n"
            "/new_post - Create new article\n"
            "/my_posts - View your posts\n"
            "/help - Show this help\n\n"
            "Let's start creating amazing content! 🚀"
        )

        await message.answer(welcome_text, parse_mode="Markdown")

    async def handle_help(self, message: types.Message):
        """Handle /help command"""
        help_text = (
            "📚 **AutoPoster Bot Help**\n\n"
            "**Commands:**\n"
            "/new_post - Create new article with AI\n"
            "/my_posts - View your saved posts\n"
            "/help - Show this help message\n\n"
            "**How to create an article:**\n"
            "1. Use /new_post command\n"
            "2. Enter your topic when prompted\n"
            "3. AI will generate content\n"
            "4. Review and confirm\n"
            "5. Publish to platforms\n\n"
            "**Supported platforms:**\n"
            "• Medium\n"
            "• Dev.to\n"
            "• Reddit\n\n"
            "Need help? Just ask! 💬"
        )

        await message.answer(help_text, parse_mode="Markdown")

    async def handle_new_post(self, message: types.Message):
        """Handle /new_post command"""
        user_id = message.from_user.id

        # Clear any existing state
        self._waiting_for_topic.add(user_id)
        if user_id in self._user_posts:
            del self._user_posts[user_id]

        await message.answer(
            "🎯 **Create New Article**\n\n"
            "Please enter the topic for your article:\n"
            "_(e.g., \"Machine Learning for Beginners\", \"Web Development Tips\")_",
            parse_mode="Markdown"
        )

    async def handle_my_posts(self, message: types.Message):
        """Handle /my_posts command"""
        await message.answer(
            "📝 **Your Posts**\n\n"
            "This feature will show your saved posts.\n"
            "Coming soon! 🔜",
            parse_mode="Markdown"
        )

    async def handle_topic_input(self, message: types.Message):
        """Handle topic input from user"""
        user_id = message.from_user.id
        topic = message.text.strip()

        if not topic:
            await message.answer("Please enter a valid topic.")
            return

        try:
            # Remove from waiting state
            self._waiting_for_topic.discard(user_id)

            # Show processing message
            processing_msg = await message.answer(
                "🧠 **AI is working...**\n\n"
                f"Creating article about: *{topic}*\n"
                "This may take a few seconds...",
                parse_mode="Markdown"
            )

            # Create post using use case
            use_case = get_container().resolve(CreatePostUseCase)
            command = CreatePostCommand(user_id=user_id, topic=topic)
            result = await use_case.execute(command)

            if result.success:
                # Store post ID for this user
                self._user_posts[user_id] = str(result.post_id)

                # Delete processing message
                await processing_msg.delete()

                # Show generated content with actions
                await self._show_post_preview(message, result.post_id, result.content)

            else:
                await processing_msg.edit_text(
                    f"❌ **Error creating post**\n\n{result.error_message}",
                    parse_mode="Markdown"
                )

        except Exception as e:
            logger.error(f"Error handling topic input: {e}")
            await message.answer(
                "❌ **Error**\n\nSomething went wrong. Please try again.",
                parse_mode="Markdown"
            )

    async def handle_callback(self, callback: types.CallbackQuery):
        """Handle callback queries from inline keyboards"""
        try:
            data = callback.data
            user_id = callback.from_user.id

            if not data:
                await callback.answer("Invalid action")
                return

            # Parse callback data
            action, post_id = data.split(":", 1)

            if action == "confirm":
                await self._handle_confirm_post(callback, post_id)
            elif action == "regenerate":
                await self._handle_regenerate_content(callback, post_id)
            elif action == "delete":
                await self._handle_delete_post(callback, post_id)
            elif action == "publish":
                await self._handle_publish_post(callback, post_id)
            else:
                await callback.answer("Unknown action")

        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await callback.answer("Error processing action")

    async def _show_post_preview(self, message: types.Message, post_id: str, content):
        """Show post preview with action buttons"""
        preview_text = (
            "📝 **Article Preview**\n\n"
            f"**Title:** {content.title}\n\n"
            f"**Content:**\n{content.body[:500]}..."
            f"\n\n**Topic:** {content.topic}\n"
            f"**Tags:** {', '.join(content.tags)}"
        )

        # Create inline keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm:{post_id}"),
                InlineKeyboardButton(text="♻️ Regenerate", callback_data=f"regenerate:{post_id}")
            ],
            [
                InlineKeyboardButton(text="❌ Delete", callback_data=f"delete:{post_id}")
            ]
        ])

        await message.answer(
            preview_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    async def _handle_confirm_post(self, callback: types.CallbackQuery, post_id: str):
        """Handle confirm post action"""
        try:
            use_case = get_container().resolve(ConfirmPostUseCase)
            command = ConfirmPostCommand(post_id=post_id)
            result = await use_case.execute(command)

            if result.success:
                # Update message with publish option
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🚀 Publish", callback_data=f"publish:{post_id}")
                    ]
                ])

                await callback.message.edit_text(
                    "✅ **Article Confirmed!**\n\n"
                    "Your article is ready for publishing.\n"
                    "Choose where to publish:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )

            else:
                await callback.answer(f"Error: {result.error_message}")

        except Exception as e:
            logger.error(f"Error confirming post: {e}")
            await callback.answer("Error confirming post")

    async def _handle_regenerate_content(self, callback: types.CallbackQuery, post_id: str):
        """Handle regenerate content action"""
        try:
            await callback.message.edit_text(
                "♻️ **Regenerating content...**\n\n"
                "Please wait while AI creates new version...",
                parse_mode="Markdown"
            )

            use_case = get_container().resolve(RegenerateContentUseCase)
            command = RegenerateContentCommand(post_id=post_id)
            result = await use_case.execute(command)

            if result.success:
                await self._show_post_preview(callback.message, post_id, result.content)
            else:
                await callback.message.edit_text(
                    f"❌ **Error regenerating content**\n\n{result.error_message}",
                    parse_mode="Markdown"
                )

        except Exception as e:
            logger.error(f"Error regenerating content: {e}")
            await callback.answer("Error regenerating content")

    async def _handle_delete_post(self, callback: types.CallbackQuery, post_id: str):
        """Handle delete post action"""
        try:
            # Simple delete - just remove from user's state
            user_id = callback.from_user.id
            if user_id in self._user_posts:
                del self._user_posts[user_id]

            await callback.message.edit_text(
                "❌ **Article Deleted**\n\n"
                "The article has been removed.\n"
                "Use /new_post to create a new one.",
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            await callback.answer("Error deleting post")

    async def _handle_publish_post(self, callback: types.CallbackQuery, post_id: str):
        """Handle publish post action"""
        try:
            await callback.message.edit_text(
                "🚀 **Publishing...**\n\n"
                "Publishing your article to platforms...",
                parse_mode="Markdown"
            )

            use_case = get_container().resolve(PublishPostUseCase)
            command = PublishPostCommand(post_id=post_id)
            result = await use_case.execute(command)

            if result.success:
                # Show publish results
                results_text = "🎉 **Publishing Complete!**\n\n"

                for pub_result in result.publication_results:
                    if pub_result.success:
                        results_text += f"✅ {pub_result.platform.value.title()}: {pub_result.url}\n"
                    else:
                        results_text += f"❌ {pub_result.platform.value.title()}: {pub_result.error_message}\n"

                await callback.message.edit_text(
                    results_text,
                    parse_mode="Markdown"
                )
            else:
                await callback.message.edit_text(
                    f"❌ **Publishing Error**\n\n{result.error_message}",
                    parse_mode="Markdown"
                )

        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            await callback.answer("Error publishing post")

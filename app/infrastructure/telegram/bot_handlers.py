"""
Telegram Bot Handlers
"""
from typing import Dict, Set
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import html

from core.container import get_container
from application.use_cases.create_post import CreatePostUseCase, CreatePostCommand
from application.use_cases.confirm_post import ConfirmPostUseCase, ConfirmPostCommand
from application.use_cases.publish_post import PublishPostUseCase, PublishPostCommand
from application.use_cases.regenerate_content import RegenerateContentUseCase, RegenerateContentCommand
from core.logging import get_logger

logger = get_logger(__name__)


def escape_html(text: str) -> str:
    """Escape text for HTML parsing"""
    if not text:
        return text
    return html.escape(text)


def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text to fit Telegram message limits"""
    if len(text) <= max_length:
        return text

    # Try to truncate at word boundary
    truncated = text[:max_length-3]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # If we can find a space in the last 20%
        truncated = truncated[:last_space]

    return truncated + "..."


async def safe_send_message(message: types.Message, text: str, **kwargs):
    """Safely send message with fallback to plain text if HTML parsing fails"""
    try:
        # Truncate text if too long
        text = truncate_text(text)
        await message.answer(text, **kwargs)
    except Exception as e:
        logger.warning(f"Failed to send HTML message, falling back to plain text: {e}")
        # Remove HTML tags and send as plain text
        plain_text = re.sub(r'<[^>]+>', '', text)
        plain_text = truncate_text(plain_text)
        await message.answer(plain_text, parse_mode=None)


async def safe_edit_message(message: types.Message, text: str, **kwargs):
    """Safely edit message with fallback to plain text if HTML parsing fails"""
    try:
        # Truncate text if too long
        text = truncate_text(text)
        await message.edit_text(text, **kwargs)
    except Exception as e:
        logger.warning(f"Failed to edit HTML message, falling back to plain text: {e}")
        # Remove HTML tags and send as plain text
        plain_text = re.sub(r'<[^>]+>', '', text)
        plain_text = truncate_text(plain_text)
        await message.edit_text(plain_text, parse_mode=None)


class TELEGRAM_BOT_COMMANDS:
    START = "/start"
    HELP = "/help"
    NEW_POST = "/new_post"
    MY_POSTS = "/my_posts"


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
            "🤖 <b>AutoPoster Bot</b> - AI-powered content generation\n\n"
            "I can help you create and publish articles using AI.\n\n"
            "<b>Available commands:</b>\n"
            f"{TELEGRAM_BOT_COMMANDS.NEW_POST} - Create new article\n"
            f"{TELEGRAM_BOT_COMMANDS.MY_POSTS} - View your posts\n"
            f"{TELEGRAM_BOT_COMMANDS.HELP} - Show this help\n\n"
            "Let's start creating amazing content! 🚀"
        )

        await safe_send_message(message, welcome_text, parse_mode="HTML")

    async def handle_help(self, message: types.Message):
        """Handle /help command"""
        help_text = (
            "📚 <b>AutoPoster Bot Help</b>\n\n"
            "<b>Commands:</b>\n"
            f"{TELEGRAM_BOT_COMMANDS.NEW_POST} - Create new article with AI\n"
            f"{TELEGRAM_BOT_COMMANDS.MY_POSTS} - View your saved posts\n"
            f"{TELEGRAM_BOT_COMMANDS.HELP} - Show this help message\n\n"
            "<b>How to create an article:</b>\n"
            f"1. Use {TELEGRAM_BOT_COMMANDS.NEW_POST} command\n"
            "2. Enter your topic when prompted\n"
            "3. AI will generate content\n"
            "4. Review and confirm\n"
            "5. Publish to platforms\n\n"
            "<b>Supported platforms:</b>\n"
            "• Medium\n"
            "• Dev.to\n"
            "• Reddit\n\n"
            "Need help? Just ask! 💬"
        )

        await safe_send_message(message, help_text, parse_mode="HTML")

    async def handle_new_post(self, message: types.Message):
        """Handle /new_post command"""
        user_id = message.from_user.id

        # Clear any existing state
        self._waiting_for_topic.add(user_id)
        if user_id in self._user_posts:
            del self._user_posts[user_id]

        await safe_send_message(
            message,
            "🎯 <b>Create New Article</b>\n\n"
            "Please enter the topic for your article:\n"
            "<i>(e.g., \"Machine Learning for Beginners\", \"Web Development Tips\")</i>",
            parse_mode="HTML"
        )

    async def handle_my_posts(self, message: types.Message):
        """Handle /my_posts command"""
        text = (
            "📝 <b>Your Posts</b>\n\n"
            "This feature will show your saved posts.\n"
            "Coming soon! 🔜"
        )
        await safe_send_message(
            message,
            text,
            parse_mode="HTML"
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
            processing_msg = await safe_send_message(
                message,
                "🧠 <b>AI is working...</b>\n\n"
                f"Creating article about: <b>{escape_html(topic)}</b>\n"
                "This may take a few seconds...",
                parse_mode="HTML"
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
                await safe_edit_message(
                    processing_msg,
                    f"❌ <b>Error creating post</b>\n\n{escape_html(result.error_message)}",
                    parse_mode="HTML"
                )

        except Exception as e:
            logger.error(f"Error handling topic input: {e}")
            await safe_send_message(
                message,
                "❌ <b>Error</b>\n\nSomething went wrong. Please try again.",
                parse_mode="HTML"
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
        # Safely escape content for HTML
        safe_title = escape_html(content.title)
        safe_body = escape_html(content.body[:300])  # Reduced length for preview
        safe_topic = escape_html(content.topic)
        safe_tags = escape_html(', '.join(content.tags[:5]))  # Limit tags

        preview_text = (
            "📝 <b>Article Preview</b>\n\n"
            f"<b>Title:</b> {safe_title}\n\n"
            f"<b>Content:</b>\n{safe_body}..."
            f"\n\n<b>Topic:</b> {safe_topic}\n"
            f"<b>Tags:</b> {safe_tags}"
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

        await safe_send_message(
            message,
            preview_text,
            reply_markup=keyboard,
            parse_mode="HTML"
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

                await safe_edit_message(
                    callback.message,
                    "✅ <b>Article Confirmed!</b>\n\n"
                    "Your article is ready for publishing.\n"
                    "Choose where to publish:",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

            else:
                await callback.answer(f"Error: {result.error_message}")

        except Exception as e:
            logger.error(f"Error confirming post: {e}")
            await callback.answer("Error confirming post")

    async def _handle_regenerate_content(self, callback: types.CallbackQuery, post_id: str):
        """Handle regenerate content action"""
        try:
            await safe_edit_message(
                callback.message,
                "♻️ <b>Regenerating content...</b>\n\n"
                "Please wait while AI creates new version...",
                parse_mode="HTML"
            )

            use_case = get_container().resolve(RegenerateContentUseCase)
            command = RegenerateContentCommand(post_id=post_id)
            result = await use_case.execute(command)

            if result.success:
                await self._show_post_preview(callback.message, post_id, result.content)
            else:
                await safe_edit_message(
                    callback.message,
                    f"❌ <b>Error regenerating content</b>\n\n{escape_html(result.error_message)}",
                    parse_mode="HTML"
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

            await safe_edit_message(
                callback.message,
                "❌ <b>Article Deleted</b>\n\n"
                "The article has been removed.\n"
                f"Use {TELEGRAM_BOT_COMMANDS.NEW_POST} to create a new one.",
                parse_mode="HTML"
            )

        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            await callback.answer("Error deleting post")

    async def _handle_publish_post(self, callback: types.CallbackQuery, post_id: str):
        """Handle publish post action"""
        try:
            await safe_edit_message(
                callback.message,
                "🚀 <b>Publishing...</b>\n\n"
                "Publishing your article to platforms...",
                parse_mode="HTML"
            )

            use_case = get_container().resolve(PublishPostUseCase)
            command = PublishPostCommand(post_id=post_id)
            result = await use_case.execute(command)

            if result.success:
                # Show publish results
                results_text = "🎉 <b>Publishing Complete!</b>\n\n"

                for pub_result in result.publication_results:
                    if pub_result.success:
                        results_text += f"✅ {pub_result.platform.value.title()}: {pub_result.url}\n"
                    else:
                        results_text += f"❌ {pub_result.platform.value.title()}: {escape_html(pub_result.error_message)}\n"

                await safe_edit_message(
                    callback.message,
                    results_text,
                    parse_mode="HTML"
                )
            else:
                await safe_edit_message(
                    callback.message,
                    f"❌ <b>Publishing Error</b>\n\n{escape_html(result.error_message)}",
                    parse_mode="HTML"
                )

        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            await callback.answer("Error publishing post")

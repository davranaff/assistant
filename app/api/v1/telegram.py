from fastapi import APIRouter, Request, HTTPException
from aiogram import Bot, Dispatcher, types

from infrastructure.telegram.bot_handlers import TelegramBotHandlers, TELEGRAM_BOT_COMMANDS
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["telegram"])

# Global bot instance - lazy initialization
bot = None
dp = Dispatcher()
handlers = TelegramBotHandlers()


def get_bot():
    """Get bot instance with lazy initialization"""
    global bot
    if bot is None:
        bot = Bot(token=settings.telegram_bot_token)
    return bot


def setup_bot_handlers():
    """Setup bot message and callback handlers"""

    # Command handlers
    @dp.message(lambda message: message.text == TELEGRAM_BOT_COMMANDS.START)
    async def handle_start_command(message: types.Message):
        await handlers.handle_start(message)

    @dp.message(lambda message: message.text == TELEGRAM_BOT_COMMANDS.HELP)
    async def handle_help_command(message: types.Message):
        await handlers.handle_help(message)

    @dp.message(lambda message: message.text == TELEGRAM_BOT_COMMANDS.NEW_POST)
    async def handle_new_post_command(message: types.Message):
        await handlers.handle_new_post(message)

    @dp.message(lambda message: message.text == TELEGRAM_BOT_COMMANDS.MY_POSTS)
    async def handle_my_posts_command(message: types.Message):
        await handlers.handle_my_posts(message)

    # Text message handler for topic input
    @dp.message(lambda message: message.text and not message.text.startswith("/"))
    async def handle_text_message(message: types.Message):
        user_id = message.from_user.id
        if handlers.is_waiting_for_topic(user_id):
            await handlers.handle_topic_input(message)
        else:
            await message.answer(
                "Use commands:\n"
                f"{TELEGRAM_BOT_COMMANDS.NEW_POST} - create article\n"
                f"{TELEGRAM_BOT_COMMANDS.HELP} - help"
            )

    # Callback query handler
    @dp.callback_query()
    async def handle_callback_query(callback: types.CallbackQuery):
        await handlers.handle_callback(callback)


# Setup handlers when module is imported
setup_bot_handlers()


@router.post("/webhook")
async def webhook(request: Request):
    """Handle Telegram webhook"""
    try:
        # Get update from request
        update_data = await request.json()

        logger.info(f"Received webhook update: {update_data.get('update_id')}")

        # Create Update object
        update = types.Update(**update_data)

        # Process update
        await dp.feed_update(bot=get_bot(), update=update)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/set_webhook")
async def set_webhook():
    """Set webhook URL"""
    try:
        logger.info(f"Current webhook_base_url: {settings.webhook_base_url}")
        webhook_url = f"{settings.webhook_base_url}/api/v1/telegram/webhook"
        logger.info(f"Setting webhook to: {webhook_url}")

        await get_bot().set_webhook(
            url=webhook_url,
            drop_pending_updates=False
        )

        logger.info(f"Webhook set to: {webhook_url}")

        return {
            "status": "ok",
            "webhook_url": webhook_url
        }

    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/webhook")
async def delete_webhook():
    """Delete webhook"""
    try:
        await get_bot().delete_webhook(drop_pending_updates=True)

        logger.info("Webhook deleted")

        return {"status": "ok", "message": "Webhook deleted"}

    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhook/info")
async def get_webhook_info():
    """Get webhook info"""
    try:
        webhook_info = await get_bot().get_webhook_info()

        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }

    except Exception as e:
        logger.error(f"Failed to get webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_bot_info():
    """Get bot information"""
    try:
        bot_info = await get_bot().get_me()

        return {
            "id": bot_info.id,
            "is_bot": bot_info.is_bot,
            "first_name": bot_info.first_name,
            "username": bot_info.username,
            "can_join_groups": bot_info.can_join_groups,
            "can_read_all_group_messages": bot_info.can_read_all_group_messages,
            "supports_inline_queries": bot_info.supports_inline_queries
        }

    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Cleanup function
async def cleanup_bot():
    """Cleanup bot session"""
    if bot is not None:
        await bot.session.close()

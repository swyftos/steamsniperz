# src/handlers/login.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
import os
from dotenv import load_dotenv

from src.constant import ConversationState
from src.handlers.common import cancel_handler
from src.modules.bot_context import BotContext
from src.modules.middleware import update_user
from src.modules.reddit_manager import RedditManager

load_dotenv()

def _get_keys():
    return os.getenv("REDDIT_CLIENT_ID"), os.getenv("REDDIT_CLIENT_SECRET")

async def login_command_handler(update: Update, context: BotContext):
    if context.reddit:
        await update.message.reply_text(
            "You are already authenticated. Please use /logout to logout."
        )
        return ConversationState.END

    client_id, client_secret = _get_keys()
    if not client_id or not client_secret:
        await update.message.reply_text(
            "Missing REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET in .env"
        )
        return ConversationState.END

    auth_url = RedditManager.create_auth_url(
        update.message.from_user.id, client_id=client_id, client_secret=client_secret
    )

    keyboard = [[InlineKeyboardButton("Authenticate Reddit", url=auth_url)]]
    await update.message.reply_text(
        "Open the URL, authorize on Reddit, puis COPIE le paramètre 'code' de l’URL et colle-le ici.\n\n<i>Send /cancel to cancel</i>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )
    return ConversationState.WAITING_FOR_AUTH_CODE

async def auth_code_handler(update: Update, context: BotContext):
    auth_code = (update.message.text or "").strip()
    user_id = update.message.from_user.id

    client_id, client_secret = _get_keys()
    refresh_token, username = RedditManager.authorize_user(
        user_id, auth_code, client_id=client_id, client_secret=client_secret
    )
    context.user.refresh_token = refresh_token
    context.user.save()

    update_user(update, context, user_id)
    await update.message.reply_text(f"Reddit authenticated successfully as u/{username}")
    return ConversationState.END

async def logout_command_handler(update: Update, context: BotContext):
    context.user.refresh_token = None
    context.user.save()
    context.user_data.pop("reddit", None)
    context.user_data.pop("user", None)
    await update.message.reply_text("Reddit logged out successfully")
    return ConversationState.END

def get_login_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("login", login_command_handler)],
        states={
            ConversationState.WAITING_FOR_AUTH_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, auth_code_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )

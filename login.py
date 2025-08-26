# src/handlers/login.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters

import os
from dotenv import load_dotenv

from src.constant import ConversationState
from src.database import db
from src.handlers.common import cancel_handler
from src.modules.bot_context import BotContext
from src.modules.middleware import update_user
from src.modules.reddit_manager import RedditManager

# charge .env (si c'est déjà fait ailleurs, ce n'est pas gênant de l'appeler à nouveau)
load_dotenv()

def _get_reddit_app_keys():
    """Lit les clés app Reddit depuis l'environnement .env"""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    return client_id, client_secret


async def login_command_handler(update: Update, context: BotContext):
    # si déjà authentifié
    if context.reddit:
        await update.message.reply_text(
            "You are already authenticated. Please use /logout to logout."
        )
        return ConversationState.END

    # lire les clés app reddit depuis .env
    client_id, client_secret = _get_reddit_app_keys()
    if not client_id or not client_secret:
        await update.message.reply_text(
            "Reddit app keys are missing. Please set REDDIT_CLIENT_ID and "
            "REDDIT_CLIENT_SECRET in your .env and restart the bot."
        )
        return ConversationState.END

    # créer l'URL d'autorisation (le repo attend ensuite que tu colles le code)
    auth_url = RedditManager.create_auth_url(
        update.message.from_user.id,
        client_id=client_id,
        client_secret=client_secret,
    )

    keyboard = [[InlineKeyboardButton("Authenticate Reddit", url=auth_url)]]
    await update.message.reply_text(
        (
            "Please visit this URL and authenticate with Reddit.\n"
            "Then copy the 'code' you see in the URL bar and paste it here.\n\n"
            "<i>Send /cancel to cancel the process</i>"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )
    return ConversationState.WAITING_FOR_AUTH_CODE


async def auth_code_handler(update: Update, context: BotContext):
    auth_code = (update.message.text or "").strip()
    if not auth_code:
        await update.message.reply_text("Please paste the authorization code from Reddit.")
        return ConversationState.WAITING_FOR_AUTH_CODE

    user_id = update.message.from_user.id

    # relire les clés app reddit depuis .env
    client_id, client_secret = _get_reddit_app_keys()
    if not client_id or not client_secret:
        await update.message.reply_text(
            "Reddit app keys are missing. Set REDDIT_CLIENT_ID/SECRET and try again."
        )
        return ConversationState.END

    # échange code -> refresh_token
    refresh_token, username = RedditManager.authorize_user(
        user_id, auth_code, client_id=client_id, client_secret=client_secret
    )

    # persister le token côté "user" du repo
    context.user.refresh_token = refresh_token
    context.user.save()

    # mettre à jour le contexte (le repo l’utilise ensuite)
    update_user(update, context, user_id)

    await update.message.reply_text(f"Reddit authenticated successfully as u/{username}")
    return ConversationState.END


async def logout_command_handler(update: Update, context: BotContext):
    context.user.refresh_token = None
    context.user.save()

    # PTB v20 : utiliser user_data
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

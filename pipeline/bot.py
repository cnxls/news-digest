import asyncio as aio
from telegram.ext import Application
from pipeline.database import Database
from pipeline.config import settings

db = Database(settings.database_url)
app = Application.builder().token(settings.telegram_bot_token).build()


async def start(update, context):
    chat_id = update.effective_chat.id
    db.add_subscriber(chat_id=chat_id)
    await update.message.reply_text("Hi! Use /subscribe ... to pick topics.")

async def subscribe(update, context):
    chat_id = update.effective_chat.id
    categories = context.args

    if not categories:
        await update.message.reply_text("Use: /subscribe tech finance")
        return
    
    valid = ["tech", "finance"]
    not_valid = [c for c in categories if c not in valid]
    if not_valid:
        await update.message.reply_text(f"Unknown category : {not_valid}")
        return
    
    db.update_categories(categories=categories, chat_id=chat_id)
    await update.message.reply_text(f"Subscribed to :{', '.join(categories)}")
    
async def unsubscribe(update, context):
    chat_id = update.effective_chat.id
    db.remove_subscriber(chat_id)
    await update.message.reply_text("Unsubscribed. Use /start to come back anytime.")
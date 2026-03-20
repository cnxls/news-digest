from telegram.ext import Application,CommandHandler
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


async def todays_digest(update, context):
    chat_id = update.effective_chat.id
    categories = db.get_categories(chat_id=chat_id)
    if not categories:
        await update.message.reply_text("No categories selected. Use /subscribe to choose.")
        return
    digests = db.get_unsent_digest_for_user(categories, chat_id)
    if not digests:
        await update.message.reply_text("No new digests available.")
        return
    for digest in digests:
        await update.message.reply_text(digest["content"])
        db.record_delivery(digest["id"], chat_id=chat_id)


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CommandHandler("digest", todays_digest))

if __name__ == "__main__":
    db.connect()
    db.init_tables()
    app.run_polling()
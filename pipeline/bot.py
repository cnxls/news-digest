from telegram.ext import Application,CommandHandler
from pipeline.database import Database
from pipeline.config import settings, get_valid_categories

db = Database(settings.database_url)
app = Application.builder().token(settings.telegram_bot_token).build()

async def start(update, context):
    chat_id = update.effective_chat.id
    db.add_subscriber(chat_id=chat_id)
    await update.message.reply_text("Hi! Use /subscribe ... to pick topics.")

async def subscribe(update, context):
    chat_id = update.effective_chat.id
    
    categories = context.args
    current_cats = db.get_categories(chat_id=chat_id) or []

    if not categories:
        await update.message.reply_text("Use: /subscribe categories")
        return
    
    valid = get_valid_categories()
    not_valid = [c for c in categories if c not in valid]
    if not_valid:
        await update.message.reply_text(f"Unknown category : {not_valid}")
        return
    
    resulting_list = list(current_cats)
    resulting_list.extend(cat for cat in categories if cat not in resulting_list)
    
    db.update_categories(categories=resulting_list, chat_id=chat_id)
    await update.message.reply_text(f"Subscribed to : {', '.join(categories)}")
    


async def unsubscribe(update, context):
    chat_id = update.effective_chat.id
    categories_to_remove = context.args

    if not categories_to_remove:
        db.remove_subscriber(chat_id)
        await update.message.reply_text("Unsubscribed from all topics.\nUse /start to come back anytime.")
        return

    valid = get_valid_categories()
    not_valid = [c for c in categories_to_remove if c not in valid]
    if not_valid:
        await update.message.reply_text(f"Unknown categories: {', '.join(not_valid)}")
        return

    current = db.get_categories(chat_id=chat_id)
    if not current:
        await update.message.reply_text("You have no active subscriptions.")
        return

    remaining = [c for c in current if c not in categories_to_remove]
    if not remaining:
        db.remove_subscriber(chat_id)
        await update.message.reply_text("Unsubscribed from all topics.\nUse /start to come back anytime.")
        return

    db.update_categories(categories=remaining, chat_id=chat_id)
    removed = [c for c in categories_to_remove if c in current]
    await update.message.reply_text(
        f"Removed: {', '.join(removed)}\n"
        f"Still subscribed to: {', '.join(remaining)}"
    )


async def todays_digest(update, context):
    chat_id = update.effective_chat.id
    categories = db.get_categories(chat_id=chat_id)
    if not categories:
        await update.message.reply_text("No categories selected. Use /subscribe to choose.")
        return

    valid = get_valid_categories()

    if context.args:
        category = context.args[0].lower()
        if category not in valid:
            await update.message.reply_text(f"Unknown category: {category}\nAvailable: {', '.join(valid)}")
            return
        if category not in categories:
            await update.message.reply_text(f"You're not subscribed to '{category}'. Use /subscribe {category} first.")
            return
        digest = db.get_todays_digest_by_category(category)
        if not digest:
            await update.message.reply_text(f"No digest for '{category}' today yet.")
            return
        await update.message.reply_text(digest["content"], parse_mode="HTML")
        db.record_delivery(digest["id"], chat_id=chat_id)
        return

    digests = db.get_unsent_digest_for_user(categories, chat_id)
    if not digests:
        await update.message.reply_text("No new digests available.")
        return
    for digest in digests:
        await update.message.reply_text(digest["content"], parse_mode="HTML")
        db.record_delivery(digest["id"], chat_id=chat_id)

async def help(update, context):
    await update.message.reply_text(
        "<b>Available commands:</b>\n\n"
        "/start — Register and get started\n"
        "/subscribe &lt;categories&gt; — Subscribe to topics\n"
        "/unsubscribe — Unsubscribe from all updates\n"
        "/digest &lt;category&gt; — Get today's latest digest (or all unsent if no category)\n"
        "/mysubs — View your current subscriptions\n"
        "/help — Show this message\n\n"
        f"<b>Categories:</b> {', '.join(get_valid_categories())}\n\n"
        "<i>Example:</i> /subscribe tech finance crypto",
        parse_mode="HTML"
    )

async def mysubs(update, context):
    chat_id = update.effective_chat.id
    categories = db.get_categories(chat_id=chat_id)
    if not categories:
        await update.message.reply_text("You have no active subscriptions.\nUse /subscribe to choose topics.")
        return 
    cat_list = "\n".join(f"  • {c}" for c in categories)
    await update.message.reply_text(f"You are subscribed to : \n\n{cat_list}")


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CommandHandler("digest", todays_digest))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("mysubs", mysubs))

if __name__ == "__main__":
    db.connect()
    db.init_tables()
    app.run_polling()
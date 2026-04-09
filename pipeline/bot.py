from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from pipeline.database import Database
from pipeline.config import settings, get_valid_categories

db = Database(settings.database_url)
app = Application.builder().token(settings.telegram_bot_token).build()
categories = get_valid_categories()

CAT_LIST = "\n".join(f" • {cat}" for cat in categories)
VALID_LANGUAGES = {'eng': 'en', 'ukr': 'uk'}
LANGUAGE_LABELS = {'en': 'English', 'uk': 'Ukrainian'}



async def start(update, context):
    chat_id = update.effective_chat.id
    db.add_subscriber(chat_id=chat_id)
    message = (
        "📰 <b>Welcome to News Digest!</b>\n"
        "I collect and summarize news from across the web and deliver it here.\n\n"
        "👇 Pick your topics to get started:"
    )
    buttons = [[InlineKeyboardButton(cat, callback_data=f"sub:{cat}")] for cat in get_valid_categories()]
    await update.message.reply_text(message, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def subscribe(update, context):
    chat_id = update.effective_chat.id
    
    categories = context.args
    current_cats = db.get_categories(chat_id=chat_id) or []

    if not categories:
        await update.message.reply_text(
            f"Please specify categories.\n\n<b>Available:</b>\n{CAT_LIST}\n\n<i>Example:</i> <code>/subscribe tech finance</code>",
            parse_mode="HTML"
        )
        return
    
    valid = get_valid_categories()
    not_valid = [c for c in categories if c not in valid]
    if not_valid:
        await update.message.reply_text(f"Unknown category: {', '.join(not_valid)}")
        return
    
    resulting_list = list(current_cats)
    resulting_list.extend(cat for cat in categories if cat not in resulting_list)
    
    db.update_categories(categories=resulting_list, chat_id=chat_id)
    await update.message.reply_text(f"""Subscribed to : {', '.join(categories)}\nYour active subscribtions:{" ,".join(current_cats)}""")


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

    lang = db.get_language(chat_id=chat_id)
    valid = get_valid_categories()

    if context.args:
        category = context.args[0].lower()
        if category not in valid:
            await update.message.reply_text(f"Unknown category: {category}\nAvailable: {', '.join(valid)}")
            return
        if category not in categories:
            await update.message.reply_text(f"You're not subscribed to '{category}'. Use /subscribe {category} first.")
            return
        digest = db.get_todays_digest_by_category(category, language=lang)
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

async def status(update, context):
    chat_id = update.effective_chat.id
    current_cats = db.get_categories(chat_id) or []
    user_cat_list = ", ".join(current_cats) if current_cats else "None — use /subscribe to choose"
    user_language = LANGUAGE_LABELS.get(db.get_language(chat_id), "English")
    user_unsent_digest = len(db.get_unsent_digest_for_user(current_cats, chat_id)) if current_cats else 0
    message = (
        "📊 <b>Your Status</b>\n\n"
        f"Subscriptions: <b>{user_cat_list}</b>\n"
        f"Language: {user_language}\n"
        f"Digests waiting: <b>{user_unsent_digest}</b> → use /digest to read them\n"
        "Schedule: refreshed every 8 hours"
    )
    await update.message.reply_text(message, parse_mode="HTML")

async def help(update, context):
    await update.message.reply_text(
        "<b>Available commands:</b>\n\n"
        "/start — Register and get started\n"
        "/subscribe &lt;categories&gt; — Subscribe to topics\n"
        "/unsubscribe — Unsubscribe from all updates\n"
        "/digest &lt;category&gt; — Get today's latest digest (or all unsent if no category)\n"
        "/language &lt;eng|ukr&gt; — Set digest language\n"
        "/status — Your subscriptions and pending digests\n"
        "/mysubs — View your current subscriptions\n"
        "/help — Show this message\n\n"
        f"<b>Categories:</b> {', '.join(get_valid_categories())}\n\n"
        "<i>Example:</i> /subscribe tech finance crypto",
        parse_mode="HTML"
    )

async def language(update, context):
    chat_id = update.effective_chat.id
    if not context.args:
        current = db.get_language(chat_id=chat_id)
        label = LANGUAGE_LABELS.get(current, current)
        buttons = [[
            InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton("🇺🇦 Ukrainian", callback_data="lang:uk"),
        ]]
        await update.message.reply_text(
            f"Current language: <b>{label}</b>\nChoose a language:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    choice = context.args[0].lower()
    if choice not in VALID_LANGUAGES:
        await update.message.reply_text(
            f"Unknown language: {choice}\n"
            f"Available: {', '.join(VALID_LANGUAGES.keys())}"
        )
        return

    lang_code = VALID_LANGUAGES[choice]
    db.update_language(language=lang_code, chat_id=chat_id)
    label = LANGUAGE_LABELS[lang_code]
    await update.message.reply_text(f"Language set to {label}.")

async def mysubs(update, context):
    chat_id = update.effective_chat.id
    categories = db.get_categories(chat_id=chat_id)
    if not categories:
        await update.message.reply_text("You have no active subscriptions.\nUse /subscribe to choose topics.")
        return
    lang = db.get_language(chat_id=chat_id)
    label = LANGUAGE_LABELS.get(lang, lang)
    cat_list = "\n".join(f"  • {c}" for c in categories)
    await update.message.reply_text(f"You are subscribed to:\n\n{cat_list}\n\nLanguage: {label}")


async def handle_lang_cb(update, context):
    query = update.callback_query
    await query.answer()

    lang_code = query.data.split(":")[1]
    db.update_language(language=lang_code, chat_id=query.message.chat_id)
    label = LANGUAGE_LABELS[lang_code]

    await query.edit_message_text(f"✅ Language set to <b>{label}</b>.", parse_mode="HTML")


async def handle_sub_cb(update, context):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    cat = query.data.split(":")[1]
    current_cats = db.get_categories(chat_id=chat_id) or []

    if cat not in current_cats:
        current_cats = current_cats + [cat]
        db.update_categories(categories=current_cats, chat_id=chat_id)

    await query.edit_message_text(
        f"✅ Subscribed to <b>{cat}</b>.\nActive subscriptions: {', '.join(current_cats)}\n\nUse /subscribe to add more.",
        parse_mode="HTML"
    )


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CommandHandler("digest", todays_digest))
app.add_handler(CommandHandler("language", language))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("mysubs", mysubs))
app.add_handler(CommandHandler("status", status))
app.add_handler(CallbackQueryHandler(handle_lang_cb, pattern="^lang:"))
app.add_handler(CallbackQueryHandler(handle_sub_cb, pattern="^sub:"))

if __name__ == "__main__":
    db.connect()
    db.init_tables()
    app.run_polling()
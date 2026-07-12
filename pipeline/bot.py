from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pipeline.database import Database
from pipeline.config import settings, get_valid_categories, get_sources_by_category
from pipeline.logger import get_logger

logger = get_logger()

app = Application.builder().token(settings.telegram_bot_token).build()

CAT_LIST = "\n".join(f" • {cat}" for cat in get_valid_categories())
VALID_LANGUAGES = {'eng': 'en', 'ukr': 'uk'}
LANGUAGE_LABELS = {'en': 'English', 'uk': 'Ukrainian'}


async def start(update, context):
    chat_id = update.effective_chat.id
    with Database(settings.database_url) as db:
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
    categories = get_valid_categories()
    selected_categories = context.args

    with Database(settings.database_url) as db:
        current_cats = db.get_user_subscriptions(chat_id=chat_id) or []

    if not context.args:
        buttons = [[InlineKeyboardButton(cat, callback_data=f"sub:{cat}")] for cat in get_valid_categories()]
        await update.message.reply_text(
            f"Current subscriptions: <b>{', '.join(current_cats)}</b>\nChoose category to subscribe to:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if not categories:
        await update.message.reply_text(
            f"Please specify categories.\n\n<b>Available:</b>\n{CAT_LIST}\n\n<i>Example:</i> <code>/subscribe tech finance</code>",
            parse_mode="HTML"
        )
        return

    valid = get_valid_categories()
    not_valid = [c for c in selected_categories if c not in valid]
    if not_valid:
        await update.message.reply_text(f"Unknown category: {', '.join(not_valid)}")
        return

    resulting_list = list(current_cats)
    resulting_list.extend(cat for cat in selected_categories if cat not in resulting_list)

    with Database(settings.database_url) as db:
        db.update_categories(categories=resulting_list, chat_id=chat_id)
    await update.message.reply_text(f"Subscribed to: {', '.join(selected_categories)}\nYour active subscriptions: {', '.join(current_cats)}")


async def unsubscribe(update, context):
    chat_id = update.effective_chat.id
    categories_to_remove = context.args

    if not categories_to_remove:
        buttons = [[
            InlineKeyboardButton("Yes", callback_data="unsub:confirm"),
            InlineKeyboardButton("No", callback_data="unsub:cancel")
        ]]
        await update.message.reply_text("Are you sure you want to unsubscribe from all the categories?",
                                        reply_markup=InlineKeyboardMarkup(buttons))
        return

    valid = get_valid_categories()
    not_valid = [c for c in categories_to_remove if c not in valid]
    if not_valid:
        await update.message.reply_text(f"Unknown categories: {', '.join(not_valid)}")
        return

    with Database(settings.database_url) as db:
        current = db.get_user_subscriptions(chat_id=chat_id)
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
    with Database(settings.database_url) as db:
        categories = db.get_user_subscriptions(chat_id=chat_id)
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
    with Database(settings.database_url) as db:
        current_cats = db.get_user_subscriptions(chat_id) or []
        user_language = LANGUAGE_LABELS.get(db.get_language(chat_id), "English")
        user_unsent_digest = len(db.get_unsent_digest_for_user(current_cats, chat_id)) if current_cats else 0
    user_cat_list = ", ".join(current_cats) if current_cats else "None — use /subscribe to choose"
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
        "📖 <b>News Digest — Commands</b>\n\n"
        "<b>🚀 Getting started</b>\n"
        "/start — Register and pick your topics\n"
        "/subscribe — Add categories  ·  <code>/subscribe tech finance</code>\n"
        "/unsubscribe — Remove categories or leave\n\n"
        "<b>📰 Your news</b>\n"
        "/digest — Read today's digest  ·  <code>/digest crypto</code>\n"
        "/status — Your subscriptions &amp; pending digests\n"
        "/sources — See where your news comes from  ·  <code>/sources tech</code>\n\n"
        "<b>⚙️ Settings</b>\n"
        "/language — Switch language  ·  <code>eng | ukr</code>\n"
        "/help — Show this message\n\n"
        f"<b>Categories:</b> <i>{', '.join(get_valid_categories())}</i>",
        parse_mode="HTML"
    )

async def sources(update, context):
    by_cat = get_sources_by_category()
    if context.args:
        cat = context.args[0].lower()
        if cat not in by_cat:
            await update.message.reply_text(f"Unknown category: {cat}\nAvailable: {', '.join(by_cat)}")
            return
        feed_list = "\n".join(f" • {name}" for name in by_cat[cat])
        await update.message.reply_text(
            f"📡 <b>Sources for {cat}:</b>\n{feed_list}",
            parse_mode="HTML"
        )
        return

    lines = []
    for cat, feeds in by_cat.items():
        lines.append(f"<b>{cat}</b> ({len(feeds)} feeds)")
        lines.extend(f" • {name}" for name in feeds)
        lines.append("")
    await update.message.reply_text(
        f"📡 <b>All News Sources</b>\n\n" + "\n".join(lines),
        parse_mode="HTML"
    )


async def language(update, context):
    chat_id = update.effective_chat.id
    if not context.args:
        with Database(settings.database_url) as db:
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
    with Database(settings.database_url) as db:
        db.update_language(language=lang_code, chat_id=chat_id)
    label = LANGUAGE_LABELS[lang_code]
    await update.message.reply_text(f"Language set to {label}.")

async def handle_lang_cb(update, context):
    query = update.callback_query
    await query.answer()

    lang_code = query.data.split(":")[1]
    with Database(settings.database_url) as db:
        db.update_language(language=lang_code, chat_id=query.message.chat_id)
    label = LANGUAGE_LABELS[lang_code]
    await query.edit_message_text(f"✅ Language set to <b>{label}</b>.", parse_mode="HTML")


async def handle_sub_cb(update, context):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    cat = query.data.split(":")[1]

    if cat == "done":
        await query.edit_message_text(
            "All set! Use /digest to read today's news.",
            parse_mode="HTML"
        )
        return

    with Database(settings.database_url) as db:
        current_cats = db.get_user_subscriptions(chat_id=chat_id) or []
        if cat not in current_cats:
            current_cats = current_cats + [cat]
            db.update_categories(categories=current_cats, chat_id=chat_id)

    buttons = [[InlineKeyboardButton(
        f"✅ {c}" if c in current_cats else c,
        callback_data=f"sub:{c}"
    )] for c in get_valid_categories()]
    buttons.append([InlineKeyboardButton("✅ Done", callback_data="sub:done")])

    await query.edit_message_text(
        f"Active subscriptions: <b>{', '.join(current_cats)}</b>\n\nPick more or use /digest to read today's news.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_unsub_cb(update, context):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    ans = query.data.split(":")[1]

    with Database(settings.database_url) as db:
        current_cats = db.get_user_subscriptions(chat_id=chat_id) or []
        if ans == "confirm":
            if not current_cats:
                await query.edit_message_text("You have no active subscriptions.\nUse /subscribe to choose topics.", parse_mode="HTML")
                return
            db.update_categories([], chat_id=chat_id)
            await query.edit_message_text(
                "✅ Unsubscribed from all topics.\nUse /start to come back anytime.",
                parse_mode="HTML"
            )
        else:
            await query.edit_message_text(
                "Cancelled. Your subscriptions are unchanged.",
                parse_mode="HTML"
            )


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CommandHandler("digest", todays_digest))
app.add_handler(CommandHandler("language", language))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("sources", sources))
app.add_handler(CommandHandler("status", status))
app.add_handler(CallbackQueryHandler(handle_lang_cb, pattern="^lang:"))
app.add_handler(CallbackQueryHandler(handle_sub_cb, pattern="^sub:"))
app.add_handler(CallbackQueryHandler(handle_unsub_cb, pattern="^unsub:"))

def pipeline_task():
    from pipeline.collectors import run_collect
    from main import summarize_all_languages
    logger.info("Scheduled pipeline run started")
    run_collect()
    for cat in get_valid_categories():
        summarize_all_languages(category=cat)
    logger.info("Scheduled pipeline run complete")


if __name__ == "__main__":
    with Database(settings.database_url) as db:
        db.init_tables()

    scheduler = BackgroundScheduler()
    scheduler.add_job(pipeline_task, trigger='interval', hours=8, next_run_time=__import__('datetime').datetime.now())
    scheduler.start()

    app.run_polling()

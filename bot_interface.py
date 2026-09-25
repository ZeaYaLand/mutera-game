"""Telegram UI adapter for the Mutera game session."""
import os
from mutera.game import GameSession

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

SESSIONS = {}


def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧬 Организм", callback_data="inspect"), InlineKeyboardButton("🌍 Исследовать", callback_data="explore")],
        [InlineKeyboardButton("🍎 Кормить", callback_data="feed"), InlineKeyboardButton("💚 Лечить", callback_data="heal")],
        [InlineKeyboardButton("▶️ Следующий ход", callback_data="act")],
    ])


def get_session(user_id):
    if user_id not in SESSIONS:
        SESSIONS[user_id] = GameSession.new(str(user_id))
    return SESSIONS[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(update.effective_user.id)
    await update.message.reply_text(
        "🧬 MUTERA\n\nПервый организм создан. Твоя эволюция начинается.",
        reply_markup=keyboard(),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    session = get_session(query.from_user.id)
    action = query.data

    if action == "inspect":
        result = session.inspect()
        text = f"🧬 MUTERA\nОрганизмов: {result['game']['world']['total']}\nЖивых: {result['game']['world']['living']}\nПоколение: {result['game']['world']['generations']}\nТемпература: {result['game']['temperature']:.1f}°C"
    elif action == "explore":
        text = session.explore()
    elif action == "feed":
        text = session.feed()
    elif action == "heal":
        text = session.heal()
    else:
        result = session.act()
        text = f"▶️ Ход {result['world']['turn']} завершён. Живых организмов: {result['world']['living']}"

    await query.edit_message_text(text, reply_markup=keyboard())


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()


if __name__ == "__main__":
    main()

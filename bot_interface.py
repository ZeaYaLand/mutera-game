"""Telegram UI adapter for the Mutera game session."""
import os
from mutera.game import GameSession

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

SESSIONS = {}


def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧬 Организм", callback_data="inspect"), InlineKeyboardButton("🧬 Геном", callback_data="genome")],
        [InlineKeyboardButton("🌍 Исследовать", callback_data="explore"), InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("🍎 Кормить", callback_data="feed"), InlineKeyboardButton("💚 Лечить", callback_data="heal")],
        [InlineKeyboardButton("▶️ Следующий ход", callback_data="act")],
    ])


def get_session(user_id):
    if user_id not in SESSIONS:
        SESSIONS[user_id] = GameSession.new(str(user_id))
    return SESSIONS[user_id]


def render_inspect(session):
    result = session.inspect()
    o = result["organism"]
    w = result["game"]["world"]
    return (
        "🧬 <b>ТВОЙ ОРГАНИЗМ</b>\n\n"
        f"ID: <code>{o['id']}</code>\n"
        f"Поколение: <b>{o['generation']}</b>\n"
        f"Возраст: {o['age']}\n"
        f"Энергия: {o['energy']:.1f}/100\n"
        f"Здоровье: {o['health']:.1f}/100\n\n"
        f"🌍 Живых в мире: {w['living']}\n"
        f"🌡 Температура: {result['game']['temperature']:.1f}°C"
    )


def render_genome(session):
    o = session.inspect()["organism"]
    return f"🧬 <b>ГЕНОМ</b>\n\n<code>{o['genome']}</code>\n\nПоколение: {o['generation']}"


def render_stats(session):
    result = session.inspect()
    p = result["player"]
    g = result["game"]
    return (
        "📊 <b>СТАТИСТИКА</b>\n\n"
        f"Ходов: {p['statistics'].get('turns', 0)}\n"
        f"Исследований: {p['statistics'].get('explorations', 0)}\n"
        f"Кормлений: {p['statistics'].get('feeds', 0)}\n"
        f"Лечений: {p['statistics'].get('heals', 0)}\n"
        f"Биомов открыто: {p['biomes']}\n"
        f"Видов открыто: {p['species']}\n"
        f"Поворот мира: {g['world']['turn']}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_session(update.effective_user.id)
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
        text = render_inspect(session)
    elif action == "genome":
        text = render_genome(session)
    elif action == "stats":
        text = render_stats(session)
    elif action == "explore":
        result = session.explore()
        text = f"🌍 <b>ИССЛЕДОВАНИЕ</b>\n\nКоординаты: {result['position']}\nБиом: <b>{result['biome']}</b>"
    elif action == "feed":
        result = session.feed()
        text = "🍎 Организм накормлен." if result["ok"] else f"⚠️ {result['message']}"
    elif action == "heal":
        result = session.heal()
        text = "💚 Здоровье восстановлено." if result["ok"] else f"⚠️ {result['message']}"
    else:
        result = session.act()
        text = f"▶️ <b>ХОД {result['world']['turn']}</b>\n\nЖивых организмов: {result['world']['living']}\nПоколение: {result['world']['generations']}"

    await query.edit_message_text(text, reply_markup=keyboard(), parse_mode="HTML")


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

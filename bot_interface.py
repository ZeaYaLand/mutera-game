"""Telegram UI adapter for the Mutera game session."""
import os
from mutera.game import GameSession
from mutera.storage import SessionStore
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

SESSIONS = {}
STORE = SessionStore(os.environ.get("MUTERA_DATA_DIR", "data/sessions"))


def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧬 Организм", callback_data="inspect"), InlineKeyboardButton("🧬 Геном", callback_data="genome")],
        [InlineKeyboardButton("🌍 Исследовать", callback_data="explore"), InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("🍎 Кормить", callback_data="feed"), InlineKeyboardButton("💚 Лечить", callback_data="heal")],
        [InlineKeyboardButton("💾 Сохранить", callback_data="save"), InlineKeyboardButton("▶️ Следующий ход", callback_data="act")],
    ])


def get_session(user_id):
    if user_id not in SESSIONS:
        SESSIONS[user_id] = STORE.load(user_id) or GameSession.new(str(user_id))
    return SESSIONS[user_id]


def persist(user_id, session):
    STORE.save(user_id, session)


def render_inspect(session):
    result = session.inspect(); o = result["organism"]; w = result["game"]["world"]
    return (f"🧬 <b>ТВОЙ ОРГАНИЗМ</b>\n\nID: <code>{o['id']}</code>\n"
            f"Поколение: <b>{o['generation']}</b>\nВозраст: {o['age']}\n"
            f"Энергия: {o['energy']:.1f}/100\nЗдоровье: {o['health']:.1f}/100\n\n"
            f"🌍 Живых: {w['living']}\n🌡 Температура: {result['game']['temperature']:.1f}°C")


def render_genome(session):
    o = session.inspect()["organism"]
    return f"🧬 <b>ГЕНОМ</b>\n\n<code>{o['genome']}</code>\n\nПоколение: {o['generation']}"


def render_stats(session):
    r = session.inspect(); p = r["player"]; g = r["game"]
    return ("📊 <b>СТАТИСТИКА</b>\n\n"
            f"Ходов: {p['statistics'].get('turns', 0)}\nИсследований: {p['statistics'].get('explorations', 0)}\n"
            f"Кормлений: {p['statistics'].get('feeds', 0)}\nЛечений: {p['statistics'].get('heals', 0)}\n"
            f"Биомов: {p['biomes']}\nВидов: {p['species']}\nХод мира: {g['world']['turn']}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(update.effective_user.id)
    persist(update.effective_user.id, session)
    await update.message.reply_text("🧬 MUTERA\n\nТвоя игровая сессия загружена. Эволюция продолжается.", reply_markup=keyboard())


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    user_id = query.from_user.id; session = get_session(user_id); action = query.data
    if action == "inspect": text = render_inspect(session)
    elif action == "genome": text = render_genome(session)
    elif action == "stats": text = render_stats(session)
    elif action == "explore":
        r = session.explore(); text = f"🌍 <b>ИССЛЕДОВАНИЕ</b>\n\nКоординаты: {r['position']}\nБиом: <b>{r['biome']}</b>"
    elif action == "feed":
        r = session.feed(); text = "🍎 Организм накормлен." if r["ok"] else f"⚠️ {r['message']}"
    elif action == "heal":
        r = session.heal(); text = "💚 Здоровье восстановлено." if r["ok"] else f"⚠️ {r['message']}"
    elif action == "save":
        persist(user_id, session); text = "💾 <b>Сохранено.</b> Прогресс записан."
    else:
        r = session.act(); text = f"▶️ <b>ХОД {r['world']['turn']}</b>\n\nЖивых организмов: {r['world']['living']}\nПоколение: {r['world']['generations']}"
    persist(user_id, session)
    await query.edit_message_text(text, reply_markup=keyboard(), parse_mode="HTML")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token: raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start)); app.add_handler(CallbackQueryHandler(buttons)); app.run_polling()

if __name__ == "__main__": main()

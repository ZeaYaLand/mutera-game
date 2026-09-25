"""Minimal Telegram interface for Mutera."""

import os

from src.genome import Genome

try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
except ImportError:  # pragma: no cover
    InlineKeyboardButton = InlineKeyboardMarkup = Update = Application = CallbackQueryHandler = CommandHandler = ContextTypes = None


def menu() -> "InlineKeyboardMarkup":
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧬 Мой организм", callback_data="organism")],
        [InlineKeyboardButton("🧪 Мутация", callback_data="mutation")],
        [InlineKeyboardButton("📊 Эволюция", callback_data="evolution")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🧬 MUTERA // SYSTEM ONLINE\n\n"
        "Твой первый организм готов к появлению.\n"
        "Выбери действие:",
        reply_markup=menu(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "organism":
        genome = Genome.random(12)
        await query.edit_message_text(
            f"🧬 Твой организм\n\nГеном: `{genome.sequence}`\nПоколение: {genome.generation}",
            parse_mode="Markdown",
            reply_markup=menu(),
        )
    elif query.data == "mutation":
        genome = Genome.random(12)
        mutated = genome.mutate(0.2)
        await query.edit_message_text(
            f"🧪 Мутация\n\nДо: `{genome.sequence}`\nПосле: `{mutated.sequence}`\n"
            f"Изменено генов: {len(mutated.mutations)}",
            parse_mode="Markdown",
            reply_markup=menu(),
        )
    else:
        await query.edit_message_text(
            "📊 Эволюция\n\nСистема эволюции готовится к Stage 1.",
            reply_markup=menu(),
        )


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()


if __name__ == "__main__":
    main()

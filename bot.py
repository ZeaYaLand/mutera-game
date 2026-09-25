"""Telegram interface for the Mutera evolution simulation."""

from __future__ import annotations

import os
import random

from src.genome import Genome
from mutera.stage1 import Stage1Config, Stage1Simulation
from mutera.stage2 import Stage2Config, Stage2Simulation
from mutera.stage3 import Stage3Config, Stage3Simulation

try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
except ImportError:  # pragma: no cover
    InlineKeyboardButton = InlineKeyboardMarkup = Update = Application = CallbackQueryHandler = CommandHandler = ContextTypes = None


user_simulations: dict[int, Stage3Simulation] = {}


def menu() -> "InlineKeyboardMarkup":
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧬 Мой организм", callback_data="organism")],
        [InlineKeyboardButton("🧪 Мутация", callback_data="mutation")],
        [InlineKeyboardButton("📈 Эволюция", callback_data="evolution")],
        [InlineKeyboardButton("🌍 Экосистема", callback_data="ecosystem")],
        [InlineKeyboardButton("🔄 Новый организм", callback_data="reset")],
    ])


def get_simulation(user_id: int) -> Stage3Simulation:
    if user_id not in user_simulations:
        config = Stage3Config(
            population_size=12,
            genome_length=12,
            mutation_rate=0.05,
            reproduction_energy=65.0,
            species_count=3,
        )
        simulation = Stage3Simulation(config=config, rng=random.Random(user_id))
        simulation.seed()
        user_simulations[user_id] = simulation
    return user_simulations[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    get_simulation(update.effective_user.id)
    await update.message.reply_text(
        "🧬 MUTERA // SYSTEM ONLINE\n\n"
        "Твоя эволюционная система активна.\n"
        "Выбери действие:",
        reply_markup=menu(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "reset":
        user_simulations.pop(user_id, None)
        get_simulation(user_id)
        await query.edit_message_text("🔄 Новый организм и новая популяция созданы.", reply_markup=menu())
        return

    simulation = get_simulation(user_id)

    if query.data == "organism":
        organism = next((o for o in simulation.organisms if o.alive), simulation.organisms[0])
        traits = simulation.trait_values(organism)
        await query.edit_message_text(
            "🧬 Твой организм\n\n"
            f"ID: `{organism.id}`\n"
            f"Геном: `{organism.genome.sequence}`\n"
            f"Поколение: {organism.genome.generation}\n"
            f"Возраст: {organism.age}\n"
            f"Энергия: {organism.energy:.1f}\n"
            f"Здоровье: {organism.health:.1f}\n\n"
            f"🌱 Поиск пищи: {traits['foraging']:.2f}\n"
            f"🛡 Устойчивость: {traits['resilience']:.2f}\n"
            f"🧬 Размножение: {traits['reproduction']:.2f}",
            parse_mode="Markdown",
            reply_markup=menu(),
        )
    elif query.data == "mutation":
        organism = next((o for o in simulation.organisms if o.alive), simulation.organisms[0])
        old = organism.genome
        organism.genome = old.mutate(0.2)
        await query.edit_message_text(
            "🧪 Мутация выполнена\n\n"
            f"До: `{old.sequence}`\n"
            f"После: `{organism.genome.sequence}`\n"
            f"Изменений: {len(organism.genome.mutations)}",
            parse_mode="Markdown",
            reply_markup=menu(),
        )
    elif query.data == "evolution":
        stats = simulation.run_generations(1)[0]
        await query.edit_message_text(
            "📈 Эволюция\n\n"
            f"Ход: {stats.turn}\n"
            f"Популяция: {stats.population}\n"
            f"Рождений: {stats.births}\n"
            f"Смертей: {stats.deaths}\n"
            f"Средний fitness: {stats.mean_fitness:.3f}\n"
            f"Разнообразие: {stats.diversity:.2f}\n"
            f"Порог отбора: {stats.selection_cutoff:.3f}",
            reply_markup=menu(),
        )
    elif query.data == "ecosystem":
        stats = simulation.ecosystem_history[-1] if simulation.ecosystem_history else simulation.step()
        await query.edit_message_text(
            "🌍 Экосистема\n\n"
            f"Популяция: {stats.population}\n"
            f"Видов: {stats.species}\n"
            f"Случаев болезни: {stats.disease_cases}\n"
            f"Климатическое событие: {'да' if stats.climate_event else 'нет'}\n"
            f"Разнообразие: {stats.diversity:.2f}",
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

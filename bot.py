"""
Telegram bot para Flyer GEN — Negro Padel
Comandos:
    /hoy     — genera flyer con turnos de HOY
    /manana  — genera flyer con turnos de MAÑANA
    /start   — mensaje de bienvenida
"""

import os
import sys
import logging
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _run_flyer(target: date) -> Path:
    from scraper   import get_available_slots
    from generator import generate_flyer
    slots = get_available_slots(target_date=target)
    if not slots:
        return None
    return generate_flyer(slots, target_date=target)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Negro Padel Flyer GEN\n\n"
        "/hoy    — flyer turnos de hoy\n"
        "/manana — flyer turnos de mañana"
    )


async def cmd_hoy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Scrapeando turnos de hoy...")
    target = date.today()
    try:
        path = _run_flyer(target)
    except Exception as e:
        await msg.edit_text(f"Error: {e}")
        return

    if path is None:
        await msg.edit_text("No hay turnos disponibles hoy.")
        return

    await msg.edit_text(f"Flyer {target.strftime('%d/%m/%Y')} listo, enviando...")
    with open(path, "rb") as f:
        await update.message.reply_photo(photo=f, caption=f"Turnos {target.strftime('%d/%m/%Y')}")
    await msg.delete()


async def cmd_manana(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Scrapeando turnos de mañana...")
    target = date.today() + timedelta(days=1)
    try:
        path = _run_flyer(target)
    except Exception as e:
        await msg.edit_text(f"Error: {e}")
        return

    if path is None:
        await msg.edit_text("No hay turnos disponibles mañana.")
        return

    await msg.edit_text(f"Flyer {target.strftime('%d/%m/%Y')} listo, enviando...")
    with open(path, "rb") as f:
        await update.message.reply_photo(photo=f, caption=f"Turnos {target.strftime('%d/%m/%Y')}")
    await msg.delete()


def main():
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN no encontrado en .env")
        sys.exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("hoy",    cmd_hoy))
    app.add_handler(CommandHandler("manana", cmd_manana))

    print("Bot corriendo... (Ctrl+C para detener)")
    app.run_polling()


if __name__ == "__main__":
    main()

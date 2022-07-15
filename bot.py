#!/usr/bin/env python3

import logging
import argparse
from telegram import Update  # pip install python-telegram-bot -U --pre
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
)

import sys 
import os
sys.path.append(os.path.abspath("plugin/carwashforecast/"))
from whenshouldiwashthecar import check_weather

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

print(os.environ.get('TOKEN'))
print(os.environ.get('BROWSER'))
print(os.getenv('type',100))
print(os.environ)

parser = argparse.ArgumentParser("bot.py")
parser.add_argument("TOKEN", 
        default=os.getenv('type',100),
        help="Telegram Token")

args = parser.parse_args()
TOKEN = args.TOKEN


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def echo(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text
    )


async def caps(update: Update, context: CallbackContext):
    text_caps = " ".join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)

    application.run_polling()

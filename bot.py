#!/usr/bin/env python3

import logging
import argparse
from pickle import NONE
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
import re

from plugin.carwashforecast.whenshouldiwashthecar import (check_weather, wash_or_not_to_wash, prettify_wash)
from plugin.u2ber.u2ber_downloader import (u2ber_download)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

async def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    sys.stderr.write("ERROR: '%s' caused by '%s'" % context.error, update)
    pass


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
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text_caps
    )


async def carwash(update: Update, context: CallbackContext.DEFAULT_TYPE):
    logging.info('Carwash command started')
    #TODO: 
    # move key to parameter
    # move percentage and days to chat settings with default settings
    
    #TODO: change key to variable
    #TODO: language from the message
    #TODO: get and pass the address... not address is "/wash"
    
    # error in the line
    ##weather_pops = await check_weather(update.message.text, "12c4f93fc60a4161b0685bad13519735", update.from.language_code) 
    wash = await wash_or_not_to_wash(weather_pops, 50, 3)
    pretty = await prettify_wash(wash)
    
    logging.info('Carwash command sending output')
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=pretty
    )

async def ytmp3(update: Update, context: CallbackContext.DEFAULT_TYPE):
    #TODO: download yt video from link, get audio only and send file back
    logging.info('yt command started')
    ytfile, ytsize = u2ber_download(re.sub('^/yt ', '', update.message.text), "downloads/"+str(update.message.chat.id))

    logging.info('yt message sending')
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="File %s has been downloaded. Total size is %s Mb" % (ytfile,ytsize)
    )

    logging.info('yt audio sending')
    await context.bot.send_audio(
        chat_id=update.effective_chat.id, 
        audio=open(ytfile, 'rb')
    )


if __name__ == "__main__":

    logging.info('Main starting')
    ENV_TOKEN = os.environ.get('TOKEN') if os.environ.get('TOKEN') is not NONE else "need a token"

    parser = argparse.ArgumentParser("bot.py")
    parser.add_argument("-t", "--token",
            dest='token',
            default=ENV_TOKEN,
            help="Telegram Bot Token (can be used from environment by 'source .env')")

    args = parser.parse_args()
    TOKEN = args.token if args.token != "need a token" else ""

    if TOKEN == "":
        parser.print_help(sys.stderr)
        sys.exit(0)

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    
    #wash message:
    # 2022-08-21 21:26:04,894 - telegram.ext._application - DEBUG - Processing update {'update_id': 354593385, 'message': {'chat': {'id': 568454692, 'type': <ChatType.PRIVATE>, 'last_name': 'Zavyalov', 'first_name': 'Artem', 'username': 'artem_zavyalov'}, 'group_chat_created': False, 'entities': [], 'new_chat_members': [], 'location': {'longitude': -122.654552, 'latitude': 49.222349}, 'new_chat_photo': [], 'message_id': 147, 'delete_chat_photo': False, 'caption_entities': [], 'date': 1661142365, 'supergroup_chat_created': False, 'photo': [], 'channel_chat_created': False, 'from': {'is_bot': False, 'username': 'artem_zavyalov', 'first_name': 'Artem', 'last_name': 'Zavyalov', 'id': 568454692, 'language_code': 'en'}}}
    # 2022-10-01 20:59:18,110 - telegram.ext._application - DEBUG - Processing update {'update_id': 354593389, 'message': {'chat': {'id': 568454692, 'type': <ChatType.PRIVATE>, 'last_name': 'Zavyalov', 'first_name': 'Artem', 'username': 'artem_zavyalov'}, 'text': '/wash', 'group_chat_created': False, 'entities': [{'length': 5, 'type': <MessageEntityType.BOT_COMMAND>, 'offset': 0}], 'new_chat_members': [], 'new_chat_photo': [], 'message_id': 153, 'delete_chat_photo': False, 'caption_entities': [], 'date': 1664683156, 'supergroup_chat_created': False, 'photo': [], 'channel_chat_created': False, 'from': {'is_bot': False, 'username': 'artem_zavyalov', 'first_name': 'Artem', 'last_name': 'Zavyalov', 'id': 568454692, 'language_code': 'en'}}}
    carwash_handler = CommandHandler("wash", carwash)

    #Location message:
    # 2022-08-21 21:26:04,894 - telegram.ext._application - DEBUG - Processing update {'update_id': 354593385, 'message': {'chat': {'id': 568454692, 'type': <ChatType.PRIVATE>, 'last_name': 'Zavyalov', 'first_name': 'Artem', 'username': 'artem_zavyalov'}, 'group_chat_created': False, 'entities': [], 'new_chat_members': [], 'location': {'longitude': -122.654552, 'latitude': 49.222349}, 'new_chat_photo': [], 'message_id': 147, 'delete_chat_photo': False, 'caption_entities': [], 'date': 1661142365, 'supergroup_chat_created': False, 'photo': [], 'channel_chat_created': False, 'from': {'is_bot': False, 'username': 'artem_zavyalov', 'first_name': 'Artem', 'last_name': 'Zavyalov', 'id': 568454692, 'language_code': 'en'}}}
    # TODO

    yt_handler = CommandHandler("yt", ytmp3)
    yt_handler_link = MessageHandler(filters.Regex(r"^https\:\/\/www\.youtube\.com\/"), ytmp3)
    yt_handler_link2= MessageHandler(filters.Regex(r"^https\:\/\/youtu.be\/"), ytmp3)

    application.add_handler(start_handler)
    application.add_handler(carwash_handler)
    application.add_handler(yt_handler)
    application.add_handler(yt_handler_link)
    application.add_handler(yt_handler_link2)

    application.add_error_handler(error)

    logging.info('main polling starting')
    application.run_polling()

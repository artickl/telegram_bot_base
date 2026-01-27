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
from dotenv import load_dotenv

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
    from plugin.carwashforecast.whenshouldiwashthecar import (check_weather, wash_or_not_to_wash, prettify_wash)

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
    from plugin.u2ber.u2ber_downloader import (u2ber_download)

    logging.info('yt message acknowledgement')
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Downloading audio from YouTube, please wait..."
    )

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


async def tts(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """Text to speech command handler."""
    logging.info('TTS command started')
    logging.info('TTS message acknowledgement')
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Preparing the recording..."
    )
    #!pip install torchaudio chatterbox-tts torch ffmpeg ffmpeg-python peft
    import torchaudio as ta
    import torch
    import time
    from chatterbox.tts import ChatterboxTTS

    # Automatically detect the best available device
    
    ttsfile= f"downloads/{str(update.message.chat.id)}/tts-{time.time()}.wav"
    device = "cuda" if torch.cuda.is_available() else "cpu"    
    model = ChatterboxTTS.from_pretrained(device=device)
    text = re.sub('^/tts ', '', update.message.text)
    wav = model.generate(text)
    ta.save(ttsfile, wav, model.sr)

    logging.info('TTS audio sending')
    await context.bot.send_audio(
        chat_id=update.effective_chat.id, 
        audio=open(ttsfile, 'rb')
    )

async def ttsaz(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """Text to speech command handler."""
    logging.info('TTS command started')
    logging.info('TTS message acknowledgement')
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Preparing the recording..."
    )
    #!pip install torchaudio chatterbox-tts torch ffmpeg ffmpeg-python peft
    import torchaudio as ta
    import torch
    import time
    from chatterbox.tts import ChatterboxTTS
    from pydub import AudioSegment

    # Automatically detect the best available device
    
    ttsfile= f"downloads/{str(update.message.chat.id)}/ttsaz-{time.time()}.wav"
    ttsmp3=f"{ttsfile[:-4]}.mp3"
    device = "cuda" if torch.cuda.is_available() else "cpu"    
    model = ChatterboxTTS.from_pretrained(device=device)
    text = re.sub('^/aztts ', '', update.message.text)
    AUDIO_PROMPT_PATH = "plugin/ChatterboxTTS/AZ-Voice Message.wav"
    wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
    ta.save(ttsfile, wav, model.sr)

    #converting wav to mp3
    wav_audio = AudioSegment.from_file(ttsfile, format="wav")
    wav_audio.export(ttsmp3, format="mp3")

    logging.info('TTS audio sending')
    await context.bot.send_audio(
        chat_id=update.effective_chat.id, 
        audio=open(ttsmp3, 'rb')
    )


if __name__ == "__main__":

    logging.info('Main starting')
    load_dotenv()

    ENV_TOKEN = os.environ.get('TOKEN')
    ENV_F_TOKEN = os.getenv('TOKEN')

    parser = argparse.ArgumentParser("bot.py")
    parser.add_argument("-t", "--token",
            dest='token',
            default=None,
            help="Telegram Bot Token (can be used from environment by 'source .env')")

    args = parser.parse_args()

    print(f"{ENV_TOKEN=}, {ENV_F_TOKEN=}, {args.token=}")
    
    if args.token is not None:
        TOKEN = args.token
    elif ENV_TOKEN is not None:
        TOKEN = ENV_TOKEN
    elif ENV_F_TOKEN is not None:
        TOKEN = ENV_F_TOKEN
    else:
        parser.print_help(sys.stderr)
        sys.exit(0)

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    
    #wash message:
    # 2022-08-21 21:26:04,894 - telegram.ext._application - DEBUG - Processing update {'update_id': 354593385, 'message': {'chat': {'id': 568454692, 'type': <ChatType.PRIVATE>, 'last_name': 'Zavyalov', 'first_name': 'Artem', 'username': 'artem_zavyalov'}, 'group_chat_created': False, 'entities': [], 'new_chat_members': [], 'location': {'longitude': -122.654552, 'latitude': 49.222349}, 'new_chat_photo': [], 'message_id': 147, 'delete_chat_photo': False, 'caption_entities': [], 'date': 1661142365, 'supergroup_chat_created': False, 'photo': [], 'channel_chat_created': False, 'from': {'is_bot': False, 'username': 'artem_zavyalov', 'first_name': 'Artem', 'last_name': 'Zavyalov', 'id': 568454692, 'language_code': 'en'}}}
    # 2022-10-01 20:59:18,110 - telegram.ext._application - DEBUG - Processing update {'update_id': 354593389, 'message': {'chat': {'id': 568454692, 'type': <ChatType.PRIVATE>, 'last_name': 'Zavyalov', 'first_name': 'Artem', 'username': 'artem_zavyalov'}, 'text': '/wash', 'group_chat_created': False, 'entities': [{'length': 5, 'type': <MessageEntityType.BOT_COMMAND>, 'offset': 0}], 'new_chat_members': [], 'new_chat_photo': [], 'message_id': 153, 'delete_chat_photo': False, 'caption_entities': [], 'date': 1664683156, 'supergroup_chat_created': False, 'photo': [], 'channel_chat_created': False, 'from': {'is_bot': False, 'username': 'artem_zavyalov', 'first_name': 'Artem', 'last_name': 'Zavyalov', 'id': 568454692, 'language_code': 'en'}}}
    carwash_handler = CommandHandler("wash", carwash)
    application.add_handler(carwash_handler)

    #Location message:
    # 2022-08-21 21:26:04,894 - telegram.ext._application - DEBUG - Processing update {'update_id': 354593385, 'message': {'chat': {'id': 568454692, 'type': <ChatType.PRIVATE>, 'last_name': 'Zavyalov', 'first_name': 'Artem', 'username': 'artem_zavyalov'}, 'group_chat_created': False, 'entities': [], 'new_chat_members': [], 'location': {'longitude': -122.654552, 'latitude': 49.222349}, 'new_chat_photo': [], 'message_id': 147, 'delete_chat_photo': False, 'caption_entities': [], 'date': 1661142365, 'supergroup_chat_created': False, 'photo': [], 'channel_chat_created': False, 'from': {'is_bot': False, 'username': 'artem_zavyalov', 'first_name': 'Artem', 'last_name': 'Zavyalov', 'id': 568454692, 'language_code': 'en'}}}
    # TODO

    yt_handler = CommandHandler("yt", ytmp3)
    yt_handler_link = MessageHandler(filters.Regex(r"^https\:\/\/www\.youtube\.com\/"), ytmp3)
    yt_handler_link2= MessageHandler(filters.Regex(r"^https\:\/\/youtu.be\/"), ytmp3)
    application.add_handler(yt_handler)
    application.add_handler(yt_handler_link)
    application.add_handler(yt_handler_link2)

    tts_handler = CommandHandler("tts", tts)
    application.add_handler(tts_handler)

    ttsaz_handler = CommandHandler("aztts", ttsaz)
    application.add_handler(ttsaz_handler)

    application.add_error_handler(error)
    logging.info('main polling starting')
    application.run_polling()

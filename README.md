# telegram_bot_base
base for telegram bot, will try to make all extensions as a separate instances

https://github.com/python-telegram-bot/python-telegram-bot
pip install python-telegram-bot

# testing first bot

https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot

# heroku
UPD: unfortunately Heroku removing free dyno as of November 28, 2022
https://devcenter.heroku.com/articles/free-dyno-hours

curl https://cli-assets.heroku.com/install-ubuntu.sh | sudo sh
heroky create
heroku config:set TOKEN=#############:###########################
heroku config:get TOKEN -s > .env

Local run:
heroku local

Remote deploy:
git push heroku main

# checking REPL
URL: https://replit.com

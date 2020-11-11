# Fichero usado en heroku
import logging
import os
from telegram.ext import Updater
from melibbot import melibbot


if __name__ == "__main__":
    WEBHOOK_TOKEN = os.environ.get('WEBHOOK_TOKEN')
    HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME')
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    if melibbot.bot is None:
        melibbot.bot_setup()
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(bot=melibbot.bot, dispatcher=melibbot.dispatcher)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=WEBHOOK_TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, WEBHOOK_TOKEN))
    updater.idle()

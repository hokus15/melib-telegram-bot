import os
import telegram
from flask import Flask, request
from melibbot import telebot
from melibbot.version import __version__

app = Flask(__name__)

WEBHOOK_TOKEN = os.environ['WEBHOOK_TOKEN']
print(WEBHOOK_TOKEN)

bot = None
dispatcher = None
valid_users = []


@app.route('/{}'.format(WEBHOOK_TOKEN), methods=['POST'])
def respond():
    print(request.get_json(force=True))
    if bot is None:
        telebot.bot_setup()
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return __version__


@app.route('/', methods=['GET'])
def version():
    return __version__


if __name__ == '__main__':
    app.run(threaded=True)

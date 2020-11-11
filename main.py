# main.py
# To deploy use: gcloud functions deploy webhook

# Fichero usado en Google Cloud Functions
import os
import telegram
from telegram.ext import Dispatcher
from flask import abort
from melibbot import melibbot

bot = None
dispatcher = None


def _autheticate(request):
    '''
    Comprueba si el token proporcionado es válido.
    '''
    webhook_token = os.environ['WEBHOOK_TOKEN']
    request_token = request.args.get('token')
    if request_token and request_token == webhook_token:
        return True
    else:
        return False


def webhook(request):
    # print(request.get_json(force=True))
    global bot
    global dispatcher
    if _autheticate(request):
        if request.method == "POST":
            if bot is None:
                bot = telegram.Bot(token=os.environ.get('TELEGRAM_TOKEN'))
                dispatcher = Dispatcher(bot=bot,
                                        update_queue=None,
                                        workers=0,
                                        use_context=True)
                dispatcher.add_error_handler(melibbot.error_callback)
                dispatcher.add_handler(melibbot.get_handler())

            update = telegram.Update.de_json(request.get_json(force=True), bot)
            dispatcher.process_update(update)
        return "ok"
    else:
        # Si no se ha podido verificar el token
        abort(403)

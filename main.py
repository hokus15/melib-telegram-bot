# main.py
# To deploy use: gcloud functions deploy webhook

# Fichero usado en Google Cloud Functions
import os
import telegram
from flask import abort
from melibbot import melibbot


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
    if melibbot.bot is None:
        melibbot.bot_setup()
    if _autheticate(request):
        if request.method == "POST":
            update = telegram.Update.de_json(request.get_json(force=True), melibbot.bot)
            melibbot.dispatcher.process_update(update)
        return "ok"
    else:
        # Si no se ha podido verificar el token
        abort(403)

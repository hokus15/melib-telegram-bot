# main.py
# To deploy use: gcloud functions deploy webhook

import os
import telegram
import requests
import json
import html
import traceback
from flask import abort
from geopy import distance
from functools import wraps
from telegram.ext import MessageHandler, CallbackQueryHandler, Dispatcher, Filters
# from telegram.error import TelegramError, BadRequest

# Rádio por defecto en metros.
DEFAULT_RADIUS = 500

STATION_BASE_URL = 'https://ws.consorcidetransports.com/produccio/ximelib-mobile/rest/devicegroups'

HEADERS = {
    'content-type': "application/json",
    'accept-encoding': "gzip",
    'cache-control': "no-cache",
}

PLACE_TYPE = {
    'CAR': 'coche',
    'MOTORCYCLE': 'moto'
}

STATUS = {
    'AVAILABLE': 'libre',
    'OCCUPIED_PARTIAL': 'parcialmente ocupado'
}


SEND_LOCATION_INSTRUCTIONS = 'ℹ *Para enviar una ubicación* ℹ \n' \
                             '1\\. Pulsa sobre el clip \\(📎\\) que encontrarás en la ventana de mensaje\\.\n' \
                             '2\\. Elige la opción de `Ubicación`\\.\n' \
                             '3\\. Desplázate por el mapa hasta la ubicación que quieras\\.\n' \
                             '4\\. Elije `Enviar la ubicación seleccionada`\\.'

# Si no encuentra la variable de entorno usa 1234567890 para los tests
VALID_USERS = os.environ.get('VALID_USERS', '1234567890').split(';')


def restricted(func):
    """Decorator: Comprueba si el usuario puede ejecutar el comando `func`."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id not in VALID_USERS:
            update.message.reply_text(
                text=f'Hola {update.effective_user.first_name}, por '
                'ahora, no puedes usar el bot, por favor proporciona '
                f'el siguiente número: {user_id} al administrador\\.\n'
                'Una vez dado de alta prueba a enviarme una ubicación:\n'
                f'{SEND_LOCATION_INSTRUCTIONS}',
                parse_mode=telegram.ParseMode.MARKDOWN_V2)
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def send_action(action):
    """Decorator: Envia un `action` mientras procesa el comando `func`."""
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    return decorator


def error_callback(update, context):
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb = ''.join(tb_list)
    message = (
        'Excepción lanzada cuando se procesaba una actualización:\n'
        '<pre>update = {}</pre>\n\n'
        '<pre>context.chat_data = {}</pre>\n\n'
        '<pre>context.user_data = {}</pre>\n\n'
        '<pre>{}</pre>'
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(str(context.chat_data)),
        html.escape(str(context.user_data)),
        html.escape(tb),
    )
    # Envía el mensaje de error al administrador (ha de ser el primero de la lista de usuarios)
    context.bot.send_message(chat_id=VALID_USERS[0], text=message, parse_mode=telegram.ParseMode.HTML)
    update.message.reply_text(text='Ups! Parece que algo no ha salido bien.\n '
                                   'He enviado un mensaje al administrador con '
                                   'detalles del error para que lo revise.')


@restricted
@send_action(telegram.ChatAction.TYPING)
def help(update, context):
    # print('context.chat_data = {}'.format(context.chat_data))
    location_keyboard = telegram.KeyboardButton(text="Enviar mi ubicación actual", request_location=True)
    reply_markup = telegram.ReplyKeyboardMarkup([[location_keyboard]])
    update.message.reply_text(
        text=f'⚠ Hola {update.message.from_user.first_name}, para poder darte '
             'información de los cargadores que hay libres cerca de tu '
             'posición, por favor, *envíame tu ubicación* usando el botón de abajo\\.\n\n'
             'ℹ *CONSEJO* ℹ\n'
             'A parte de enviar tu ubicación actual, puedes enviar la ubicación '
             'de tu destino para saber los cargadores que hay libres cerca\\.\n\n'
             f'{SEND_LOCATION_INSTRUCTIONS}\n\n'
             '‼ *ATENCIÓN* ‼\n'
             'La distancia la mido en *linea recta* entre la ubicación enviada '
             'y la ubicación del cargador\\. No tengo en cuenta la ruta '
             'ni la altura de ninguno de los dos puntos\\. Por lo que la '
             'distancia para llegar al cargador puede variar dependiendo '
             'del camino que sigas hasta él\\.',
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup)


@restricted
@send_action(telegram.ChatAction.TYPING)
def location(update, context):
    free_stations = _free_stations_in_range(update.message.location, DEFAULT_RADIUS)
    context.chat_data['location'] = json.dumps({
        'latitude': str(update.message.location.latitude),
        'longitude': str(update.message.location.longitude)
    })
    # Si hay estaciones de carga dentro del rádio
    if len(free_stations) > 0:
        message = _free_stations_response(free_stations, DEFAULT_RADIUS)
        update.message.reply_text(
            parse_mode=telegram.ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True,
            text=message)
    # Si no se han encontrado estaciones de carga libres dentro del rádio
    else:
        # Prepara la respuesta con las opciones
        message = f'💩 No he encontrado cargadores libres en {DEFAULT_RADIUS} metros'
        update.message.reply_text(message)
        message = 'Podemos volver a probar ampliando el rádio de búsqueda a:'
        keyboard = [
            [
                telegram.InlineKeyboardButton('1 Km', callback_data='1000'),
                telegram.InlineKeyboardButton('1,5 Km', callback_data='1500'),
                telegram.InlineKeyboardButton('2 Km', callback_data='2000')
            ],
            [telegram.InlineKeyboardButton("No amplies el rádio de búsqueda", callback_data='0')]
        ]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)


@restricted
@send_action(telegram.ChatAction.TYPING)
def callback(update, context):
    # print('callback - context.chat_data = {}'.format(context.chat_data))
    radius = int(update.callback_query.data)
    if radius > 0:
        message = ''
        try:
            chat_location = json.loads(context.chat_data['location'])
            location = telegram.Location(float(chat_location['longitude']), float(chat_location['latitude']))
            free_stations = _free_stations_in_range(location, radius)
            # Si hay estaciones de carga dentro del rádio
            if len(free_stations) > 0:
                message = _free_stations_response(free_stations, radius)
            # Si no se han encontrado estaciones de carga libres dentro del rádio
            else:
                message = f'💩 ¡Vaya\\! Pues ni ampliando el rádio de búsqueda a {radius} metros ' \
                    'he encontrado cargadores libres, comparte otra ubicación y vuelve a probar\\.'
                update.callback_query.answer()
                update.callback_query.edit_message_text(parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                                        disable_web_page_preview=True,
                                                        text=message)
        except KeyError:
            update.callback_query.answer()
            update.callback_query.edit_message_text(text='Ups! No he podido ampliar el rádio de búsqueda, '
                                                    'comparte otra ubicación y vuelve a probar.')
    # Si no quiere ampliar el rádio
    else:
        update.callback_query.answer()
        update.callback_query.edit_message_text(f'Vale {update.callback_query.from_user.first_name}, '
                                                'tú mandas, no amplio el rádio de búsqueda.')


bot = telegram.Bot(token=os.environ.get('TELEGRAM_TOKEN', '0000:yyyy'))
dispatcher = Dispatcher(bot=bot,
                        update_queue=None,
                        workers=0,
                        use_context=True)
dispatcher.add_error_handler(error_callback)
# Para procesar cualquier texto
dispatcher.add_handler(MessageHandler(Filters.text, help))
dispatcher.add_handler(MessageHandler(Filters.location, location))
dispatcher.add_handler(CallbackQueryHandler(callback))


def webhook(request):
    # print(request.get_json(force=True))
    if _autheticate(request):
        if request.method == "POST":
            update = telegram.Update.de_json(request.get_json(force=True), bot)
            dispatcher.process_update(update)
        return "ok"
    else:
        # Si no se ha podido verificar el token
        abort(403)


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


def _free_stations_in_range(location, radius):
    '''
    Devuelve una lista de las estaciones libres o parcialmente ocupadas dentro
    del rádio de la ubicación.
    '''

    # Se puede filtrar por los siguentes conceptos:
    # placeType: Tipo de plaza.
    # Posibles valores:
    #   CAR: Coche
    #   MOTORCYCLE: Moto

    # idComponentType: Tipo Conector
    # Se puede obtener una lista de cargadores válidos usando la siguiente
    # petición GET : https://ws.consorcidetransports.com/produccio/ximelib-mobile/rest/devicecomponenttypes
    # Posibles valores:
    #   1: Mennekes
    #   2: Shuko
    #   3: CSSCombo
    #   4: CHAdeMo

    # chargeType: Tipo carga Posibles valores:
    #   CHARGE_MODE_2: Lenta
    #   CHARGE_MODE_3: Semi-rápida
    #   CHARGE_MODE_4: Rápida

    # onlyAvailable: Mostrar sólo disponibles. true/false

    # includeOffline:Mostrar no gestionados. true/false

    # bounds:No he podido averiguar para que sirve
    payload = {
        "bounds": None,
        "idComponentType": None,
        "onlyAvailable": True,
        "includeOffline": False,
        "chargeType": None,
        "placeType": None
    }
    # Envía la petición
    response = requests.request(
        "POST",
        STATION_BASE_URL,
        data=json.dumps(payload),
        headers=HEADERS)
    all_station_json_data = response.json()
    latlong = (location.latitude, location.longitude)
    stations = {}
    for value in all_station_json_data:
        station_id = value['id']
        station_location = (float(value['lat']), float(value['lng']))
        try:
            # Calcula la distancia en metros desde la estación de carga
            # a la ubicación pasada por el usuario
            dist = distance.distance(latlong, station_location).meters
            # print(f'Station id: {station_id}, distance: {dist:0.0f}m')
            if dist <= radius:
                stations[station_id] = dist
                # print(f'Added station id: {station_id}, distance: {dist:0.0f}m to list...')
        except ValueError:
            print(f'Bad location {station_location} for station {station_id}')
    return stations


def _free_stations_response(stations, radius):
    '''
    Prepara el texto de respuesta con las estaciones de carga libres.
    '''
    message = ''
    # Ordena las estaciones de carga por distancia
    sorted_stations = sorted(stations.items(), key=lambda x: x[1])
    message += f'🎉🎊 He encontrado los siguientes cargadores disponibles en {radius} metros:\n\n'
    for station in sorted_stations:
        station_status_url = f'{STATION_BASE_URL}/{station[0]}'
        response = requests.request("GET", station_status_url, headers=HEADERS)
        station_status = response.json()
        message += f"🔌🆓 Cargador para *{PLACE_TYPE[station_status['devices'][0]['placeType']]} " \
                   f"{STATUS[station_status['status']]}* a " \
                   f"*{station[1]:0.0f}* metros en " \
                   f"[*{_escape_data(station_status['address'])}*]" \
                   f"(https://www.google.com/maps/place/{station_status['lat']},{station_status['lng']})\n"
    # print(message)
    return message


def _escape_data(s):
    '''
    Telegram tiene ciertos caracteres reservados que hay que "escapar".
    '''
    return s.replace('_', '\\_') \
            .replace('*', '\\*') \
            .replace('[', '\\[') \
            .replace(']', '\\]') \
            .replace('(', '\\(') \
            .replace(')', '\\)') \
            .replace('~', '\\~') \
            .replace('`', '\\`') \
            .replace('>', '\\>') \
            .replace('#', '\\#') \
            .replace('+', '\\+') \
            .replace('-', '\\-') \
            .replace('=', '\\=') \
            .replace('|', '\\|') \
            .replace('{', '\\{') \
            .replace('}', '\\}') \
            .replace('.', '\\.') \
            .replace('!', '\\!')

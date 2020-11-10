import os
import telegram
import json
import html
import traceback
from geopy import distance
from functools import wraps
from melibbot import melib
from melibbot.version import __version__
from telegram.ext import (MessageHandler, CallbackQueryHandler, ConversationHandler,
                          Dispatcher, Filters)
from telegram.utils.helpers import escape_markdown


bot = None
dispatcher = None
valid_users = []


MAX_CHARGERS = 9

PLACE_TYPE = {
    'CAR': 'coche',
    'MOTORCYCLE': 'moto'
}

STATUS = {
    'AVAILABLE': 'libre',
    'OCCUPIED_PARTIAL': 'parcialmente ocupado',
    'UNAVAILABLE': 'no dispobible',  # Necesario para los tests
    'OCCUPIED': 'ocupado'  # Necesario para los tests
}

SEND_LOCATION_INSTRUCTIONS = 'ℹ *Para enviar una ubicación* ℹ \n' \
                             '1\\. Pulsa sobre el clip \\(📎\\) que encontrarás en la ventana de mensaje\\.\n' \
                             '2\\. Elige la opción de `Ubicación`\\.\n' \
                             '3\\. Desplázate por el mapa hasta la ubicación que quieras\\.\n' \
                             '4\\. Elije `Enviar la ubicación seleccionada`\\.'


# Estados de conversación
RADIUS, UPDATE_RADIUS = range(2)


def restricted(func):
    """Decorator: Comprueba si el usuario puede ejecutar el comando `func`."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id not in valid_users:
            update.effective_message.reply_text(
                text=f'Hola {update.effective_user.first_name}, por '
                'ahora, no puedes usar el bot, por favor, proporciona '
                f'el siguiente número al administrador:\n\n*{user_id}*\n\n'
                'Una vez dado de alta prueba a escribirme algo o enviarme una ubicación:\n'
                f'{SEND_LOCATION_INSTRUCTIONS}',
                parse_mode=telegram.ParseMode.MARKDOWN_V2)
            message = f'Hola soy {update.effective_user.first_name} {update.effective_user.last_name} ' \
                f'y mi usuario de Telegram es:\n*{user_id}*\nPor favor dame de ' \
                'alta en el sistema para que pueda acceder al bot\\.'
            context.bot.send_message(chat_id=valid_users[0], text=message, parse_mode=telegram.ParseMode.MARKDOWN_V2)
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
    print('Excepción lanzada cuando se procesaba una actualización: {}'.format(context.error))
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb = ''.join(tb_list)
    message = (
        'Excepción: {}\n'
        'Mensaje: {}\n'
        '<pre>update = {}</pre>\n\n'
        '<pre>context.chat_data = {}</pre>\n\n'
        '<pre>context.user_data = {}</pre>\n\n'
        '<pre>{}</pre>'
    ).format(
        html.escape(str(type(context.error))),
        html.escape(str(context.error)),
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(str(context.chat_data)),
        html.escape(str(context.user_data)),
        html.escape(tb),
    )
    # Corta el mensaje si es más largo de lo permitido
    if len(message) > 4096:
        message = message[:4089] + '</pre>'
    # Envía el mensaje de error al administrador (ha de ser el primero de la lista de usuarios)
    context.bot.send_message(chat_id=valid_users[0], text=message, parse_mode=telegram.ParseMode.HTML)
    update.effective_message.reply_text(text='Ups\\! Parece que algo no ha salido bien\\.\n '
                                             'He enviado un mensaje al administrador con '
                                             'detalles del error para que lo revise\\.\n\n'
                                             '*Error*: {}'.format(escape_markdown(str(context.error))),
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2)
    return ConversationHandler.END


@ restricted
@ send_action(telegram.ChatAction.TYPING)
def help(update, context):
    location_keyboard = telegram.KeyboardButton(text="Enviar mi ubicación actual", request_location=True)
    reply_markup = telegram.ReplyKeyboardMarkup([[location_keyboard]], one_time_keyboard=True)
    update.effective_message.reply_text(
        text=f'⚠ Hola {update.effective_user.first_name}, para poder darte '
             'información de los cargadores que hay libres cerca de tu '
             'posición, por favor, *envíame tu ubicación* usando el botón de abajo\\.\n\n'
             'ℹ *CONSEJO* ℹ\n'
             'A parte de enviar tu ubicación actual, puedes enviar la ubicación '
             'de tu destino para saber los cargadores que hay libres cerca\\.\n\n'
             f'{SEND_LOCATION_INSTRUCTIONS}\n\n'
             '‼ *ATENCIÓN* ‼\n'
             f'Te voy a devolver como máximo {MAX_CHARGERS} cargadores\\.\n\n'
             'La distancia la mido en *linea recta* entre la ubicación enviada '
             'y la ubicación del cargador\\. No tengo en cuenta la ruta '
             'ni la altura de ninguno de los dos puntos\\. Por lo que la '
             'distancia para llegar al cargador puede variar dependiendo '
             'del camino que sigas hasta él\\.\n\n'
             f'`v{escape_markdown(__version__)}`',
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup)
    return RADIUS


@ restricted
@ send_action(telegram.ChatAction.TYPING)
def location(update, context):
    context.chat_data['location'] = json.dumps({
        'latitude': str(update.effective_message.location.latitude),
        'longitude': str(update.effective_message.location.longitude)
    })
    message = '¿Qué rádio de búsqueda quieres usar?'
    keyboard = [
        [
            telegram.InlineKeyboardButton('500 m', callback_data='500'),
            telegram.InlineKeyboardButton('1 Km', callback_data='1000'),
            telegram.InlineKeyboardButton('2 Km', callback_data='2000')
        ],
        [
            telegram.InlineKeyboardButton('3 Km', callback_data='3000'),
            telegram.InlineKeyboardButton('5 Km', callback_data='5000'),
            telegram.InlineKeyboardButton('7 Km', callback_data='7000'),
        ],
        # [telegram.InlineKeyboardButton("Cargador libre más cercano", callback_data='0')]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(message, reply_markup=reply_markup)
    return UPDATE_RADIUS


@ restricted
@ send_action(telegram.ChatAction.TYPING)
def callback(update, context):
    radius = int(update.callback_query.data)
    update.callback_query.answer()
    if radius > 0:
        message = ''
        try:
            chat_location = json.loads(context.chat_data['location'])
            location = telegram.Location(float(chat_location['longitude']), float(chat_location['latitude']))
            available_chargers = free_chargers(location)
            # Si hay estaciones de carga dentro del rádio
            if len(available_chargers) > 0:
                message = free_chargers_response(available_chargers, radius, location)
            # Si no se han encontrado estaciones de carga libres dentro del rádio
            else:
                message = f'💩 ¡Vaya\\! No he encontrado ningún cargador libre en {radius} metros, ' \
                    'comparte otra ubicación y vuelve a probar\\.'
#            update.callback_query.edit_message_text(parse_mode=telegram.ParseMode.MARKDOWN_V2,
#                                                    disable_web_page_preview=True,
#                                                    text=f'Vale, busco cargadores en {radius} metros')
            update.callback_query.edit_message_reply_markup(telegram.InlineKeyboardMarkup([[]]))
            context.bot.send_message(chat_id=update.effective_user.id,
                                     parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                     disable_web_page_preview=False,
                                     text=message)
        except KeyError:
            print('No he podido encontrar la ubicación en chat_data: {}'.format(context.chat_data))
            update.callback_query.edit_message_text(text='Ups! No he podido realizar la búsqueda, '
                                                    'comparte otra ubicación y vuelve a probar.')
    # Si quiere buscar la estación libre más cercana
    else:
        update.callback_query.edit_message_text(f'Vale {update.callback_query.from_user.first_name}, '
                                                'tú mandas, estación libre más cercana.')
    return ConversationHandler.END


def free_chargers(location):
    '''
    Devuelve un dict de los cargadores libres o parcialmente ocupados junto
    con la distancia en metros a la ubicación proporcionada.

    La clave del dict es el identificador del cargador y el valor es la distancia
    en metros desde la ubicación proporcionada.
    Ejemplo:
    {
        23: 400,
        523: 342,
        684: 1203,
        690: 500,
        691: 501
    }
    '''

    payload = {
        "bounds": None,
        "idComponentType": None,
        "onlyAvailable": True,
        "includeOffline": False,
        "chargeType": None,
        "placeType": None
    }

    all_chargers_json_data = melib.device_groups(payload)
    latlong = (location.latitude, location.longitude)
    chargers = {}
    for value in all_chargers_json_data:
        charger_id = value['id']
        charger_location = (float(value['lat']), float(value['lng']))
        try:
            # Calcula la distancia en metros desde la estación de carga
            # a la ubicación pasada por el usuario
            dist = distance.distance(latlong, charger_location).meters
            chargers[charger_id] = dist
        except ValueError:
            print(f'Bad location {charger_location} for charger {charger_id}')
    return chargers


def free_chargers_response(chargers, radius, location):
    '''
    Prepara el texto de respuesta con las estaciones de carga libres dentro del rango.
    '''
    message = ''
    message_charger = ''
    message_header = ''
    message_map_markers = ''
    if len(chargers) > 0:
        # Ordena las estaciones de carga por distancia
        sorted_chargers = sorted(chargers.items(), key=lambda x: x[1])
        # Siempre hay que retornar al menos el cargador más cercano
        closest_charger = sorted_chargers.pop(0)
        closest_charger_data = melib.device_groups_by_id(closest_charger[0])
        closest_charger_distance = closest_charger[1]
        message_charger += f'⚡ 1\\. {get_charger_text(closest_charger_data, closest_charger_distance)}'
        message_map_markers += f'~{closest_charger_data["lng"]},{closest_charger_data["lat"]},pm2bll1'
        # Si el cargador más cercano está fuera del radio
        if closest_charger_distance > radius:
            message_header = '🤬 No he encontrado cargadores disponibles en ' \
                             f'{radius} metros, pero el más cercano es:\n\n'
        else:
            message_header = '😁 He encontrado los siguientes cargadores ' \
                             f'disponibles en {radius} metros:\n\n'
            pos = 2
            for charger in sorted_chargers:
                if charger[1] <= radius and pos <= MAX_CHARGERS:
                    charger_data = melib.device_groups_by_id(charger[0])
                    message_map_markers += f'~{charger_data["lng"]},{charger_data["lat"]},pm2bll{pos}'
                    message_charger += f'⚡ {pos}\\. {get_charger_text(charger_data, charger[1])}'
                    pos += 1
                else:
                    break
        static_map = 'https://static-maps.yandex.ru/1.x/?lang=es_ES&l=map&ll=' \
                     f'{location.longitude},{location.latitude}' \
                     f'&size=300,300&pt={location.longitude},{location.latitude},' \
                     f'pm2rdl{message_map_markers}'
        message = f'[🧐]({static_map}){message_header}{message_charger}'
    else:
        message = 'Algo muy gordo ha ocurrido porque no hay ningún cargador libre en las Baleares'
    # print(message)
    return message


def get_charger_text(charger, distance):
    message = f"Cargador para *{PLACE_TYPE[charger['devices'][0]['placeType']]} " \
        f"{STATUS[charger['status']]}* a " \
        f"*{distance:0.0f}* metros en " \
        f"[*{escape_markdown(charger['address'], 2)}*]" \
        f"(https://www.google.com/maps/place/{charger['lat']},{charger['lng']})\n"
    return message


def bot_setup():
    global bot
    global dispatcher
    global valid_users
    valid_users = os.environ.get('VALID_USERS', '').split(';')
    bot = telegram.Bot(token=os.environ.get('TELEGRAM_TOKEN'))
    dispatcher = Dispatcher(bot=bot,
                            update_queue=None,
                            workers=0,
                            use_context=True)
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text, help), MessageHandler(Filters.location, location)],
        states={
            RADIUS: [MessageHandler(Filters.location, location)],
            UPDATE_RADIUS: [CallbackQueryHandler(callback)],
        },
        fallbacks=[MessageHandler(Filters.text, help), MessageHandler(Filters.location, location)]
    )
    dispatcher.add_error_handler(error_callback)
    dispatcher.add_handler(conv_handler)

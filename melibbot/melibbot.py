import os
import telegram
import json
import html
import traceback
import logging

from geopy import distance
from functools import wraps
from melibbot import melib
from melibbot.version import __version__
from telegram.ext import (MessageHandler, CallbackQueryHandler,
                          ConversationHandler, Filters, CommandHandler)

logger = logging.getLogger(__name__)

valid_users = os.environ.get('VALID_USERS', '').split(';')

admin_user = os.environ.get('ADMIN_USER', valid_users[0])

MAX_CHARGERS = 10

PLACE_TYPE = {
    'CAR': 'coche',
    'MOTORCYCLE': 'moto'
}

STATUS = {
    'AVAILABL': 'libre',
    'OCCUPIED_PARTIAL': 'parcialmente ocupado',
    'UNAVAILABLE': 'no disponible',
    'OCCUPIED': 'ocupado',
    'UNKNOWN': 'desconocido',
    'OFFLINE': 'no gestionado'
}

HELP_HEADER = 'Prueba a decirme algo, mandarme los comandos /lista, /libres o una ubicación.'

HELP_LOCATION_INSTRUCTIONS = 'ℹ <b>Para enviar una ubicación</b> ℹ \n' \
                             '1. Pulsa sobre el clip (📎) que encontrarás en la ventana de mensaje.\n' \
                             '2. Elige la opción de `Ubicación`.\n' \
                             '3. Desplázate por el mapa hasta la ubicación que quieras.\n' \
                             '4. Elije `Enviar la ubicación seleccionada`.'

HELP_HINT = 'ℹ <b>CONSEJO</b> ℹ\n' \
            'A parte de enviar tu ubicación actual, puedes enviar la ubicación ' \
            'de tu destino o cualquier otra para saber los cargadores que hay cerca.'

HELP_FOOTER = '‼ <b>ATENCIÓN</b> ‼\n' \
              f'Te voy a devolver como máximo {MAX_CHARGERS} cargadores.\n\n' \
              'La distancia la mido en <b>linea recta</b> entre la ubicación enviada ' \
              'y la ubicación del cargador. No tengo en cuenta la ruta ' \
              'ni la altura de ninguno de los dos puntos. Por lo que la ' \
              'distancia para llegar al cargador puede variar dependiendo ' \
              'del camino que sigas hasta él.\n\n' \
              f'<code>v{__version__}</code>'

# Estados de conversación
LOCATION, RADIUS = range(2)


def restricted(func):
    """Decorator: Comprueba si el usuario puede ejecutar el comando `func`."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id not in valid_users:
            logger.warning(f'Acceso restringido al usuario: {user_id} - '
                           f'{update.effective_user.first_name} {update.effective_user.last_name}')
            update.effective_message.reply_text(
                text=f'Hola {update.effective_user.first_name}, por '
                     'ahora, no puedes usar el bot, por favor, proporciona '
                     f'el siguiente número al administrador:\n\n<b>{user_id}</b>\n\n'
                     f'{HELP_HEADER}\n\n'
                     f'{HELP_LOCATION_INSTRUCTIONS}',
                parse_mode=telegram.ParseMode.HTML)
            message = f'Hola soy {update.effective_user.first_name} {update.effective_user.last_name} '
            f'y mi usuario de Telegram es:\n<b>{user_id}</b>\nPor favor dame de '
            'alta en el sistema para que pueda acceder al bot.'
            context.bot.send_message(chat_id=admin_user, text=message, parse_mode=telegram.ParseMode.HTML)
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
    logger.error('Excepción lanzada cuando se procesaba una actualización: {}\n{}'.format(context.error, tb))
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
    # Envía el mensaje de error al administrador
    context.bot.send_message(chat_id=admin_user, text=message, parse_mode=telegram.ParseMode.HTML)
    update.effective_message.reply_text(text=('Ups! Parece que algo no ha salido bien.\n '
                                              'He enviado un mensaje al administrador con '
                                              'detalles del error para que lo revise.\n\n'
                                              '<b>Error</b>: {}'.format(str(context.error))),
                                        parse_mode=telegram.ParseMode.HTML)
    return ConversationHandler.END


@ restricted
@ send_action(telegram.ChatAction.TYPING)
def free_chargers_help(update, context):
    context.chat_data['onlyAvailable'] = True
    return chargers_help(update, context)


@ restricted
@ send_action(telegram.ChatAction.TYPING)
def list_chargers_help(update, context):
    context.chat_data['onlyAvailable'] = False
    return chargers_help(update, context)


@ restricted
@ send_action(telegram.ChatAction.TYPING)
def chargers_help(update, context):
    location_button = telegram.KeyboardButton(text="Enviar mi ubicación actual", request_location=True)
    reply_markup = telegram.ReplyKeyboardMarkup([[location_button]],
                                                one_time_keyboard=True,
                                                resize_keyboard=True)
    update.effective_message.reply_text(
        text=f'⚠ Hola {update.effective_user.first_name}, para poder darte '
        'información de los cargadores que hay cerca de ti, por favor, '
        '<b>envíame tu ubicación</b> usando el botón de abajo.\n\n'
        f'{HELP_HINT}\n\n'
        f'{HELP_LOCATION_INSTRUCTIONS}\n\n'
        f'{HELP_FOOTER}',
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=reply_markup)
    return LOCATION


@ restricted
@ send_action(telegram.ChatAction.TYPING)
def request_radius(update, context):
    context.chat_data['location'] = json.dumps({
        'latitude': str(update.effective_message.location.latitude),
        'longitude': str(update.effective_message.location.longitude)
    })
    message = '¿Qué radio de búsqueda quieres usar?'
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
    return RADIUS


@ restricted
@ send_action(telegram.ChatAction.TYPING)
def search_chargers(update, context):
    radius = int(update.callback_query.data)
    logger.info('Solicitada búsqueda de cargadores en un radio de {} metros'.format(radius))
    update.callback_query.answer()
    if radius > 0:
        message = ''
        try:
            chat_location = json.loads(context.chat_data['location'])
            location = telegram.Location(float(chat_location['longitude']), float(chat_location['latitude']))
            available_chargers = chargers_list(location, context.chat_data.pop('onlyAvailable', True))
            # Si hay estaciones de carga dentro del radio
            if len(available_chargers) > 0:
                message = chargers_response(available_chargers, radius, location)
            # Si no se han encontrado estaciones de carga dentro del radio
            else:
                message = f'💩 ¡Vaya! No he encontrado ningún cargador en {radius} metros, '
                'comparte otra ubicación y vuelve a probar.'
            context.bot.send_message(chat_id=update.effective_user.id,
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=False,
                                     text=message,
                                     reply_markup=telegram.ReplyKeyboardRemove())
        except KeyError as err:
            logger.error('context.chat_data: {}.\n\nERROR: {}'.format(context.chat_data, err))
            raise err

    # Si quiere buscar la estación más cercana
    else:
        update.callback_query.edit_message_text(f'Vale {update.callback_query.from_user.first_name}, '
                                                'tú mandas, estación libre más cercana.')

    return ConversationHandler.END


def chargers_list(location, onlyAvailable=True):
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
        "onlyAvailable": onlyAvailable,
        "includeOffline": True,
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
            logger.error(f'Coordenadas {charger_location} incorrectas para el cargador {charger_id}')
    return chargers


def chargers_response(chargers, radius, location):
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
        message_charger += f'⚡ 1. {get_charger_text(closest_charger_data, closest_charger_distance)}'
        message_map_markers += f'~{closest_charger_data["lng"]},{closest_charger_data["lat"]},pm2bll1'
        # Si el cargador más cercano está fuera del radio
        if closest_charger_distance > radius:
            message_header = '🤬 No he encontrado cargadores en ' \
                f'{radius} metros, pero el más cercano es:\n\n'
        else:
            message_header = '😁 He encontrado los siguientes cargadores ' \
                f'en {radius} metros:\n\n'
            pos = 2
            for charger in sorted_chargers:
                if charger[1] <= radius and pos <= MAX_CHARGERS:
                    charger_data = melib.device_groups_by_id(charger[0])
                    message_map_markers += f'~{charger_data["lng"]},{charger_data["lat"]},pm2bll{pos}'
                    message_charger += f'⚡ {pos}. {get_charger_text(charger_data, charger[1])}'
                    pos += 1
                else:
                    break
        static_map = 'https://static-maps.yandex.ru/1.x/?lang=es_ES&l=map&ll=' \
            f'{location.longitude},{location.latitude}' \
            f'&size=300,300&pt={location.longitude},{location.latitude},' \
                     f'pm2rdl{message_map_markers}'
        message = f'<a href="{static_map}">🧐</a>{message_header}{message_charger}'
    else:
        logger.error('Parece que no hay ningún cargador disponible')
        message = 'Algo muy gordo ha ocurrido porque no hay ningún cargador disponible en las Baleares'
    return message


def get_charger_text(charger, distance):
    try:
        message = f'Cargador para <b>{PLACE_TYPE[charger["devices"][0]["placeType"]]} ' \
            f'{STATUS[charger["status"]]}</b> a ' \
            f'<b>{distance:0.0f}</b> metros en ' \
            f'<a href="https://www.google.com/maps/place/{charger["lat"]},{charger["lng"]}">' \
            f'<b>{charger["address"]}</b></a>\n'
    except KeyError as err:
        raise KeyError('Error generando los datos del cargador {}. No encuentro la equivalencia de: {}'
                       .format(json.dumps(charger), err))
    return message


def get_handler():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('lista', list_chargers_help),
                      CommandHandler('libres', free_chargers_help),
                      MessageHandler(Filters.location, request_radius),
                      MessageHandler(Filters.text, chargers_help)],
        states={
            LOCATION: [MessageHandler(Filters.location, request_radius)],
            RADIUS: [CallbackQueryHandler(search_chargers)],
        },
        fallbacks=[MessageHandler(Filters.text, chargers_help), MessageHandler(Filters.location, request_radius)]
    )
    return conv_handler

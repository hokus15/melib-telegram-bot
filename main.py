# main.py
# To deploy use: gcloud functions deploy webhook

import os
import telegram
import requests
import json
from flask import abort
from geopy import distance


# Radio por defecto en metros.
DEFAULT_RADIUS = 500

STATION_BASE_URL = 'https://ws.consorcidetransports.com/produccio/ximelib-mobile/rest/devicegroups'

HEADERS = {
    'content-type': "application/json",
    'accept-encoding': "gzip",
    'cache-control': "no-cache",
}

STATUS = {
    'AVAILABLE': 'libre',
    'OCCUPIED_PARTIAL': 'parcialmente ocupado'
}


SEND_LOCATION_INSTRUCTIONS = 'ℹ *Para enviar tu ubicación* ℹ \n' \
                             '1\\. Pulsa sobre el clip \\(📎\\) que encontrarás en la ventana de mensaje\\.\n' \
                             '2\\. Elige la opción de `Ubicación`\\.\n' \
                             '3\\. Elije `Enviar mi ubicación actual`\\.'


def webhook(request):
    # print(request.get_json(force=True))
    if _autheticate(request):
        bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
        if request.method == "POST":
            update = telegram.Update.de_json(request.get_json(force=True), bot)
            user_id = _get_user_id(update)
            if _is_valid_user(user_id):
                _handle_update(update)
            else:
                # Si el usuario no es válido
                update.message.reply_text(
                    text=f'Hola {update.message.from_user.first_name}, por '
                         'ahora, no puedes usar el bot, por favor proporciona '
                         f'el siguiente número: {user_id} al administrador\n'
                         'Una vez dado de alta prueba a enviarme tu ubicación:\n'
                         f'{SEND_LOCATION_INSTRUCTIONS}',
                    parse_mode=telegram.ParseMode.MARKDOWN_V2)
        return "ok"
    else:
        # Si no se ha podido verificar el token
        abort(403)


def _get_user_id(update):
    '''
    Obtiene el "user id" de telegram a partir de un mensaje.
    El "user id" está en un sitio distinto dependiendo del tipo de petición.
    '''
    user_id = ''
    if update.message:
        user_id = str(update.message.from_user.id)
    elif update.callback_query:
        user_id = str(update.callback_query.from_user.id)
    return user_id


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


def _is_valid_user(user):
    '''
    Comprueba si el "user id" de telegram está en la lista de usuarios admitidos.
    '''
    valid_users = os.environ['VALID_USERS'].split(';')
    if user in valid_users:
        return True
    else:
        return False


def _free_stations_in_range(location, radius):
    '''
    Devuelve una lista de las estaciones libres o parcialmente ocupadas dentro
    del radio de la ubicación.
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


def _handle_update(update):
    '''
    Gestiona las actualizaciones (peticiones) recibidas
    '''
    # Comprueba si la actualización contiene el campo "message".
    # Si tiene el campo message significa que no es un callback
    if update.message:
        # Comprueba si el mensaje contiene la ubicación
        if update.message.location:
            # Calcula las estaciones libres dentro del radio
            free_stations = _free_stations_in_range(
                update.message.location,
                DEFAULT_RADIUS)
            # Prepara la respuesta al usuario
            _reply_text(update, free_stations, DEFAULT_RADIUS)
        else:
            # Si el mensaje no tiene ubicación
            update.message.reply_text(
                text=f'⚠ Hola {update.message.from_user.first_name}, para poder darte '
                     'información de los cargadores que hay libres cerca de tu '
                     'posición, por favor, *envíame tu ubicación*\\.\n\n'
                     f'{SEND_LOCATION_INSTRUCTIONS}\n\n'
                     '‼ *ATENCIÓN* ‼\n'
                     'La distancia la mido en *linea recta* entre tu ubicación '
                     'y la ubicación del cargador\\. No tengo en cuenta la ruta '
                     'ni la altura de ninguno de los dos puntos\\. Por lo que la '
                     'distancia para llegar al cargador puede variar dependiendo '
                     'del camino que sigas hasta él\\.',
                parse_mode=telegram.ParseMode.MARKDOWN_V2)
    # Si es un callback (el usuario ha apretado un botón)
    elif update.callback_query:
        # Obtiene los datos del callback (posición y radio)
        callback_data = update.callback_query.data.split('#')
        # Si tiene posición y radio
        if len(callback_data) == 3:
            location = telegram.Location(float(callback_data[1]), float(callback_data[0]))
            radius = int(callback_data[2])
            # Calcula las estaciones libres dentro del radio
            free_stations = _free_stations_in_range(
                location,
                radius)
            # Prepara la respuesta al usuario
            _reply_text(update, free_stations, radius)
        # Si no tiene posición ni radio, es que el usuario no quiere hacer otra búsqueda.
        else:
            update.callback_query.answer()
            update.callback_query.edit_message_text(f'Vale {update.callback_query.from_user.first_name}, '
                                                    'tú mandas, no amplio el rádio de búsqueda.')


def _reply_text(update, stations, radius):
    '''
    Prepara el texto de respuesta
    '''
    message = ''
    # Si hay estaciones de carga dentro del radio
    if len(stations) > 0:
        # Ordena las estaciones de carga por distancia
        sorted_stations = sorted(stations.items(), key=lambda x: x[1])
        message += f'🎉🎊 He encontrado los siguientes cargadores disponibles en {radius} metros:\n\n'
        for station in sorted_stations:
            station_status_url = f'{STATION_BASE_URL}/{station[0]}'
            response = requests.request("GET", station_status_url, headers=HEADERS)
            station_status = response.json()
            message += f"🔌🆓 Cargador *{STATUS[station_status['status']]}* a " \
                       f"*{station[1]:0.0f}* metros en " \
                       f"[*{_escape_data(station_status['address'])}*]" \
                       f"(https://www.google.com/maps/place/{station_status['lat']},{station_status['lng']})\n"
        # Si la respuesta es a un mensaje normal
        if update.message:
            update.message.reply_text(
                parse_mode=telegram.ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
                text=message)
        # Si la respuesta es a un mensaje de callback
        elif update.callback_query:
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                parse_mode=telegram.ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
                text=message)
    # Si no se han encontrado estaciones de carga libres dentro del radio
    else:
        # Si la respuesta es a un mensaje normal
        if update.message:
            # Prepara la respuesta con las opciones
            base_callback_data = f'{update.message.location.latitude}#{update.message.location.longitude}'
            message = f'💩 No he encontrado cargadores libres en {radius} metros'
            update.message.reply_text(message)
            message = 'Podemos volver a probar ampliando el rádio de búsqueda a:'
            keyboard = [
                [
                    telegram.InlineKeyboardButton('1 Km', callback_data=f'{base_callback_data}#1000'),
                    telegram.InlineKeyboardButton('1,5 Km', callback_data=f'{base_callback_data}#1500'),
                    telegram.InlineKeyboardButton('2 Km', callback_data=f'{base_callback_data}#2000')
                ],
                [telegram.InlineKeyboardButton("No amplies el rádio de búsqueda", callback_data='0')]
            ]
            reply_markup = telegram.InlineKeyboardMarkup(keyboard)
            update.message.reply_text(message, reply_markup=reply_markup)
        # Si la respuesta es a un mensaje de callback
        elif update.callback_query:
            message = f'💩 ¡Vaya! Pues ni ampliando el radio de búsqueda a {radius} metros ' \
                'he encontrado cargadores libres, muévete un poco y vuelve a probar.'
            update.callback_query.answer()
            update.callback_query.edit_message_text(text=message)
    # print(message)


def _escape_data(s):
    '''
    Telegram tiene ciertos caracteres reservados que hay que reemplazar.
    '''
    return s.replace('_', '\\_') \
            .replace('*', '\\*') \
            .replace('[', '\\[') \
            .replace('`', '\\`') \
            .replace('.', '\\.')

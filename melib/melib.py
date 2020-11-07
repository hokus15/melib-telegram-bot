import requests
import json


_RESOURCE = "https://ws.consorcidetransports.com/produccio/ximelib-mobile/rest/"

_HEADERS = {
    "content-type": "application/json",
    "accept-encoding": "gzip",
    "cache-control": "no-cache",
}


def device_groups(payload):
    '''
    Devuelve una lista de los cargadores solicitados con su posición, estado e id.
    Se puede filtrar por los siguentes conceptos:
     placeType: Tipo de plaza.
     Posibles valores:
       CAR: Coche
       MOTORCYCLE: Moto

     idComponentType: Tipo Conector
     Se puede obtener una lista de cargadores válidos usando la siguiente
     petición GET : https://ws.consorcidetransports.com/produccio/ximelib-mobile/rest/devicecomponenttypes
     Posibles valores:
       1: Mennekes
       2: Shuko
       3: CSSCombo
       4: CHAdeMo

     chargeType: Tipo carga Posibles valores:
       CHARGE_MODE_2: Lenta
       CHARGE_MODE_3: Semi-rápida
       CHARGE_MODE_4: Rápida

     onlyAvailable: Mostrar sólo disponibles. true/false

    includeOffline:Mostrar no gestionados. true/false

    bounds:No he podido averiguar para que sirve
    '''
    response = requests.request(
        "POST",
        f"{_RESOURCE}devicegroups",
        data=json.dumps(payload),
        headers=_HEADERS)
    return response.json()


def device_groups_by_id(id):
    '''
    Devuelve el estado del cargador especificado.
    '''
    response = requests.request("GET", f"{_RESOURCE}devicegroups/{id}", headers=_HEADERS)
    return response.json()


def device_component_types():
    '''
    Devuelte los tipos de cargadores disponibles.
    '''
    response = requests.request("GET", f"{_RESOURCE}devicecomponenttypes", headers=_HEADERS)
    return response.json()


def sponsors():
    '''
    Devuelve los patrocinadores disponibles.
    '''
    response = requests.request("GET", f"{_RESOURCE}sponsors", headers=_HEADERS)
    return response.json()

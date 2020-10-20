# telegram-melib-bot
[![Build Status](https://img.shields.io/travis/hokus15/melib-telegram-bot?logo=travis)](https://travis-ci.com/github/hokus15/melib-telegram-bot) ![GitHub last commit](https://img.shields.io/github/last-commit/hokus15/melib-telegram-bot?logo=github) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/hokus15/melib-telegram-bot?logo=github)

Bot de telegram para comprobar las estaciones públicas de carga de vehículo eléctrico libres en las Islas Baleares en un radio de una ubicación proporcionada por el usuario.

La información es obtenida a partir de un servicio web (no publicado oficialmente) de [TIB](https://www.tib.org).

La información que muestra es la misma que puedes obtener desde la web oficial [Mapa de puntos de carga](https://www.tib.org/ximelib/public/map.xhtml)

El bot está desarrollado en Python 3.8 y desplegado en Google Cloud Platform usando Cloud Functions.

PR para mejorar la funcionalidad, la estructura o la legibilidad del código son bienvenidas.

## Cómo instalar el bot en tu cuenta de google cloud.
TODO completar
1. Despliega la función usando [Google Cloud Functions](https://cloud.google.com/functions/):
    1. Crea un proyecto de [Google Cloud Platform](https://cloud.google.com)
    1. Instala [gcloud command line utility](https://cloud.google.com/sdk/downloads).
    1. Despliega usando el siguiente comando: `$ gcloud functions deploy webhook --trigger-http` TODO pendiente de completar el comando
    1. Anota la URL 
1. Crea un [bot de telegram](https://core.telegram.org/bots#3-how-do-i-create-a-bot)
1. Asignar el webHook

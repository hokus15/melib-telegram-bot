from telethon import TelegramClient
from telethon.tl.custom.message import Message
from telethon.sessions import StringSession
import unittest
import aiounittest
import os
import sys


# Evita que falle en travis-ci ya que allí no está el fichero .env
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()


api_id = int(os.environ['TELEGRAM_APP_ID'])
api_hash = os.environ['TELEGRAM_APP_HASH']
session_str = os.environ['TELETHON_SESSION']


@unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
class ConversationTestCase(aiounittest.AsyncTestCase):

    async def test_1_conversation_no_chargers(self):
        radius = '500 m'
        print("Búsqueda de cargadores en cabrera en un radio de {}\n\n".format(radius))
        client = TelegramClient(StringSession(session_str), api_id, api_hash)
        await client.start()
        # Create a conversation
        async with client.conversation('@Devel_melib_bot', timeout=20) as conv:
            print('User > /libres\n')
            # User > /start
            await conv.send_message('/libres')
            # Bot < Hola Jordi, para poder darte información de los cargadores que
            # hay libres cerca de tu posición, por favor, envíame tu ubicación usando
            # el botón de abajo.
            resp: Message = await conv.get_response()
            self.assertTrue('Hola Jordi, para poder darte información de los cargadores que '
                            'hay cerca de tu posición, por favor, envíame tu ubicación usando '
                            'el botón de abajo.' in resp.raw_text)
#            print('Bot < {}\n[Enviar mi ubicación actual]\n\n'.format(resp.raw_text))
            # User > Click 'Enviar mi ubicación actual' button
            # Cabrera:
            latitude = 39.146895
            longitude = 2.950486
            print('User > Click en [Enviar mi ubicación actual] lat: {} - long: {}\n'.format(latitude, longitude))
            await resp.click(
                text='Enviar mi ubicación actual',
                share_geo=(longitude, latitude)
            )
            # Bot < ¿Qué radio de búsqueda quieres usar?
            # [500 m][1 Km][2 Km]
            # [3 Km] [5 Km][7 Km]
            resp = await conv.get_response()
            self.assertTrue('¿Qué radio de búsqueda quieres usar?' in resp.raw_text)
            self.assertTrue(resp.button_count == 6)
            self.assertTrue(resp.buttons[0][0].text == '500 m')
            self.assertTrue(resp.buttons[0][1].text == '1 Km')
            self.assertTrue(resp.buttons[0][2].text == '2 Km')
            self.assertTrue(resp.buttons[1][0].text == '3 Km')
            self.assertTrue(resp.buttons[1][1].text == '5 Km')
            self.assertTrue(resp.buttons[1][2].text == '7 Km')
#            print('Bot < {}\n[500 m][1 Km][2 Km]\n[3 Km ][5 Km][7 Km]\n\n'.format(resp.raw_text))
            print('User > Click en [{}]\n'.format(radius))
            await resp.click(text=radius)
            # Bot < List of free chargers
            # resp = await conv.get_edit()
            resp = await conv.get_response()
#            print('Bot < {}\n\n'.format(resp.raw_text))
            self.assertTrue(
                'No he encontrado cargadores disponibles en 500 metros, pero el más cercano es:' in resp.raw_text)
            self.assertTrue('Cargador para ' in resp.raw_text)
            self.assertEqual(resp.raw_text.count('Cargador para '), 1)
        await client.disconnect()
        await client.disconnected

    async def test_2_conversation_chargers(self):
        radius = '1 Km'
        print("Búsqueda de cargadores en Plaza de España en un radio de {}\n\n".format(radius))
        client = TelegramClient(StringSession(session_str), api_id, api_hash)
        await client.start()
        # Create a conversation
        async with client.conversation('@Devel_melib_bot', timeout=20) as conv:
            print('User > /libres\n')
            # User > /start
            await conv.send_message('/libres')
            # Bot < Hola Jordi, para poder darte información de los cargadores que
            # hay libres cerca de tu posición, por favor, envíame tu ubicación usando
            # el botón de abajo.
            resp: Message = await conv.get_response()
            self.assertTrue('Hola Jordi, para poder darte información de los cargadores que '
                            'hay cerca de tu posición, por favor, envíame tu ubicación usando '
                            'el botón de abajo.' in resp.raw_text)
#            print('Bot < {}\n[Enviar mi ubicación actual]\n\n'.format(resp.raw_text))
            # User > Click 'Enviar mi ubicación actual' button
            # Plaza España:
            latitude = 39.575416
            longitude = 2.654223
            print('User > Click en [Enviar mi ubicación actual] lat: {} - long: {}\n'.format(latitude, longitude))
            await resp.click(
                text='Enviar mi ubicación actual',
                share_geo=(longitude, latitude)
            )
            # Bot < ¿Qué radio de búsqueda quieres usar?
            # [500 m][1 Km][2 Km]
            # [3 Km] [5 Km][7 Km]
            resp = await conv.get_response()
            self.assertTrue('¿Qué radio de búsqueda quieres usar?' in resp.raw_text)
            self.assertTrue(resp.button_count == 6)
            self.assertTrue(resp.buttons[0][0].text == '500 m')
            self.assertTrue(resp.buttons[0][1].text == '1 Km')
            self.assertTrue(resp.buttons[0][2].text == '2 Km')
            self.assertTrue(resp.buttons[1][0].text == '3 Km')
            self.assertTrue(resp.buttons[1][1].text == '5 Km')
            self.assertTrue(resp.buttons[1][2].text == '7 Km')
#            print('Bot < {}\n[500 m][1 Km][2 Km]\n[3 Km ][5 Km][7 Km]\n\n'.format(resp.raw_text))
            print('User > Click en [{}]\n'.format(radius))
            await resp.click(text=radius)
            # Bot < List of free chargers
            # resp = await conv.get_edit()
            resp = await conv.get_response()
            print('Bot < {}\n\n'.format(resp.raw_text))
#            self.assertTrue(
#                'No he encontrado cargadores disponibles en 500 metros, pero el más cercano es:' in resp.raw_text)
#            self.assertTrue('Cargador para ' in resp.raw_text)
#            self.assertEqual(resp.raw_text.count('Cargador para '), 1)
        await client.disconnect()
        await client.disconnected

import main
import telegram
import json
import flask
import unittest
import re
import os
from telegram import Bot
from unittest.mock import patch
from werkzeug.exceptions import Forbidden

# Evita que falle en travis-ci ya que allí no está el fichero .env
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()


app = flask.Flask(__name__)


class MelibTestCase(unittest.TestCase):

    def test_webhook_autheticate_false(self):
        with open("test_text.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with app.test_request_context('?token=poiuytrewq', method="POST", data=f):
                    rq = flask.request
                    try:
                        main.webhook(rq)
                    except Exception as ex:
                        self.assertEqual(type(ex), Forbidden)

    def test_webhook_autheticate_true(self):
        with open("test_text.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with patch.object(Bot, "send_message", return_value="test message"):
                    with patch.object(Bot, "send_chat_action", return_value="test action"):
                        with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                            rq = flask.request
                            rs = main.webhook(rq)
                            self.assertEqual("ok", rs)

    def test_autheticate_true(self):
        with open("test_text.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                    r = flask.request
                    self.assertTrue(main._autheticate(r))

    def test_autheticate_false(self):
        with open("test_text.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with app.test_request_context('?token=poiuytrewq', method="POST", data=f):
                    r = flask.request
                    self.assertFalse(main._autheticate(r))

    def test_free_chargers_ok(self):
        with open("test_devicegroups_response_ok.json") as f:
            with patch("melib.melib.device_groups") as mock_devicegroups:
                mock_devicegroups.return_value = json.loads(f.read())
                location = telegram.Location(2.4916501, 39.3892373)
                response = main._free_chargers(location)
                self.assertEqual(len(response), 5)

    def test_free_chargers_bad_coordinates(self):
        with open("test_devicegroups_response_bad_coordinates.json") as f:
            with patch("melib.melib.device_groups") as mock_devicegroups:
                mock_devicegroups.return_value = json.loads(f.read())
                location = telegram.Location(2.4916501, 39.3892373)
                response = main._free_chargers(location)
                self.assertEqual(len(response), 4)
                self.assertTrue(684 not in response)

    def test_free_chargers_response_no_chargers(self):
        chargers = {}
        radius = 500
        location = telegram.Location(2.654223, 39.575416)
        response = main._free_chargers_response(chargers, radius, location)
        self.assertTrue(response.startswith('Algo muy gordo ha ocurrido'))

    def test_free_chargers_response_one_charger_available_not_in_radius(self):
        chargers = {
            23: 1000
        }
        radius = 500
        location = telegram.Location(2.654223, 39.575416)
        response = main._free_chargers_response(chargers, radius, location)
        self.assertTrue("No he encontrado cargadores disponibles en 500 metros" in response)
        self.assertTrue(re.search(r"Cargador para \*coche .*\* a \*1000\* metros.*", response, re.DOTALL))
        self.assertEqual(response.count("Cargador para *coche "), 1)

    def test_free_chargers_response_one_charger_in_radius(self):
        chargers = {
            23: 400
        }
        radius = 500
        location = telegram.Location(2.654223, 39.575416)
        response = main._free_chargers_response(chargers, radius, location)
        self.assertTrue('He encontrado los siguientes cargadores' in response)
        self.assertTrue(re.search(r"Cargador para \*coche .*\* a \*400\* metros.*", response, re.DOTALL))
        self.assertEqual(response.count("Cargador para *coche"), 1)

    def test_free_chargers_response_multiple_charger_in_radius(self):
        chargers = {
            23: 400,
            523: 342,
            684: 1203,
            690: 500,
            691: 501
        }
        radius = 500
        location = telegram.Location(2.654223, 39.575416)
        response = main._free_chargers_response(chargers, radius, location)
        self.assertTrue('He encontrado los siguientes cargadores' in response)
        self.assertTrue(re.search(r".*Cargador para \*coche .*\* a \*400\* metros.*", response, re.DOTALL))
        self.assertTrue(re.search(r".*Cargador para \*coche .*\* a \*342\* metros.*", response, re.DOTALL))
        self.assertTrue(re.search(r".*Cargador para \*coche .*\* a \*500\* metros.*", response, re.DOTALL))
        self.assertEqual(response.count("Cargador para *coche "), 3)

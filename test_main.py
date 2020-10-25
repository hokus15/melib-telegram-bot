import main
import telegram
import json
import flask
import unittest
import re
from unittest.mock import patch


app = flask.Flask(__name__)


class MelibTestCase(unittest.TestCase):

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
        with open("devicegroups_response_ok.json") as f:
            with patch("main.requests.request") as mock_devicegroups:
                mock_devicegroups.return_value.ok = True
                mock_devicegroups.return_value.json.return_value = json.loads(f.read())
                location = telegram.Location(2.4916501, 39.3892373)
                response = main._free_chargers(location)
                self.assertEqual(len(response), 5)

    def test_free_chargers_bad_coordinates(self):
        with open("devicegroups_response_bad_coordinates.json") as f:
            with patch("main.requests.request") as mock_devicegroups:
                mock_devicegroups.return_value.ok = True
                mock_devicegroups.return_value.json.return_value = json.loads(f.read())
                location = telegram.Location(2.4916501, 39.3892373)
                response = main._free_chargers(location)
                self.assertEqual(len(response), 4)
                self.assertTrue(684 not in response)

    def test_free_chargers_response_no_chargers(self):
        chargers = {}
        radius = 500
        response = main._free_chargers_response(chargers, radius)
        self.assertTrue(response.startswith('Algo muy gordo ha ocurrido'))

    def test_free_chargers_response_one_charger_available_not_in_radius(self):
        chargers = {
            23: 1000
        }
        radius = 500
        response = main._free_chargers_response(chargers, radius)
        self.assertTrue(response.startswith('No he encontrado cargadores disponibles en 500 metros'))
        self.assertTrue(re.search(r"Cargador para \*coche .*\* a \*1000\* metros.*", response, re.DOTALL))
        self.assertEqual(response.count("Cargador para *coche "), 1)

    def test_free_chargers_response_one_charger_in_radius(self):
        chargers = {
            23: 400
        }
        radius = 500
        response = main._free_chargers_response(chargers, radius)
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
        response = main._free_chargers_response(chargers, radius)
        self.assertTrue('He encontrado los siguientes cargadores' in response)
        self.assertTrue(re.search(r".*Cargador para \*coche .*\* a \*400\* metros.*", response, re.DOTALL))
        self.assertTrue(re.search(r".*Cargador para \*coche .*\* a \*342\* metros.*", response, re.DOTALL))
        self.assertTrue(re.search(r".*Cargador para \*coche .*\* a \*500\* metros.*", response, re.DOTALL))
        self.assertEqual(response.count("Cargador para *coche "), 3)


# TODO cambiar los assert de los strings para que independientemente del estado  no falle el assert.
# Usar expresiones regualares
# self.assertTrue(search("Cargador para *coche ?????* a *400* metros" in response", response))
if __name__ == "__main__":
    unittest.main()

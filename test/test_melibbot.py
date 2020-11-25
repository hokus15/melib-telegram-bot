import telegram
import json
import unittest
import re
import os
from unittest.mock import patch
from melibbot import melibbot

# Evita que falle en travis-ci ya que allí no está el fichero .env
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()


class MelibTestCase(unittest.TestCase):

    def test_free_chargers_ok(self):
        with open("test/test_devicegroups_response_ok.json") as f:
            with patch("melibbot.melib.device_groups") as mock_devicegroups:
                mock_devicegroups.return_value = json.loads(f.read())
                location = telegram.Location(2.4916501, 39.3892373)
                response = melibbot.chargers_list(location)
                self.assertEqual(len(response), 5)

    def test_free_chargers_bad_coordinates(self):
        with open("test/test_devicegroups_response_bad_coordinates.json") as f:
            with patch("melibbot.melib.device_groups") as mock_devicegroups:
                mock_devicegroups.return_value = json.loads(f.read())
                location = telegram.Location(2.4916501, 39.3892373)
                response = melibbot.chargers_list(location)
                self.assertEqual(len(response), 4)
                self.assertTrue(684 not in response)

    def test_free_chargers_response_no_chargers(self):
        chargers = {}
        radius = 500
        location = telegram.Location(2.654223, 39.575416)
        response = melibbot.chargers_response(chargers, radius, location)
        self.assertTrue(response.startswith('Algo muy gordo ha ocurrido'))

    def test_free_chargers_response_one_charger_available_not_in_radius(self):
        chargers = {
            23: 1000
        }
        radius = 500
        location = telegram.Location(2.654223, 39.575416)
        response = melibbot.chargers_response(chargers, radius, location)
        self.assertTrue("No he encontrado cargadores en 500 metros" in response)
        self.assertTrue(re.search(r"Cargador para <b>coche .*</b> a <b>1000</b> metros.*", response, re.DOTALL))
        self.assertEqual(response.count("Cargador para <b>coche "), 1)

    def test_free_chargers_response_one_charger_in_radius(self):
        chargers = {
            23: 400
        }
        radius = 500
        location = telegram.Location(2.654223, 39.575416)
        response = melibbot.chargers_response(chargers, radius, location)
        self.assertTrue('He encontrado los siguientes cargadores' in response)
        self.assertTrue(re.search(r"Cargador para <b>coche .*</b> a <b>400</b> metros.*", response, re.DOTALL))
        self.assertEqual(response.count("Cargador para <b>coche"), 1)

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
        response = melibbot.chargers_response(chargers, radius, location)
        self.assertTrue('He encontrado los siguientes cargadores' in response)
        self.assertTrue(re.search(r".*Cargador para <b>coche .*</b> a <b>400</b> metros.*", response, re.DOTALL))
        self.assertTrue(re.search(r".*Cargador para <b>coche .*</b> a <b>342</b> metros.*", response, re.DOTALL))
        self.assertTrue(re.search(r".*Cargador para <b>coche .*</b> a <b>500</b> metros.*", response, re.DOTALL))
        self.assertEqual(response.count("Cargador para <b>coche "), 3)

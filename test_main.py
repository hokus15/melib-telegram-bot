import main
import telegram
import json
import flask
import unittest
from unittest.mock import patch


app = flask.Flask(__name__)


class ClientTestCase(unittest.TestCase):
    #    def test_webhook_1_location(self):
    #        with open("test_location.json") as f:
    #            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
    #                                           'WEBHOOK_TOKEN': 'qwertyuiop',
    #                                           'VALID_USERS': '1234567890'}):
    #                with patch.object(telegram.Bot, "send_message", return_value="test message"):
    #                    with patch.object(telegram.Bot, "send_chat_action", return_value="test message"):
    #                        with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
    #                            r = flask.request
    #                            main.webhook(r)

    #    def test_webhook_2_callback(self):
    #        with open("test_callback.json") as f:
    #            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
    #                                           'WEBHOOK_TOKEN': 'qwertyuiop',
    #                                           'VALID_USERS': '1234567890'}):
    #                with patch.object(telegram.Bot, "answer_callback_query", return_value="test message"):
    #                    with patch.object(telegram.Bot, "edit_message_text", return_value="test message"):
    #                        with patch.object(telegram.Bot, "send_chat_action", return_value="test message"):
    #                            with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
    #                                r = flask.request
    #                                main.webhook(r)

    #    def test_webhook_3_text(self):
    #        with open("test_text.json") as f:
    #            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
    #                                           'WEBHOOK_TOKEN': 'qwertyuiop',
    #                                           'VALID_USERS': '1234567890'}):
    #                with patch.object(telegram.Bot, "send_message", return_value="test message"):
    #                    with patch.object(telegram.Bot, "send_chat_action", return_value="test message"):
    #                        with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
    #                            r = flask.request
    #                            main.webhook(r)

    #    def test_free_stations_in_range(self):
    #        location = telegram.Location(2.703475, 39.685317)
    #        radius = 100
    #        main._free_stations_in_range(location, radius)

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
        self.assertTrue("Cargador para *coche libre* a *1000* metros" in response)
        self.assertEqual(response.count("Cargador para *coche libre*"), 1)

    def test_free_chargers_response_one_charger_in_radius(self):
        chargers = {
            23: 400
        }
        radius = 500
        response = main._free_chargers_response(chargers, radius)
        self.assertTrue('He encontrado los siguientes cargadores' in response)
        self.assertTrue("Cargador para *coche libre* a *400* metros" in response)
        self.assertEqual(response.count("Cargador para *coche libre*"), 1)

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
        self.assertTrue("Cargador para *coche libre* a *400* metros" in response)
        self.assertTrue("Cargador para *coche libre* a *342* metros" in response)
        self.assertTrue("Cargador para *coche libre* a *500* metros" in response)
        self.assertEqual(response.count("Cargador para *coche libre*"), 3)


if __name__ == "__main__":
    unittest.main()

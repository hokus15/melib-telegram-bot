import main
import telegram
import flask
import unittest
from unittest.mock import patch


app = flask.Flask(__name__)


class ClientTestCase(unittest.TestCase):
    def test_webhook_1_location(self):
        with open("test_location.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with patch.object(telegram.Bot, "send_message", return_value="test message"):
                    with patch.object(telegram.Bot, "send_chat_action", return_value="test message"):
                        with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                            r = flask.request
                            main.webhook(r)

    def test_webhook_2_callback(self):
        with open("test_callback.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with patch.object(telegram.Bot, "answer_callback_query", return_value="test message"):
                    with patch.object(telegram.Bot, "edit_message_text", return_value="test message"):
                        with patch.object(telegram.Bot, "send_chat_action", return_value="test message"):
                            with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                                r = flask.request
                                main.webhook(r)

    def test_webhook_3_text(self):
        with open("test_text.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with patch.object(telegram.Bot, "send_message", return_value="test message"):
                    with patch.object(telegram.Bot, "send_chat_action", return_value="test message"):
                        with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                            r = flask.request
                            main.webhook(r)

#    def test_free_stations_in_range(self):
#        location = telegram.Location(2.703475, 39.685317)
#        radius = 100
#        main._free_stations_in_range(location, radius)


if __name__ == "__main__":
    unittest.main()

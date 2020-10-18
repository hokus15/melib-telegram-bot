from main import webhook

import unittest
from unittest.mock import patch

import flask
from telegram import Bot

app = flask.Flask(__name__)


class ClientTestCase(unittest.TestCase):
    def test_webhook_1_location(self):
        with open("test_location.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with patch.object(Bot, "send_message", return_value="test message"):
                    with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                        r = flask.request
                        webhook(r)

    def test_webhook_2_callback(self):
        with open("test_callback.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with patch.object(Bot, "answer_callback_query", return_value="test message"):
                    with patch.object(Bot, "edit_message_text", return_value="test message"):
                        with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                            r = flask.request
                            webhook(r)

    def test_webhook_3_text(self):
        with open("test_text.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with patch.object(Bot, "send_message", return_value="test message"):
                    with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                        r = flask.request
                        webhook(r)


if __name__ == "__main__":
    unittest.main()

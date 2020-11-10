import main
import flask
import unittest
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
        with open("test/test_text.json") as f:
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
        with open("test/test_text.json") as f:
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
        with open("test/test_text.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with app.test_request_context('?token=qwertyuiop', method="POST", data=f):
                    r = flask.request
                    self.assertTrue(main._autheticate(r))

    def test_autheticate_false(self):
        with open("test/test_text.json") as f:
            with patch.dict('os.environ', {'TELEGRAM_TOKEN': '0000:yyyy',
                                           'WEBHOOK_TOKEN': 'qwertyuiop',
                                           'VALID_USERS': '1234567890'}):
                with app.test_request_context('?token=poiuytrewq', method="POST", data=f):
                    r = flask.request
                    self.assertFalse(main._autheticate(r))

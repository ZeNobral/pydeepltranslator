import unittest
from unittest.mock import patch
from requests.exceptions import HTTPError
from requests import Response
from pydeepltranslator import DeepLTranslatorApi
from pydeepltranslator.exceptions import *


class TestDeepLTranslatorApi(unittest.TestCase):
    def setUp(self):
        self.dt = DeepLTranslatorApi(auth_key='ndnklqvlkjvknqslkden', source_lang='DE', target_lang='EN')
    
    @staticmethod
    def raise_HTTPError(status_code):
            r = Response()
            r.status_code = status_code

            def inner():
                raise HTTPError(response=r)
            return inner
    
    def test_raise_wrong_request(self):
        with patch('requests.post') as mock_request:
            text = 'test'
            mock_request.return_value.raise_for_status = self.raise_HTTPError(400)
            self.assertRaises(WrongRequest, self.dt, text)

    def test_raise_authorization_failed(self):
        with patch('requests.post') as mock_request:
            text = 'test'
            mock_request.return_value.raise_for_status = self.raise_HTTPError(403)
            self.assertRaises(AuthorizationFailed, self.dt, text)
            
    def test_raise_request_entity_too_large(self):
        with patch('requests.post') as mock_request:
            text = 'test'
            mock_request.return_value.raise_for_status = self.raise_HTTPError(413)
            self.assertRaises(RequestEntityTooLarge, self.dt, text)

    def test_raise_quota_exceeded(self):
        with patch('requests.post') as mock_request:
            text = 'test'
            mock_request.return_value.raise_for_status = self.raise_HTTPError(456)
            self.assertRaises(QuotaExceeded, self.dt, text)
            
    def test_response(self):
        with patch('requests.post') as mock_request:
            text = 'Hallo Welt!'
            mock_request.return_value.text = '{"translations":[{"detected_source_language":' \
                '"DE", "text": "Hello World!"}]}'
            res_json = self.dt(text)
            self.assertEqual(res_json['translations'][0]['detected_source_language'], 'DE')
            self.assertEqual(res_json['translations'][0]['text'], 'Hello World!')

    def test_wrong_lang(self):
        self.assertRaises(ValueError, setattr, self.dt, 'source_lang', 'BX')
        self.assertRaises(ValueError, setattr, self.dt, 'target_lang', 'BX')

    def test_lang_change(self):
        original_source_lang = self.dt.source_lang
        original_target_lang = self.dt.target_lang
        self.dt.source_lang = 'IT'
        self.dt.target_lang = 'EN'
        self.assertEqual(self.dt.payload['source_lang'], 'IT')
        self.assertEqual(self.dt.payload['target_lang'], 'EN')
        self.dt.source_lang = original_source_lang
        self.dt.target_lang = original_target_lang


import requests
import json
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from pydeepltranslator.exceptions import *


class DeepLTranslatorApi:
    _API_ENDPOINT = 'https://api.deepl.com/v1/translate'
    _ACCEPTED_LANGUAGES = {'EN', 'DE', 'FR', 'ES', 'IT', 'NL', 'PL'}
    _ACCEPTED_TAG_HANDLING = {'xml'}
      
    def __init__(self, auth_key, source_lang=None, target_lang=None,
                 tag_handling=None, split_sentences=True, preserve_formatting=False, jsonify=True, retries=5):
        if tag_handling:
            if tag_handling not in self._ACCEPTED_TAG_HANDLING:
                raise ValueError('{} is not a valid value for tag_handling,'
                                 ' must be one of the following : {}'.format(tag_handling, self._ACCEPTED_TAG_HANDLING))
        tag_handling_ = tag_handling
        split_sentences_ = 1 if split_sentences else 0
        preserve_formatting_ = 1 if preserve_formatting else 0
        self.payload = {
            'auth_key': auth_key,
            'tag_handling': tag_handling_,
            'split_sentences': split_sentences_,
            'preserve_formatting': preserve_formatting_
        }
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.jsonify = jsonify
        self.retries = 5
        
    @property
    def source_lang(self):
        return self._source_lang

    @source_lang.setter
    def source_lang(self, lang):
        lang = lang.upper()
        if lang not in self._ACCEPTED_LANGUAGES:
            raise ValueError('language not known, must be one of the following : {}'.format(self._ACCEPTED_LANGUAGES))
        self._source_lang = lang
        self.payload.update(source_lang=self.source_lang)

    @property
    def target_lang(self):
        return self._target_lang

    @target_lang.setter
    def target_lang(self, lang):
        lang = lang.upper()
        if lang not in self._ACCEPTED_LANGUAGES:
            raise ValueError('language not known, must be one of the following : {}'.format(self._ACCEPTED_LANGUAGES))
        self._target_lang = lang
        self.payload.update(target_lang=self.target_lang)

    def _make_request(self, text):
        payload = {'text': text}
        headers = {'Content-Length': len(text.encode('utf-8'))}
        payload.update(self.payload)
        headers.update(self.headers)
        try:
            r = requests.post(self._API_ENDPOINT, data=payload, headers=headers)
            r.raise_for_status()
            return r.text
            
        except requests.exceptions.HTTPError as e:
            sc = e.response.status_code
            if sc == 400:
                raise WrongRequest
            elif sc == 403:
                raise AuthorizationFailed
            elif sc == 413:
                raise RequestEntityTooLarge
            elif sc == 429:
                raise TooManyRequests
            elif sc == 456:
                raise QuotaExceeded
        
    def __call__(self, text):
        r_text = '{}'
        for i in range(self.retries):
            try:
                r_text = self._make_request(text)
            except TooManyRequests:
                sleep((i+1)*3)
                continue
            break
        content = json.loads(r_text, encoding='utf-8') if self.jsoninfy else r_text
        return content

    def translate_many(self, texts, max_threads=3):
        with ThreadPoolExecutor(max_workers=max_threads) as e:
            return list(e.map(self, texts))

import requests
import json


class WrongRequest(Exception):
    pass


class AuthorizationFailed(Exception):
    pass


class RequestEntityTooLarge(Exception):
    pass


class TooManyRequests(Exception):
    pass


class QuotaExceeded(Exception):
    pass


class DeepLTranslatorApi:
    _API_ENDPOINT = 'https://api.deepl.com/v1/translate'
    _ACCEPTED_LANGUAGES = {'EN', 'DE', 'FR', 'ES', 'IT', 'NL', 'PL'}
    _ACCEPTED_TAG_HANDLING = {'xml'}
      
    def __init__(self, auth_key, source_lang='FR', target_lang='IT',
                 tag_handling=None, split_sentences=True, preserve_formatting=False):
        if source_lang not in self._ACCEPTED_LANGUAGES or target_lang not in self._ACCEPTED_LANGUAGES:
            raise ValueError('language not known, must be one of the following : {}'.format(self._ACCEPTED_LANGUAGES))
        source_lang_ = source_lang
        target_lang_ = target_lang
        if tag_handling:
            if tag_handling not in self._ACCEPTED_TAG_HANDLING:
                raise ValueError('{} is not a valid value for tag_handling,'
                                 ' must be one of the following : {}'.format(tag_handling, self._ACCEPTED_LANGUAGES))
        tag_handling_ = tag_handling
        split_sentences_ = 1 if split_sentences else 0
        preserve_formatting_ = 1 if preserve_formatting else 0
        self.payload = {
            'auth_key': auth_key,
            'source_lang': source_lang_,
            'target_lang': target_lang_,
            'tag_handling': tag_handling_,
            'split_sentences': split_sentences_,
            'preserve_formatting': preserve_formatting_
        }
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
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
        
    def __call__(self, text, jsoninfy=True):
        r_text = self._make_request(text)
        content = json.loads(r_text, encoding='utf-8') if jsoninfy else r_text
        return content

# pydeepltranslator

Simple Python API wrapper for the [deepl translation service](https://www.deepl.com/api.html)

## how to use
```
from pydeepltranslator import DeepLTranslatorApi

api_key = 'my_api_key'
text_to_translate = 'Hello World!'
deepl_api = DeepLTranslatorApi(api_key, source_lang='EN', target_lang='DE'
json_resp = deepl_api(text_to_translate)
translation = json_resp['translations'][0]['text']
```
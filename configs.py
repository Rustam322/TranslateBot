TOKEN = '2097411935:AAGdmu6ZXLZXkfw1F9_I15ZiFgv6pvWTY8o'

LANGUAGES = {
    'ru': 'Русский',
    'en': 'Английский',
    'fr': 'Французский',
    'it': 'Итальянский',
    'ja': 'Японский',
    'de': 'Немецкий',
    'kk': 'Казахский',
    'hi': 'Индийский'
}

def get_key(value):
    for k, v in LANGUAGES.items():
        if v == value:
            return k





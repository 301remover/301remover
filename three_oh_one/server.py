from flask import Flask, request, jsonify
import lmdb
from three_oh_one.base_converter.base_converter import BaseConverter

from three_oh_one.services.bitly import BitlyService

from three_oh_one.client.params import PARAMS

FULL_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
FULL_ALPHABET_NO_UNDERSCORE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
ALPHANUMERIC = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHANUMERIC_LOWERCASE = '0123456789abcdefghijklmnopqrstuvwxyz'

ALPHABETS = {
    'bit.ly': FULL_ALPHABET,
    'is.gd': FULL_ALPHABET_NO_UNDERSCORE,
    'ow.ly': ALPHANUMERIC,
    'snipurl.com': "0123456789abcdefghijklmnopqrstuvwxyz-_~",
    'tinyurl.com': ALPHANUMERIC_LOWERCASE,
}

DBS = {
    'bit.ly': lmdb.open('/data/db/bit.ly', max_dbs=0, map_size=2 ** 40),
}

RESOLVERS = {
    'bit.ly': BitlyService(PARAMS['bitly'])
}


def get_from_db(shortener, shortcode):
    database = DBS.get(shortener, None)
    if database is None:
        return None

    converter = BaseConverter(ALPHABETS[shortener])

    with database.begin(write=False) as txn:
        key = converter.str_to_bytes(shortcode)
        result = txn.get(key)
        if result is None:
            return None

        return result.decode()


def store_in_db(shortener, shortcode, url):
    env = DBS[shortener]
    converter = BaseConverter(ALPHABETS[shortener])
    with env.begin(write=True) as txn:
        key = converter.str_to_bytes(shortcode)
        assert shortcode == converter.bytes_to_str(key)
        txn.put(key, url.encode())


def get_from_real_service(shortener, shortcode):
    print('getting from real service', shortener, shortcode)
    resolver = RESOLVERS.get(shortener, None)
    if resolver is None:
        return None

    response = resolver.scrape_one(shortcode)
    print('response', response)
    if response is None:
        return None

    url = response['url']
    shortcode = response['shortcode']
    store_in_db(shortener, shortcode, url)

    return url

app = Flask(__name__)


@app.route('/')
def index():
    return "301 remover is running!"


@app.route('/api/bulk_resolve', methods=['POST'])
def bulk_resolve():
    content = request.get_json()
    for i in range(len(content)):
        [shortener, shortcode] = content[i].split('/')
        content[i] = get_from_db(shortener, shortcode)

        if content[i] is not None:
            # don't bother trying the real service if we've already got it
            continue

        content[i] = get_from_real_service(shortener, shortcode)



    return jsonify(content)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

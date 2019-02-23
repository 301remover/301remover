from flask import Flask, request, jsonify
import lmdb
from three_oh_one.base_converter.base_converter import BaseConverter

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
    'bit.ly': lmdb.open('./db/bit.ly', max_dbs=0, map_size=2 ** 40),
}

def get_from_db(shortener, shortcode):
    database = DBS.get(shortener, None)
    if database == None:
        return None

    converter = BaseConverter(ALPHABETS[shortener])

    with database.begin(write=False) as txn:
        key = converter.str_to_bytes(shortcode)
        result = txn.get(key)
        if result == None:
            return None

        return result.decode()

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

    return jsonify(content)

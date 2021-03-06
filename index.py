from flask import Flask
from flask import redirect as flask_redirect
from flask import request  as flask_request

from miniapi import MiniApi
from BashOrg import Quotes

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

_VERSION_ = '0.1.2'
_DEBUG_ = False

APP_HEADERS = {
        "X-Source-Url": "https://github.com/Konrov/BashOrg-quotes-api",
        "X-Parser-Ver": _VERSION_,
        "Server": "Flask"
}

Api = MiniApi(APP_HEADERS)
quotes = Quotes()

@app.errorhandler(404)
def not_found404(error):

    return flask_redirect(APP_HEADERS.get("X-Source-Url"))


@app.errorhandler(500)
def internal_error(error):

    return Api.ret_error(error.name, error.description, error.code)


@app.route('/')
def index_route():

    return flask_redirect(APP_HEADERS.get("X-Source-Url"))


@app.route('/quote')
def quote_by_id():

    if not Api.query_key_exists(flask_request.args, 'id'):
        return Api.ret_error("id query parameter has not set.")
    qid = flask_request.args.get('id')

    if not isinstance(qid, int):
        try:
            qid = int(qid)
        except ValueError:
            return Api.ret_error("id query parameter is not int.")

    quote_details = quotes.new_quote(qid)
    if not quote_details:
        return Api.ret_error("Bash.im server returned unexpected response.")

    quote_id, quote_date, quote_text = quote_details

    _response = {
        'id': quote_id,
        'date': quote_date,
        'text': quote_text
    }

    return Api.ret_ok("quote", _response)


@app.route('/random-quote')
def random_quote():

    quote_details = quotes.new_quote()
    if not quote_details:
        return Api.ret_error("Bash.im server returned unexpected response.")

    quote_id, quote_date, quote_text = quote_details

    _response = {
        'id': quote_id,
        'date': quote_date,
        'text': quote_text
    }

    return Api.ret_ok("quote", _response)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=_DEBUG_)

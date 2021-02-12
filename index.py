from flask import Flask
from flask import request as flask_request
from flask import redirect as flask_redirect

from MiniApi import MiniApi
from BashOrg import Quotes

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

_version_ = '0'
_debug_ = False

APP_HEADERS = {
        "X-Source-Url": "https://github.com/Konrov",
        "X-Parser-Ver": _version_,
        "Server": "Flask"
}

Api = MiniApi(APP_HEADERS)
Quotes = Quotes()

@app.errorhandler(404)
def not_found404(error):
    
    return flask_redirect(APP_HEADERS.get("X-Source-Url"))


@app.errorhandler(500)
def internal_error(error):
    
    return Api.ret_error("Internal server error")


@app.route('/')
def index_route():
    
    return flask_redirect(APP_HEADERS.get("X-Source-Url"))


@app.route('/random-quote')
def random_quote():
    
    quote_details = Quotes.get_new_quote()
    if not quote_details:
        return Api.ret_error("Bash.im server returned unexpected response")
    quote_id, quote_date, quote_text = quote_details
    
    _response = {
        'id': quote_id,
        'date': quote_date,
        'text': quote_text
    }
    
    return Api.ret_ok("quote", _response)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=_debug_)

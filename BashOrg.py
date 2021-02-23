import re
from typing import List
from random import randint      as random_randint
from random import choice       as random_choice
from html   import unescape     as html_unescape
from json   import loads        as json_loads
from httpx  import get          as httpx_get


class Quotes:


    LATEST_ID: int = 0

    # In-memory list of quotes
    CACHED_QUOTES: List[list] = []


    def __init__(this,
                use_cache: bool = True,
                cache_limit: int = 100):

        this._cache = use_cache
        this._limit = cache_limit


    @classmethod
    def update_latest(cls, quote_id: int) -> None:

        cls.LATEST_ID = quote_id


    @classmethod
    def __cache_append(cls, quote: list) -> None:

        cls.CACHED_QUOTES.append(quote)


    @classmethod
    def __cache_update(cls, updated_cache: list) -> None:

        cls.CACHED_QUOTES = updated_cache


    def cache_append(this, quote: list) -> None:

        if not this._cache:
            return
        quote_id = quote[0]
        cached_quotes = this.CACHED_QUOTES
        cache_len = len(cached_quotes)

        if cache_len > this._limit:

            # Cut off half of the list if it contains more quotes
            # than set in cache_limit

            this.__cache_update(cached_quotes[int(cache_len * 0.5):])
            cached_quotes = this.CACHED_QUOTES

        for _quote in cached_quotes:
            if quote_id in _quote:
                return

        this.__cache_append(quote)


    @staticmethod
    def __clean_html(raw_html: str) -> str:
        # stackoverflow.com/a/12982689
        # cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext


    def __magic(this, text: str) -> str:

        """
        Bash.im response example:

            var scripts = document.getElementsByTagName('script');
            var script = scripts[scripts.length - 1];
            var borq='';
            borq += '<' + 'article <...long html tags...> /article>';
            setTimeout(function() {
              script.outerHTML += borq;
            }, 500);

        """

        # 1. Splitting JavaScript code into lines list (\n)
        # and assigning 3 (4) line (see example code)
        text = text.split('\n')[3]

        # 2. Remove ';' from end of string
        text = text[:-1]

        # 3. Escape double quotes
        text = text.replace(r'"', r'\"')

        # 4. Replace the stupid '<br>'s to normal new-line char
        text = text.replace(r"<' + 'br>", '\n')

        # 5. Also remove js var assigning ('borq += ')
        text = text[8:]

        # 6. And delete unnecessary single-quotes from start and end of string
        text = text[1:-1]

        # 7. Clean html tags
        text = this.__clean_html(text)

        # 8. Finally, removing html entities
        text = html_unescape(text)

        return text


    def __get_quote_details(this, quote: str) -> List[str]:

        quote = this.__magic(quote)

        re_find_date = r"\d{2}.\d{2}.\d{4}"
        re_find_id = r"\#\d+"

        # In order not to affect all dates in the text,
        # we are looking only in the first 30 chars

        finded_dates = re.findall(re_find_date, quote[:30])
        quote_date = finded_dates[0]

        quote_st = quote[:30].replace(quote_date, " {}\n".format(quote_date))
        quote = quote_st + quote[30:]

        # Also remove 'Больше на bash.im!' from the end
        quote = quote[:-18]

        # Splitting, because the date and ID now are on the first line
        finded_id = re.findall(re_find_id, quote.split('\n')[0])
        quote_id = finded_id[0][1:] # Remove "#"

        # Finally, remove first line with id and date
        _quote = quote.split('\n')[1:]
        quote = '\n'.join(_quote)

        return [quote_id, quote_date, quote]


    def __get_new_quote(this) -> List[str]:

        url = 'https://bash.im/forweb/?{}'.format(random_randint(0, 100500))
        resp = httpx_get(url).text
        if 'borq' not in resp:
            return []
        return this.__get_quote_details(resp)


    def __get_cached_quote(this) -> List[str]:

        return random_choice(this.CACHED_QUOTES)


    def __get_quote_by_id(this, qid: int) -> List[str]:

        for quote in this.CACHED_QUOTES:
            if qid == int(quote[0]):
                # Quote already in cache
                return quote

        # Attention! The following lines may contain hardcode
        # and are not recommended to reading for BeautifulSoup fans.
        _response = httpx_get('https://bash.im/quote/{}'.format(qid))
        if _response.status_code != 200:
            return []

        html_text = _response.text
        if not re.findall('<title>(.*?)</title>', html_text)[0].startswith('Цитата'):
            # On main page
            return []

        if 'title="Поделиться цитатой">' not in html_text:
            # Error page or something else
            return []

        # Format:
        # {"id": "id", "url": "quote/id", "title": "Цитата #id", "description": "text"}
        share_dict = re.findall("data-share=\'(.*?)\' title=", html_text)[0]
        quote_dict = json_loads(share_dict)

        quote_id = quote_dict.get('id')

        _quote_text_html = quote_dict.get('description')
        quote_text = html_unescape(_quote_text_html).replace('<br />', '\n').replace('<br>', '\n')
        quote_text = html_unescape(quote_text) # To be sure

        _quote_date_full = re.findall('quote__header_date\">(.*?)</div>', html_text, re.DOTALL)[0]
        quote_date = re.findall(r"\d{2}.\d{2}.\d{4}", _quote_date_full)[0]

        this.cache_append([quote_id, quote_date, quote_text])

        return [quote_id, quote_date, quote_text]


    def new_quote(this, get_id: int = None) -> List[str]:

        if get_id:
            quote = this.__get_quote_by_id(get_id)
        else:
            quote = this.__get_new_quote()

        if not quote:
            return []

        quote_id, quote_date, quote_text = quote

        # For update_latest
        _id: int = int(quote_id)

        if quote_id == this.LATEST_ID and this._cache and \
            len(this.CACHED_QUOTES) * 100 / this._limit > 20:

            # If the number of quotes in the list reaches
            # at least 20% of the limit

            quote_id, quote_date, quote_text = this.__get_cached_quote()

        this.update_latest(_id)
        this.cache_append(quote)

        return [quote_id, quote_date, quote_text]

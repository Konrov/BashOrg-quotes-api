import re
from typing import List
from random import randint as random_randint
from random import choice as random_choice
from html import unescape as html_unescape
from httpx import get as httpx_get




# TODO:
#     - Change flask to sanic

class Quotes:


    LATEST_ID: int = 0

    # In-memory list of quotes
    CACHED_QUOTES: List[list] = []


    def __init__(self,
                use_cache: bool = True,
                cache_limit: int = 100):

        self._cache = use_cache
        self._limit = cache_limit


    @classmethod
    def update_latest(cls, quote_id: int) -> None:

        cls.LATEST_ID = quote_id


    @classmethod
    def __cache_append(cls, quote: list) -> None:

        cls.CACHED_QUOTES.append(quote)


    @classmethod
    def __cache_update(cls, updated_cache: list) -> None:

        cls.CACHED_QUOTES = updated_cache


    def cache_append(self, quote: list) -> None:

        if not self._cache:
            return
        quote_id = quote[0]
        cached_quotes = self.CACHED_QUOTES
        cache_len = len(cached_quotes)

        if cache_len > self._limit:

            # Cut off half of the list if it contains more quotes
            # than set in cache_limit

            self.__cache_update(cached_quotes[int(cache_len * 0.5):])
            cached_quotes = self.CACHED_QUOTES

        for _quote in cached_quotes:
            if quote_id in _quote:
                return

        self.__cache_append(quote)


    @staticmethod
    def __clean_html(raw_html: str) -> str:
        # stackoverflow.com/a/12982689
        # cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext


    def __magic(self, text: str) -> str:

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
        text = self.__clean_html(text)

        # 8. Finally, removing html entities
        text = html_unescape(text)

        return text


    def __get_quote_details(self, quote: str) -> List[str]:

        quote = self.__magic(quote)

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


    def __get_new_quote(self) -> List[str]:

        url = 'https://bash.im/forweb/?{}'.format(random_randint(0, 100500))
        resp = httpx_get(url).text
        if 'borq' not in resp:
            return []
        return self.__get_quote_details(resp)


    def __get_cached_quote(self) -> List[str]:

        return random_choice(self.CACHED_QUOTES)


    def new_quote(self) -> List[str]:

        quote = self.__get_new_quote()
        if not quote:
            return []

        quote_id, quote_date, quote_text = quote

        # For update_latest
        _id: int = int(quote_id)

        if quote_id == self.LATEST_ID and self._cache and \
            len(self.CACHED_QUOTES) * 100 / self._limit > 20:

            # If the number of quotes in the list reaches
            # at least 20% of the limit

            quote_id, quote_date, quote_text = self.__get_cached_quote()

        self.update_latest(_id)
        self.cache_append(quote)

        return [quote_id, quote_date, quote_text]

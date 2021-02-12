import re
from httpx import get as httpx_get
from random import randint as random_randint
from html import unescape
from time import sleep as time_sleep


"""
TODO:
    - In-memory list with 100+ quotes for more responsibility
    - Change flask to sanic
"""

class Quotes:
    
    """
    Bashorg (Bash.im) quotes mini api.
    wardsenz at konrov dot com
    
    """
    
    LATEST_ID = 0
    ATTEMPS = 1
    
    
    def __init__(self, retry_if_same=False, debug=False):
        self._debug = debug
        self._retry = retry_if_same
    
    
    @classmethod
    def update_latest(cls, id):
        cls.LATEST_ID = id
    
    
    @classmethod
    def update_attemps(cls):
        cls.ATTEMPS *= 3
    
    
    @classmethod
    def reset_attemps(cls):
        cls.ATTEMPS = 1
    
    
    def __clean_html(self, raw_html):
        """ stackoverflow.com/a/12982689 """
        # cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    
    
    def __magic(self, text):
        
        """
        Response example:
            
            var scripts = document.getElementsByTagName('script');
            var script = scripts[scripts.length - 1];
            var borq='';
            borq += '<' + 'article <...very long html tags...> /article>';
            setTimeout(function() {
              script.outerHTML += borq;
            }, 500);

        
        1. 
        Splitting JavaScript code into lines list (\n)
        and assigning 3 (4) line (see example code)
        
        """
        text = text.split('\n')[3]
        
        """ 2. Remove ';' from end of string """
        text = text[:-1]
        
        """ 3. Escape double quotes """
        text = text.replace(r'"', r'\"')
        
        """ 4. Replace the stupid '<br>'s to normal new-line char """
        text = text.replace(r"<' + 'br>", '\n')
        
        """ 5. Also remove js var assigning ('borq += ') """
        text = text[8:]
        
        """ 6. And delete unnecessary single-quotes from start and end of string """
        text = text[1:-1]
        
        """ 7. Clean html tags """
        text = self.__clean_html(text)
        
        """ 8. Finally, removing html entities """
        text = unescape(text)
        
        return text
    
    
    def __get_quote_details(self, quote):
        
        quote = self.__magic(quote)
        
        re_find_date = r"\d{2}.\d{2}.\d{4}"
        re_find_id = r"\#\d+"
        
        
        """
        In order not to affect all dates in the text,
        we are looking only in the first 30 chars
        
        """
        finded_dates = re.findall(re_find_date, quote[:30])
        quote_date = finded_dates[0]
        
        quote_st = quote[:30].replace(quote_date, " {}\n".format(quote_date))
        quote = quote_st + quote[30:]
        
        """ Also remove 'Больше на bash.im!' from the end """
        quote = quote[:-18]
        
        """ Splitting, because the date and ID now are on the first line """
        finded_id = re.findall(re_find_id, quote.split('\n')[0])
        quote_id = finded_id[0][1:] # Remove "#"
        
        """ Finally, remove first line with id and date """
        quote = quote.split('\n')[1:]
        quote = '\n'.join(quote)
        
        return [quote_id, quote_date, quote]
    
    
    def get_new_quote(self):
        
        response = httpx_get('https://bash.im/forweb/?{}'.format(random_randint(0, 84294)))
        response = response.text
        if 'borq' not in response:
            return False
        id, date, quote = self.__get_quote_details(response)
        if self._retry and id == self.LATEST_ID:
            time_sleep(self.ATTEMPS)
            if self._debug:
                print("Got same id. Sleeping for {}".format(self.ATTEMPS))
            self.update_attemps()
            self.get_new_quote()
        self.update_latest(id)
        self.reset_attemps()
        
        return [id, date, quote]


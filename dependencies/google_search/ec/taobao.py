from urllib.parse import unquote
import requests
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class TaobaoCustomized:

    def __init__(self, target_url: str):

        self.target_url = unquote(target_url)
        self.domain_fetch = re.compile('world.taobao.com')
        self.category_fetch = re.compile('https://world.taobao.com/product')
        self.product_fetch = re.compile('https://world.taobao.com/item')
        self.headers = headers = {'User-Agent': ''}
        self.ua = UserAgent()

    def execute(self):
        if not re.search(self.domain_fetch, self.target_url):
            return 0
        taobao_contents_result = []
        if re.search(self.category_fetch, self.target_url):
            product_url_list = self._taobao_category(url=self.target_url)
            for product_url in product_url_list:
                title, url, text = self._taobao_product(url=product_url)
                taobao_contents_result.append([title, url, text])
                del title, url, text

        elif re.match(self.product_fetch, self.target_url):
            title, url, text = self._taobao_product(url=self.target_url)
            taobao_contents_result.append([title, url, text])
            del title, url, text
            
        return taobao_contents_result

    def _taobao_category(self, url: str):
        """
        return: product url list
        drop duplicate url
        """
        url_list = []
        res = self._session_requests(url=url)
        soup = BeautifulSoup(res.text, 'lxml')
        url_list = [i.a.attrs['href'] for i in soup.findAll('div',{'class': 'item-box'})]
        url_list = list(set(url_list))
        return url_list

    def _taobao_product(self, url: str):

        res = self._session_requests(url=url)
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.title.text
        title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', title)
        text = '。'.join(i.text for i in soup.find('div', {'class': 'spu-conatiner panel'}).findAll('li'))
        text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', text)

        return title, url, text

    def _session_requests(self, url: str):
        """
        Future: Add proxy ip list
            session_requests.proxies
        """
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        requests.adapters.DEFAULT_RETRIES = 5
        session_requests= requests.session()
        session_requests.keep_alive = False
        session_requests.headers = headers
        res = session_requests.get(url)
        return res

if __name__ == "__main__":
    import sys
    target_url = sys.argv[1]
    TEST = TaobaoCustomized(target_url=target_url).execute()
    print(TEST.__next__())

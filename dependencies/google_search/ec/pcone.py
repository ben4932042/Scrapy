import re
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class PconeCustomized:
    def __init__(self, target_url: str):

        self.target_url = unquote(target_url)
        self.domain_fetch = re.compile('www.pcone.com.tw')
        self.category_fetch = re.compile('https://www.pcone.com.tw/search')
        self.product_fetch = re.compile('https://www.pcone.com.tw/product/info')
        self.headers = {'User-Agent': ''}
        self.ua = UserAgent()

    def execute(self):
        if not re.search(self.domain_fetch, self.target_url):
            return 0
        pcone_contents_result = []
        if re.search(self.category_fetch, self.target_url):
            product_url_list = self._rakuten_category(url=self.target_url)
            for product_url in product_url_list:
                title, url, text = self._rakuten_product(url=product_url)
                pcone_contents_result.append([title, url, text])
                del title, url, text

        elif re.match(self.product_fetch, self.target_url):
            title, url, text = self._rakuten_product(url=self.target_url)
            pcone_contents_result.append([title, url, text])
            del title, url, text
        
        return pcone_contents_result

    def _rakuten_category(self, url: str):
        """
        return: product url list
        drop duplicate url
        """
        url_list = []
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        soup_url = soup.findAll('a', {'class': 'product-list-item'})
        for ele in soup_url:
            product_url = 'https://www.pcone.com.tw' + ele.attrs['href']
            url_list.append(product_url)
        return url_list

    def _rakuten_product(self, url: str):
        """
        return: product desc
        """
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.title.text
        title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', title)
        text = '。'.join(i.attrs['content'] for i in soup.findAll('meta', {'name': 'description'}))
        text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', text)

        return title, url, text

if __name__ == "__main__":
    import sys
    target_url = sys.argv[1]

    TEST = PconeCustomized(target_url=target_url).execute()
    print(TEST.__next__())

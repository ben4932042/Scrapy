import re
import requests
import time
import random
from urllib.parse import unquote
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class Buy123Customized:
    
    def __init__(self, target_url: str):

        self.target_url = unquote(target_url)
        self.domain_fetch = re.compile('www.buy123.com.tw')
        self.category_fetch = re.compile('https://www.buy123.com.tw/site/search')
        self.product_fetch = re.compile('https://www.buy123.com.tw/site+.+ref=d_search_product_+[0-9]+')
        self.headers = headers = {
                                'User-Agent': '',
                                'referer': 'https://www.buy123.com.tw/',
                                'origin': 'https://www.buy123.com.tw',
                                }
        self.ua = UserAgent()
        
    def execute(self):
        buy123_contents_result = []
        if not re.search(self.domain_fetch, self.target_url):
            return 0

        if re.search(self.category_fetch, self.target_url):
            product_url_list = self._buy123_category(url=self.target_url)
            for product_url in product_url_list:
                title, url, text = self._buy123_product(url=product_url)
                buy123_contents_result.append([title, url, text])
                del title, url, text
        
        elif re.match(self.product_fetch, self.target_url):
            title, url, text = self._buy123_product(url=self.target_url)
            buy123_contents_result.append([title, url, text])
            del title, url, text

        return buy123_contents_result

    def _buy123_category(self, url: str):
        """
        return: product url list
        drop duplicate url
        """
        url_list = []
        headers = self.headers
        headers['User-Agent'] = self.ua.firefox
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        soup_url = soup.find('div', {'class': 'item-list-wrapper'}).findAll('a')
        for ele in soup_url:
            product_url = 'https://www.buy123.com.tw' + ele.attrs['href']
            if re.match(self.product_fetch, product_url):
                if int(product_url.split('d_search_product_')[1]) < 50:
                    url_list.append(product_url)
        url_list = list(set(url_list))
        return url_list

    def _buy123_product(self, url: str):
        headers = self.headers
        headers['User-Agent'] = self.ua.firefox
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        content = soup.find('div', {'id': 'item-main-content'})
        try:
            title = content.h1.text
        except:
            time.sleep(random.randint(0, 1))
            title = ''
        title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', title)
        try:
            text = content.p.text
        except:
            time.sleep(random.randint(0, 1))
            text = ''
        text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', text)
        
        return title, url, text

if __name__ == "__main__":
    import sys
    target_url = sys.argv[1]
    test = Buy123Customized(target_url=target_url).execute()
    while True:
        try:
            print(test.__next__())
        except StopIteration:
            break

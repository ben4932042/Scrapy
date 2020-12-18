from urllib.parse import unquote
import requests
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class YahooSaleCustomized:

    def __init__(self, target_url: str):

        self.target_url = unquote(target_url)
        self.domain_fetch = re.compile('tw.bid.yahoo.com')
        self.category_fetch = re.compile('https://tw.bid.yahoo.com/search/auction/product\?ht=+[\u4e00-\u9fa5]+')
        self.product_fetch = re.compile('https://tw.bid.yahoo.com/item/[0-9]+')
        self.headers = headers = {'User-Agent': ''}
        self.ua = UserAgent()

    def execute(self):
        if not re.search(self.domain_fetch, self.target_url):
            return 0
        yahoo_sale_contents_result = []
        if re.search(self.category_fetch, self.target_url):
            product_url_list = self._yahoo_category(url=self.target_url)
            for product_url in product_url_list:
                title, url, text = self._yahoo_product(url=product_url)
                yahoo_sale_contents_result.append([title, url, text])
                del title, url, text

        elif re.match(self.product_fetch, self.target_url):
            title, url, text = self._yahoo_product(url=self.target_url)
            yahoo_sale_contents_result.append([title, url, text])
            del title, url, text

        return yahoo_sale_contents_result

    def _yahoo_category(self, url: str):
        """
        return: product url list
        drop duplicate url
        """
        url_list = []
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        soup_url = soup.find('ul', {'class': 'gridList'}).findAll('a')
        for ele in soup_url:
            product_url = ele.attrs['href']
            if re.match(self.product_fetch, product_url):
                url_list.append(product_url)
        url_list = list(set(url_list))
        return url_list

    def _yahoo_product(self, url: str):

        headers = self.headers
        headers['User-Agent'] = self.ua.random
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.title.text
        title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', title)
        try:
            product_tag = re.sub('#','。', '。'.join(i.text for i in soup.findAll('div', {'class': 'tagsRow__3AkOv'})))
        except:
            product_tag = ''
        try:
            product_desc = '。'.join(i.text for i in soup.find('div', {'class': 'pure-u-1 pure-u-md-1-2 pure-u-lg-3-5 itemBasic__mAugX'}).find('form', {'id': 'addCartForm'}).find('li'))
        except:
            product_desc = ''
        text = product_tag + '。' + product_desc
        text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', text)

        return title, url, text

if __name__ == "__main__":
    import sys
    URL = sys.argv[1]
    TEST = YahooSaleCustomized(target_url=URL).execute()
    print(TEST.__next__())

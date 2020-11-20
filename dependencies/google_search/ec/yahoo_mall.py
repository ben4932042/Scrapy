import re
from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class YahooMallCustomized:
    """
    return type: generator
    """
    def __init__(self, target_url: str):
        """
        initial setting
        """
        self.target_url = unquote(target_url)
        self.domain_fetch = re.compile('tw.mall.yahoo.com')
        self.category_fetch = re.compile('https://tw.mall.yahoo.com/+[\u4e00-\u9fa5|-]+[0-9|-]+category.html')
        self.product_fetch = re.compile('https://tw.mall.yahoo.com/item/p+[0-9]+')
        self.headers = headers = {'User-Agent': ''}
        self.ua = UserAgent()

    def execute(self):
        """
        execute crawl with some limit condition
        """
        if not re.search(self.domain_fetch, self.target_url):
            return
        yahoo_mall_contents_result = []
        if re.search(self.category_fetch, self.target_url):
            product_url_list = self._yahoo_category(url=self.target_url)
            for product_url in product_url_list:
                title, url, text = self._yahoo_product(url=product_url)
                yahoo_mall_contents_result.append([title, url, text])
                del title, url, text

        elif re.match(self.product_fetch, self.target_url):
            title, url, text = self._yahoo_product(url=self.target_url)
            yahoo_mall_contents_result.append([title, url, text])
            del title, url, text
            
        return yahoo_mall_contents_result

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
        soup_url = soup.find('ul', {'class': 'Grid Mstart-12 Pt-14'}).findAll('a')
        for ele in soup_url:
            product_url = ele.attrs['href']
            if re.match(self.product_fetch, product_url):
                url_list.append(product_url)
        url_list = list(set(url_list))
        return url_list

    def _yahoo_product(self, url: str):
        """
        extract product information
        """
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.find('div', {'class':'top'}).span.text
        title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', title)
        text = '。'.join(i.text for i in soup.findAll('div', {'class': 'desc'}))
        text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', text)

        return title, url, text

if __name__ == "__main__":
    import sys
    URL = sys.argv[1]
    TEST = YahooMallCustomized(target_url=URL).execute()
    print(TEST.__next__())

"""
ruten customize crawl
"""
import re
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class RutenCustomized:
    """
    return type: generator
    """
    def __init__(self, target_url: str):
        """
        initial setting
        """
        self.pages = 2
        self.target_url = target_url

    def execute(self):
        """
        execute crawl with some limit condition
        """
        target_url = self.target_url
        
        if re.search('ruten.com', target_url):
            ruten_contents_result = []
            if re.search('www.ruten.com.tw', target_url):
                title, url, text = self._ruten_product(url=target_url)
                ruten_contents_result.append([title, url, text])
                del title, url, text

            elif re.search('find.ruten.com.tw', target_url):
                product_list = self._ruten_category(url=target_url, pages=self.pages)
                for product_id in product_list:
                    product_url = 'https://goods.ruten.com.tw/item/show?' + product_id
                    title, url, text = self._ruten_product(url=product_url)
                    ruten_contents_result.append([title, url, text])
                    del title, url, text
        return ruten_contents_result

    def _ruten_product(self, url: str):
        """
        extract product information
        """
        headers = {'User-Agent': '',}
        headers['User-Agent'] = UserAgent().random
        prodid = re.findall(r'[0-9]+', re.findall(r'show\?[0-9]+', url)[0])[0]
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        data = json.loads(soup.findAll('script', {'type':'application/ld+json'})[0].text)
        title = data['name']
        des_curl = re.findall(r'goods_comments.php\?id=.*?o=[0-9]{1,}', resp.text)[0]
        des_curl = re.sub('&amp;', '&', des_curl)
        des_curl = 'https://goods.ruten.com.tw/item/' + des_curl
        headers = {'User-Agent':'GoogleBot',
                   'Referer': 'https://goods.ruten.com.tw/item/show?{}'.format(prodid)}
        des_resp = requests.get(des_curl, headers=headers)
        des_soup = BeautifulSoup(des_resp.text, 'lxml')
        desc = ''.join(i.text for i in des_soup.findAll('p'))
        title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', title)
        desc = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', desc)
        return title, des_curl, desc

    def _ruten_category(self, url: str, pages: int):
        """
        if cateid not in url, then skip.
        """
        try:
            cateid = re.findall('[0-9]+', re.findall('c/[0-9]+|cateid=[0-9]+', url)[0])[0]
        except IndexError:
            return []
        api_headers = {'User-Agent':'GoogleBot'}
        product_list = []
        for page in range(1, pages+1):
            offset = 1 + 80*page
            url = 'https://rtapi.ruten.com.tw/api/search/v3/index.php/core/prod?cateid={}&sort=rnk%2Fdc&offset={}&limit=80&2653512&_callback=jsonpcb_CoreProd'.format(cateid, offset)
            res = requests.get(url, headers=api_headers)
            api_list = re.findall(r'\"Id\":\"[0-9]+\"', res.text)
            api_list = [re.findall('[0-9]+', pid)[0] for pid in api_list]
            product_list += api_list
        return product_list


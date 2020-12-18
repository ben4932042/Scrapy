from urllib.parse import unquote
import requests
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class RakutenCustomized:
    def __init__(self, target_url: str):

        self.target_url = unquote(target_url)
        self.domain_fetch = re.compile('www.rakuten.com.tw')
        self.category_fetch = re.compile('https://www.rakuten.com.tw/search/')
        self.product_fetch = re.compile('https://www.rakuten.com.tw/shop/')
        self.headers = {'User-Agent': ''}
        self.ua = UserAgent()
        
    def execute(self):
        if not re.search(self.domain_fetch, self.target_url):
            return 0
        rakuten_contents_result = []
        if re.search(self.category_fetch, self.target_url):
            product_url_list = self._rakuten_category(url=self.target_url)
            print(product_url_list)
            for product_url in product_url_list:
                title, url, text = self._rakuten_product(url=product_url)
                rakuten_contents_result.append([title, url, text])
                del title, url, text
        
        elif re.match(self.product_fetch, self.target_url):
            title, url, text = self._rakuten_product(url=self.target_url)
            rakuten_contents_result.append([title, url, text])
            del title, url, text
        
        return rakuten_contents_result

    def _rakuten_category(self, url: str):
        """
        return: product url list
        drop duplicate url
        """
        url_list = []
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        headers['path'] = '/graphql'
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        soup_url = str(soup.script)
        url_list = [i.split('@id:')[-1] for i in soup_url.split('#Product')][:-1]
        url_list = [i.split('\"@id\":\"')[-1] for i in url_list]
        try:
            url_list = url_list[:10]
        except:
            pass
        return url_list

    def _rakuten_product(self, url: str):
        """
        return: product desc
        """
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        headers['path'] = '/graphql'
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.title.text
        title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', title)
        text_json_list = soup\
                        .find('script',{'class': "js-react-on-rails-component", 'data-component-name': 'ProductInfoTabs'})\
                        .text.replace('\\','').split("\"shippingTab\"")[0]
        text_json_list = re.sub('u003cbru003en|u003cimg|u003e|u003|cu003c|span','',text_json_list)
        try:
            descriptionHtml = text_json_list.split('\"descriptionHtml\":\"')[1].split('\",\"')[0]
        except:
            descriptionHtml = '。'
        try:
            subDescriptionHtml = text_json_list.split('\"subDescriptionHtml\":\"')[1].split('\",\"')[0]
        except:
            subDescriptionHtml = '。'
        text = descriptionHtml + '。' + subDescriptionHtml
        text = re.sub('src+=+\"http+?s+://?[a-z|A-Z|0-9|\-|_|.|/]+\"|[style|id|class|alt]=\"?[a-z|A-Z|0-9|\-|_|.|/]\"','。',text)
        text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', text)
        
        return title, url, text


if __name__ == "__main__":
    import sys
    target_url = sys.argv[1]
    test = RakutenCustomized(target_url=target_url).execute()
    while True:
        try:
            print(test.__next__())
        except StopIteration:
            break

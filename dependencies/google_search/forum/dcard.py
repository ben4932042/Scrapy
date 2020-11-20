import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import unquote

class DcardCustomized:
    def __init__(self, target_url: str):
        """
        allow domain: www.dcard.tw, {forum}.dcard.tw
        """
        self.target_url = unquote(target_url)
        self.domain_fetch = re.compile('dcard.tw')
        self.category_fetch = re.compile('https://+[a-z|A-Z|0-9| ]+\.dcard\.tw/+(f|topics)+/.+')
        self.content_fetch = re.compile('https://+[a-z|A-Z|0-9| ]+\.dcard\.tw/f/+[a-z|A-Z|0-9| ]+/p/+[0-9]+')
        self.content_id_fetch = re.compile('/f/[a-z|A-Z|0-9| ]+/p/+[0-9]+')
        self.headers = {'User-Agent': ''}
        self.ua = UserAgent()
        
    def execute(self):
        if not re.search(self.domain_fetch, self.target_url):
            return 0
        dcard_contents_result = []
        if re.search(self.content_fetch, self.target_url):
            content_sub_url = re.search(self.content_id_fetch, self.target_url).group(0)
            content_id = re.search('[0-9]+',content_sub_url).group(0)
            title, url, text = self._dcard_content(content_id=content_id)
            dcard_contents_result.append([title, url, text])
            del title, url, text

        elif re.search(self.category_fetch, self.target_url):
            content_id_list = self._dcard_category(url=self.target_url)
            for content_id in content_id_list:
                title, url, text = self._dcard_content(content_id=content_id)
                dcard_contents_result.append([title, url, text])
                del title, url, text
        return dcard_contents_result

    def _dcard_category(self, url: str):
        """
        return: product url list
        drop duplicate url
        """
        content_id_list = []
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        res = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        for i in soup.body.find('div', {'role': 'main'}).findAll('a'):
            try:
                content_sub_url = i.attrs['href']
                if re.search(self.content_id_fetch, content_sub_url):
                    content_id = re.search('[0-9]+',content_sub_url).group(0)
                    content_id_list.append(content_id)
            except Exception:
                continue
                
        content_id_list = list(set(content_id_list))
        return content_id_list

    def _dcard_content(self, content_id: str):
        """
        input post/content id
        redirect to api url
        return: content title, desc
        """
        headers = self.headers
        headers['User-Agent'] = self.ua.random
        content_url = f'https://www.dcard.tw/service/api/v2/posts/{content_id}'
        res = requests.get(url=content_url, headers=headers)
        res_json = res.json()
        content_title = res_json['title']
        content_title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', content_title)
        content_text = res_json['content']
        content_text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', content_text)
        
        return content_title, content_url, content_text

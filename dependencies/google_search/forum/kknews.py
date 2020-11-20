import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def kknews_customized(target_url: str):
    if not re.search('https://kknews.cc/', target_url):
        return
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    res = requests.get(url=target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    try:
        content_title = soup.find('h1',{'class':'entry-title p-name'}).text
    except Exception:
        content_title = ''
    try:
        content_text = '。'.join(i.text for i in soup.find('div',{'class':'basic'}).findAll('p'))
    except:
        content_text = ''
        
    content_title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', content_title)
    content_text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', content_text)

    return [[content_title, target_url, content_text]]
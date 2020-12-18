"""
domain rule: http+[s]+//${username}.pixnet.net/blog/post/*
"""
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def pixnet_customized(target_url: str):
    """
    [Note]
        res.encoding is required
        return content_title, content_url, content_text
    """
    if not re.search(r'http+[s]+://+.+\.pixnet\.net/blog/post/[0-9]+.+', target_url):
        return
    
    proxy_ua = UserAgent()
    headers = {'User-Agent': proxy_ua.random}
    res = requests.get(url=target_url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'lxml')

    try:
        content_title = soup.title.text
    except Exception:
        content_title = ''
    try:
        content_text = soup.find('div', {'class': 'article-content-inner'}).text
    except Exception:
        content_text = ''

    content_title = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', content_title)
    content_text = re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', content_text)

    return [[content_title, target_url, content_text]]

if __name__ == "__main__":
    import sys
    target_url = sys.argv[1]
    print(pixnet_customized(target_url=target_url))

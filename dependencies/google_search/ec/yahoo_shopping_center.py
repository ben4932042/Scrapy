import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re


def yahoo_shopping_center_customized(search_word: str, target_url: str):
    
    if not re.search('tw.buy.yahoo.com', target_url):
        return 1
    
    pages = 2
    headers = {'User-Agent': ''}
    url_list = []
    ua = UserAgent()
    yahoo_shopping_center_contents_result = []
    
    for page in range(1,pages+1):
        headers['User-Agent'] = ua.firefox
        res = requests.get('https://tw.buy.yahoo.com/search/product?p={}A&pg={}'.format(search_word, page), headers=headers)
        soup = BeautifulSoup(res.text, 'lxml')
        soup_urls = soup.find('div',{'class': 'main'}).findAll('a')
        for raw_url in soup_urls:
            contents_url = raw_url.attrs['href']
            if re.search('tw.buy.yahoo.com', contents_url):
                url_list.append(contents_url)

    for url in url_list:
        try:
            headers['User-Agent'] = ua.random
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'lxml')
            title = re.sub(' ', '。', soup.title.text)
            des = '。'.join([i.text for i in soup.find('div','ProductFeatures__productFeatureWrapper___2vMZ7').ul.findAll('li')])
            detail = soup.find('div',{'class': 'ProductTag__wrapper___Y9p3j ProductItemPage__moduleWhiteCard___1HiL1'}).div.text
            text = re.sub(' |\n|\r|\t|,|‧', '。', des + '。' + detail)
            yahoo_shopping_center_contents_result.append([title, url, text])
            del title, url, text

        except AttributeError:
            continue
        except Exception as e:
            pass
    return yahoo_shopping_center_contents_result
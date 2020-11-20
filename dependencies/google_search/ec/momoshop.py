"""[summary]
    1. customize each page in target url.
"""
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def momo_customized(search_word: str, target_url: str):
    """
    return type: generator
    """
    if not re.search('momoshop.com.tw', target_url):
        return
    momo_contents_result = []
    keyword = search_word
    pages = 2
    headers = {
        'User-Agent':"",
        'Referer': 'https://www.google.com/',
        'Range': 'bytes=0-',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
    ua = UserAgent()
    headers['User-Agent'] = ua.firefox
    urls = []
    for page in range(1, pages):
        url = 'https://m.momoshop.com.tw/search.momo?_advFirst=N&_advCp=N&curPage={}&searchType=1&cateLevel=2&ent=k&searchKeyword={}&_advThreeHours=N&_isFuzzy=0&_imgSH=fourCardType'.format(page, keyword)
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'lxml')
            for item in soup.select('li.goodsItemLi > a'):
                urls.append('https://m.momoshop.com.tw'+item['href'])
        urls = list(set(urls))
        
    for url in urls:
        res = requests.get(url, headers=headers)
        title, link, cate, desc, specification, text = '', '', '' ,'' ,'', ''

        if resp.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            try:
                title = soup.find('meta',{'property':'og:title'})['content']
                title = re.sub('\r|\n|\t| ', '。',title)

                link = soup.find('meta',{'property':'og:url'})['content']

                cate = ''.join([i.text for i in soup.findAll('article',{'class':'pathArea'})])
                cate = re.sub('\xa0|>| ','',cate)
                cate = re.sub('\r|\n|\t| ', '。',cate)

                try:
                    desc = soup.find('div',{'class':'Area101'}).text
                    desc = re.sub('\r|\n|\t| ', '。', desc)
                except AttributeError:
                    desc = ''

                for i in soup.select('div.attributesArea > table > tr'):
                    try:
                        column = i.find('th').text
                        column = re.sub('\n|\r| ','',column)
                        value = ''.join([j.text for j in i.findAll('li')])
                        value = re.sub('\n|\r| ','',value)
                    except AttributeError:
                        column=''
                        value=''
                    specification += '。' + column + '。' + value + '。'

                result = cate + desc + specification

            except TypeError:
                continue
            except Exception as e:
                break

        momo_contents_result.append([title, link, result])
        del title, link, result
    return momo_contents_result
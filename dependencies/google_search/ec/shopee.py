import json
from json import JSONDecodeError
import re
import requests
from bs4 import BeautifulSoup

def shopee_customized(search_word: str, target_url: str):
    
    REJECT = True
    shopee_contents_result = []
    if re.search('shopee.tw', target_url):
        REJECT = False
    
    if re.search('shopee.com.tw', target_url):
        REJECT = False
    
    if re.search('shopee.com', target_url):
        REJECT = False
    
    if re.search('shopee.com.tw', target_url):
        REJECT = False
    
    if REJECT:
        raise Exception('Wrong Domain')
    
    n_page = 2
    shopee_headers = {'User-Agent': 'Googlebot'}
    for page in range(1, n_page):
        url = 'https://shopee.tw/search?keyword={keyword}&page={page}&sortBy=relevancy'.format(keyword=search_word,page=page)
        r = requests.get(url,headers=shopee_headers)
        soup = BeautifulSoup(r.text, 'lxml')
        all_items = soup.find_all("div", class_="col-xs-2-4 shopee-search-item-result__item")

        links = [ 'https://shopee.tw' + i.find('a').get('href') for i in all_items]        
        for link in links:
            try:
                r = requests.get(url=link, headers=shopee_headers)
                soup = BeautifulSoup(r.text, 'lxml')
                tmp = '{' + soup.head.text.split('}{')[-1]
                try:
                    result_json = json.loads(tmp)
                    title = result_json['name']
                    text = result_json['description']
                except JSONDecodeError:
                    try:
                        title = soup.title.text
                    except:
                        title = ''
                    try:
                        text = '。'.join(i.text for i in soup.findAll('span'))
                    except:
                        text = ''

                title = re.sub('\t|\n|\r|/| ','。',title)

                text = re.sub('\t|\n|\r|\\\\n|/| ','。',text)
                shopee_contents_result.append([title, link, text])
                del title, link, text
            except Exception as e:
                return e
                continue

    return shopee_contents_result
    
if __name__ == "__main__":
    import sys
    search_word = sys.argv[1]
    target_url = sys.argv[2]
    
    print(shopee_customized(search_word=search_word, target_url=target_url))

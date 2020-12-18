import time
import random
import pandas as pd
import datetime
import os
import sys
import logging
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv,find_dotenv
from fake_useragent import UserAgent
from dependencies import mkdir_force
from retry import retry
load_dotenv(find_dotenv())

class GoogleSearch:
    def __init__(self, search_word: str, PROXY=True):
        """
        initial setting
        """
        self.PROXY = PROXY
        ua = UserAgent()
        self.url = 'https://www.google.com/search?q={}&gws_rd=ssl'.format(search_word)
        self.url_next = 'https://www.google.com/search?q={}&gws_rd=ssl&start=10'.format(search_word)
        self.headers = {
                        'User-Agent': ua.random,
                        'Referer': 'https://www.google.com/',
                        'Range': 'bytes=0-',
                        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        }

    def get_url(self):
        """
        get two page in google search
        """
        google_soup_first_page = self._get_soup(self.url)
        google_soup_next_page = self._get_soup(self.url_next)
        html_raw_first_page = google_soup_first_page.find('div',{'id':'search'})
        html_raw_next_page = google_soup_next_page.find('div',{'id':'search'})
        search_url_list_first_page = [
                                   content_html.a.attrs['href'] 
                                   for content_html 
                                   in html_raw_first_page.findAll('div', {'class': 'g'})
                                  ]
        search_url_list_next_page = [
                                   content_html.a.attrs['href'] 
                                   for content_html 
                                   in html_raw_next_page.findAll('div', {'class': 'g'})
                                  ]
        search_url_list = search_url_list_first_page + search_url_list_next_page
        search_url_list = list(set(search_url_list))
        
        return search_url_list
    
    def get_recommend(self):
        """
        get recommend keyword at the first page in google search
        """
        google_soup = self._get_soup(self.url)
        recommend_list = [
            recommend_html.text 
            for recommend_html 
            in google_soup.find('div', {'class': 'card-section'}).findAll('a')
            ]
        recommend_list = list(set(recommend_list))
        return recommend_list
    
    def _get_soup(self, url: str):
        """
        return raw html
        """
        if self.PROXY:
            proxy = self._get_proxy().get("proxy")
            response = requests.get(
                        url = url,
                        headers=self.headers,
                        proxies={"http": "http://{}".format(proxy)},
                        )
        else:
            response = requests.get(url = url, headers=self.headers)
        if response.status_code != 200:
            self._delete_proxy(proxy)
            raise NameError('Too fast ip: {}'.format(proxy))
        soup = BeautifulSoup(response.text,'lxml')
        return soup
    
    def _get_proxy(self):
        """
        Dependencies: proxy_pool docker images
        Only used in local
        summary: get proxy IP
        """
        return requests.get("http://127.0.0.1:5010/get/").json()

    def _delete_proxy(self, proxy):
        """
        delete dead proxy IP
        """
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))
        
@retry(tries=-1, delay=5, backoff=0, jitter=(1,15))
def main(search_data_list: list, execute_date: str):
    RESULT_ARRAY = []
    search_word_index = search_data_list[0]
    search_data_list = search_data_list[1:]
    search_word = search_data_list[3]
    search_word_url_list = GoogleSearch(search_data_list[3]).get_url()
    search_word_list = search_data_list + search_word_url_list
    RESULT_ARRAY.append(search_word_list)
    del search_word_list, search_word_url_list
    
    try:
        recommend_array = [
                    [search_data_list[0], search_data_list[1],search_data_list[2], recommend_word] 
                    for recommend_word 
                    in GoogleSearch(search_data_list[3]).get_recommend()
                    ]


        for recommend_list in recommend_array:
            recommend_word_url_list = GoogleSearch(recommend_list[3]).get_url()
            recommend_word_list = recommend_list + recommend_word_url_list
            RESULT_ARRAY.append(recommend_word_list)
            del recommend_word_list, recommend_word_url_list
        del recommend_array

    except AttributeError:
        pass

    pd.DataFrame(RESULT_ARRAY).to_csv(
                            f"{GOOGLE_LOCAL_PATH}/url/202011/{TAG_NAME}/{search_word_index}.csv",
                            index=None,
                            )
    finally:
        del RESULT_ARRAY
    else:
        print('{}: {}'.format(search_word_index, search_word))
 
if __name__ == "__main__":
    logging.basicConfig()
    GOOGLE_LOACL_PATH = os.getenv('GOOGLE_LOCAL_PATH')
    TAG_NAME = sys.argv[1]
    print(TAG_NAME)
    print('='*10)
    MONTH = datetime.datetime.now().strftime('%Y%m')
    CSV_PATH = f'{GOOGLE_LOCAL_PATH}/raw/{MONTH}/{TAG_NAME}.csv'
    mkdir_force(f'{GOOGLE_LOCAL_PATH}/url/{MONTH}/{TAG_NAME}'
    df = pd.read_csv(CSV_PATH)
    df = df[['第一層','第二層','第三層']]
    df = df.reset_index(drop=False)
    df['search_word'] =df['第三層'] + '+推薦'
    
    search_word_array = df.to_numpy().tolist()
    for search_data_list in search_word_array:
        main(search_data_list=search_data_list,execute_date=MONTH)
    

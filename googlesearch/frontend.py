"""
This jobs will handle googlesearch forend-part.
"""
import time
import random
import os
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
#from dotenv import load_dotenv,find_dotenv
from fake_useragent import UserAgent
#load_env(find_dotenv())

ua = UserAgent()
i=int(sys.argv[1])
df_raw = pd.read_csv(os.getenv("SEARCHWORDLIST_LOACL_PATH")+'/raw.csv')
index_start = i - 2
raws_to_df = [
        [df_raw.iloc[x][0],df_raw.iloc[x][1],df_raw.iloc[x][2],df_raw.iloc[x][2]+'+推薦']
        for x in range(index_start,len(df_raw))
    ]
for raw_data in raws_to_df:
    try:
        time.sleep(random.randint(1,5))
        Matrix = []
        search_data_list = raw_data.copy()
        headers = {
            'User-Agent':"",
            'Referer': 'https://www.google.com/',
            'Range': 'bytes=0-',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        user_agent = ua.firefox
        headers = {'User-Agent': user_agent}
        URL = 'https://www.google.com/search?q={}&gws_rd=ssl'.format(search_data_list[3])
        response = requests.get(url = URL,headers=headers)
        if str(response) == '<Response [429]>':
            raise NameError('Too fast')
        soup = BeautifulSoup(response.text,'lxml')
        html_raw = soup.find('div',{'id':'rso'})
        all_article_raw = soup.findAll('div',{'class':"r"})
        for each_article in all_article_raw:
            each_title = each_article.h3.text
            each_url = each_article.a["href"]
            search_data_list = search_data_list + [each_title,each_url]
        URL_NEXT = 'https://www.google.com/search?q={}&gws_rd=ssl&start=10'\
                                                        .format(search_data_list[3])
        time.sleep(random.randint(5,10))
        user_agent = ua.firefox
        headers = {'User-Agent': user_agent}
        response = requests.get(url = URL_NEXT, headers=headers)
        if str(response) == '<Response [429]>':
            raise NameError('Too fast')
        soup = BeautifulSoup(response.text,'lxml')
        html_raw = soup.find('div',{'id':'rso'})
        all_article_raw = soup.findAll('div',{'class':"r"})
        for each_article in all_article_raw:
            each_title = each_article.h3.text
            each_url = each_article.a["href"]
            search_data_list = search_data_list + [each_title,each_url]
        Matrix.append(search_data_list)
        time.sleep(1)
        recommand = soup.find('div',{'class':"card-section"})
        if recommand:
            for r in recommand.findAll('p'):
                time.sleep(1)
                command_word = r.text
                search_data_list = a.copy()
                search_data_list[3] = command_word
                URL = 'https://www.google.com/search?q={}&gws_rd=ssl'.format(search_data_list[3])
                response = requests.get(url = URL, headers=headers)
                user_agent = ua.firefox
                headers = {'User-Agent': user_agent}
                if str(response) == '<Response [429]>':
                    raise NameError('Too fast')
                soup = BeautifulSoup(response.text,'lxml')
                html_raw = soup.find('div',{'id':'rso'})
                all_article_raw = soup.findAll('div',{'class':"r"})
                for each_article in all_article_raw:
                    each_title = each_article.h3.text
                    each_url = each_article.a["href"]
                    search_data_list = search_data_list + [each_title,each_url]
                URL_NEXT = 'https://www.google.com/search?q={}&gws_rd=ssl&start=10'\
                                                                    .format(search_data_list[3])
                time.sleep(random.randint(1,5))
                user_agent = ua.firefox
                headers = {'User-Agent': user_agent}
                response = requests.get(url = URL_NEXT,headers=headers)
                if str(response) == '<Response [429]>':
                    raise NameError('Too fast')
                soup = BeautifulSoup(response.text,'lxml')
                html_raw = soup.find('div',{'id':'rso'})
                all_article_raw = soup.findAll('div',{'class':"r"})
                for each_article in all_article_raw:
                    each_title = each_article.h3.text
                    each_url = each_article.a["href"]
                    search_data_list = search_data_list + [each_title,each_url]

                Matrix.append(search_data_list)

        pd.DataFrame(Matrix).to_csv(
                            os.getenv("SEARCHWORD_LOCAL_PATH")+'/data/{}.csv'.format(str(i)),
                            index=None,
                            )
        i +=1
    except NameError as error_:
        os.stderr('{}-{}'.format(i,error_))
        break

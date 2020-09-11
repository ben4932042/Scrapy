import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import os
import sys
from dotenv import load_dotenv,find_dotenv

load_env(find_dotenv())

i=int(sys.argv[1])

headerlist = [    
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991",
"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 OPR/42.0.2393.94",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.39",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
"Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
]

df_raw = pd.read_csv(os.getenv("SEARCHWORDLIST_LOACL_PATH")+'/raw.csv')

index_start = i - 2
A = [
        [df_raw.iloc[x][0],df_raw.iloc[x][1],df_raw.iloc[x][2],df_raw.iloc[x][2]+'+推薦']
        for x in range(index_start,len(df_raw))
    ]


for a in A:
    try:
        os.stdout(a[3])
        time.sleep(random.randint(1,5))
        raw_data = a
        Matrix = []
        search_data_list = raw_data.copy()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0',
            'Referer': 'https://www.google.com/',
            'Range': 'bytes=0-',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        user_agent = random.choice(headerlist)
        headers = {'User-Agent': user_agent}
        url = 'https://www.google.com/search?q={}&gws_rd=ssl'.format(search_data_list[3])
        response = requests.get(url = url,headers=headers)
        if str(response) == '<Response [429]>':
            raise NameError('Too fast')
        soup = BeautifulSoup(response.text,'lxml')
        html_raw = soup.find('div',{'id':'rso'})
        all_article_raw = soup.findAll('div',{'class':"r"})
        for each_article in all_article_raw:
            each_title = each_article.h3.text
            each_url = each_article.a["href"]
            search_data_list = search_data_list + [each_title,each_url]
        url_next = 'https://www.google.com/search?q={}&gws_rd=ssl&start=10'.format(search_data_list[3])
        #time.sleep(random.randint(5,10))
        user_agent = random.choice(headerlist)
        headers = {'User-Agent': user_agent}
        response = requests.get(url = url_next,headers=headers)
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
                url = 'https://www.google.com/search?q={}&gws_rd=ssl'.format(search_data_list[3])
                response = requests.get(url = url,headers=headers)
                user_agent = random.choice(headerlist)
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
                url_next = 'https://www.google.com/search?q={}&gws_rd=ssl&start=10'.format(search_data_list[3])
                #time.sleep(random.randint(5,10))
                user_agent = random.choice(headerlist)
                headers = {'User-Agent': user_agent}
                response = requests.get(url = url_next,headers=headers)
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
    except NameError as n:
        os.stderr('{}-{}'.format(i,n))
        break
    except Exception as e:
        os.stderr('{}-{}'.format(i,n)
        break

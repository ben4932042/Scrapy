import os
from ..items import GoogleSearchItem
import requests
import hashlib
from bs4 import BeautifulSoup
import scrapy
from dotenv import load_dotenv,find_dotenv
import requests
import datetime
import gzip
import csv
import time
import random
import pandas as pd
import numpy as np
import glob
import re
import logging
from retry import retry
from fake_useragent import UserAgent
from dependencies.customization_google_search import Customization
from dependencies import mkdir_force
load_dotenv(find_dotenv())


def judge_skip_word(target:str,skip_word_list:list):
    tmp_list = [target.count(skip) for skip in skip_word_list]
    judge_count = 0
    for t in tmp_list:
        judge_count += t
    return judge_count

def get_hash256(url: str):
    s = hashlib.sha256()
    s.update(url.encode('utf-8'))
    URLID = s.hexdigest()
    return URLID

def replace_word(word: str):
    return re.sub(' |\t|\r|\n|\u3000|\xa0|<br>|<br/>', '。', word)

class GooglesearchSpider(scrapy.Spider):
    name = 'googlesearch_each'
    custom_settings = {
        #"CONCURRENT_REQUESTS" : 10,
        #"CONCURRENT_REQUESTS_PER_DOMAIN" : 5,
        "DOWNLOAD_FAIL_ON_DATALOSS" : False,
        }
    download_delay = 6
    category_tag = 'tobaccoAndAlcohol'
    start_urls = ['https://www.google.com/']
    skip_url_list = ['www.youtube.com','www.bilibili.com']
    skip_word_list = ['焦點新聞','相關搜尋','搜尋結果','建議搜尋篩選器','影片']
    customize_domain = [
                'shopee.tw',
                'feebee.com.tw',
                'return.com.tw',
                'www.dcard.tw',
                'momoshop.com.tw',
                'my-best.com',
                'biggo.com.tw',
                'blog.xuite.net',
                'www.pcone.com.tw',
                'pchome.com.tw',
                'pcstore.com.tw',
                'world.taobao.com',
                'kknews.cc',
                'www.buy123.com.tw',
                'www.rakuten.com.tw',
                'ruten.com.tw',
                'tw.buy.yahoo.com',
                'tw.bid.yahoo.com',
                'tw.mall.yahoo.com',
                'pixnet.net',
                ]

    def start_requests(self):
        ua = UserAgent()
        GOOGLE_LOCAL_PATH = os.getenv("GOOGLE_LOCAL_PATH")
        MONTH = datetime.datetime.now().strftime('%Y%m')
        google_search_url_path = '{google_search}/url/{month}/{category}'\
                                                                    .format(
                                                                            google_search=GOOGLE_LOCAL_PATH,
                                                                            month = MONTH,
                                                                            category = {},
                                                                            )

        
        google_search_url_path_each_tag = google_search_url_path.format(self.category_tag)
        file_name_list = glob.glob('{}/*.csv'.format(google_search_url_path_each_tag))
        for file_name in file_name_list:
            search_word_index = int(file_name.split('/')[-1][:-4])
            self.logger.info("start to crawl index {}".format(search_word_index))
            tmp_df = pd.read_csv(file_name)
            contents_array = tmp_df.to_numpy().tolist()
            del df_tmp
            content_list_list = []
            for content_list in contents_array:
                content_tmp_list = [
                    [content_list[0], content_list[1], content_list[2], content_list[3], content_list[i]]
                    for i in range(4,len(content_list))
                    ]
                content_list_list += content_tmp_list
            del contents_array
            for content_list in content_list_list:
                content_search_word = content_list[3]
                content_url = content_list[4]
                
                if isinstance(content_url, float):
                    continue  # content_url == nan
                elif not re.search('http://|https://', content_url):
                    continue
                elif judge_skip_word(target=content_url, skip_word_list=self.skip_url_list) > 0:
                    continue
                elif judge_skip_word(target=content_search_word, skip_word_list =self.skip_word_list) > 0:
                    continue
                else:
                    search_url = content_list[4]
                    category_tag_name = self.category_tag
                    ua = UserAgent()
                    headers = {'user-agent': ua.random}
                    try:
                        domain = re.search("//[a-z|A-Z|0-9|\.]+/", search_url).group().split('/')[2]
                    except Exception:
                        domain = ''
                        
                    if domain in self.customize_domain:
                        del domain
                        yield scrapy.Request(
                                        search_url, 
                                        meta={'attribute': content_list},
                                        callback=self.customized_parse,
                                        dont_filter=True,
                                        headers=headers,
                                        )
                            
                    else:
                        del domain
                        yield scrapy.Request(
                                        search_url, 
                                        meta={'attribute': content_list},
                                        callback=self.extract_parse,
                                        dont_filter=True,
                                        headers=headers,
                                        )
            os.remove(file_name)    
    
    def extract_parse(self, response):
        item = GoogleSearchItem()
        target_list = response.meta['attribute']  
        item['source'] = 'googlesearch'
        search_word = target_list[3]
        search_url = target_list[4]
        item['searchWord'] = search_word
        item['tag_layer1'] = target_list[0]
        item['tag_layer2'] = target_list[1]         
        item['tag_layer3'] = target_list[2]
        save_file_name = '{}_extract.tsv.gz'.format(self.category_tag)
        self.logger.info(search_word)

        html_str = response.text
        cus = Customization(
                        target_word=search_word,
                        target_url=search_url,
                        html_str=html_str,
                        )
        contents_list_list = cus.execute()

        try:
            if len(contents_list_list) == 0:
                return None
        except TypeError:
            return None

        for contents_list in contents_list_list:
            content_title = contents_list[0]
            content_url = contents_list[1]
            content_text = contents_list[2]
            content_id = get_hash256(content_url)
            content_title = replace_word(content_title)
            content_text = replace_word(content_text)
            
            item['title'] = content_title
            item['text'] = content_text
            item['url'] = content_url
            item['_id'] = content_id
            item['createtime'] = datetime.datetime.now().strftime("%Y%m%d")

            yield item
            
    def customized_parse(self, response):
        item = GoogleSearchItem()
        target_list = response.meta['attribute']  
        item['source'] = 'googlesearch'
        search_word = target_list[3]
        search_url = target_list[4]
        item['searchWord'] = search_word
        item['tag_layer1'] = target_list[0]
        item['tag_layer2'] = target_list[1]         
        item['tag_layer3'] = target_list[2]
        save_file_name = '{}_customized.tsv.gz'.format(self.category_tag)
        self.logger.info(search_word)

        html_str = response.text
        cus = Customization(
                        target_word=search_word,
                        target_url=search_url,
                        html_str=html_str,
                        )
        contents_list_list = cus.execute()

        try:
            if len(contents_list_list) == 0:
                return None
        except TypeError:
            self.logger.warning('get skip url')
            return None

        for contents_list in contents_list_list:
            content_title = contents_list[0]
            content_url = contents_list[1]
            content_text = contents_list[2]
            content_id = get_hash256(content_url)
            content_title = replace_word(content_title)
            content_text = replace_word(content_text)
            
            item['title'] = content_title
            item['text'] = content_text
            item['url'] = content_url
            item['_id'] = content_id
            item['createtime'] = datetime.datetime.now().strftime("%Y%m%d")

            yield item


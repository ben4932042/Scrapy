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
from retry import retry
from fake_useragent import UserAgent
from dependencies.customization_google_search import Customization
load_dotenv(find_dotenv())

def mkdir_force(destination_path: str):
    if not os.path.exists(destination_path):
        os.makedirs(destination_path, exist_ok = True)

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

@retry(delay=3)
def save_tsv_gz_file_by_appending_method(path: str, file_name: str, data_filed_header: list, data_filed_dict: dict):

    with gzip.open(path + file_name, "at", newline="") as filetype:
        wcsv = csv.DictWriter(
            filetype,
            data_filed_header,
            delimiter = "\t",
        )
        wcsv.writerow(data_filed_dict)


class GooglesearchSpider(scrapy.Spider):
    name = 'googlesearch_each'
    custom_settings = {
        "CONCURRENT_REQUESTS" : 10,
        "CONCURRENT_REQUESTS_PER_DOMAIN" : 5,
        "DOWNLOAD_FAIL_ON_DATALOSS" : False,
        }
    download_delay = 3
    category_tag = '3C'
    start_urls = ['https://www.google.com/']
    skip_url_list = ['www.youtube.com','www.bilibili.com']
    skip_word_list = []
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
                'www.return.com.tw',
                'tw.buy.yahoo.com',
                'tw.bid.yahoo.com',
                'tw.mall.yahoo.com',
                'pixnet.net',
                ]

    data_filed = [
            "_id",
            'source',
            'tag_layer1',
            'tag_layer2',
            'tag_layer3',
            'searchWord',
            "url",
            "title",
            "text",
            "createtime",
            ]

    local_path = os.getenv("GOOGLE_LOCAL_PATH")+'/result/{}/'.format(datetime.datetime.now().strftime('%Y%m'))
    mkdir_force(local_path)

    def parse(self, response):

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
            df = pd.read_csv(file_name)
            contents_array = df.to_numpy().tolist()
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
                    headers = {'user-agent': ua.random}
                    yield scrapy.Request(
                                        content_url, 
                                        meta={'attribute': content_list},
                                        callback=self.each_parse,
                                        dont_filter=True,
                                        headers=headers,
                                        )                    

    def each_parse(self, response):
        target_list = response.meta['attribute']  
        search_url = target_list[4]
        category_tag_name = self.category_tag

        ua = UserAgent()
        headers = {'user-agent': ua.random}

        try:
            domain = re.search("//[a-z|A-Z|0-9|\.|-]+/", search_url).group().split('/')[2]
        except AttributeError:
            del domain
            yield scrapy.Request(
                            search_url, 
                            meta={'attribute': target_list},
                            callback=self.extract_parse,
                            dont_filter=True,
                            headers=headers,
                            )
            
        if domain in self.customize_domain:
            del domain
            yield scrapy.Request(
                            search_url, 
                            meta={'attribute': target_list},
                            callback=self.customized_parse,
                            dont_filter=True,
                            headers=headers,
                            )
                
        else:
            del domain
            yield scrapy.Request(
                            search_url, 
                            meta={'attribute': target_list},
                            callback=self.extract_parse,
                            dont_filter=True,
                            headers=headers,
                            )

    def extract_parse(self, response):
        """
        run AI Lab module
        """
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
        
        html_str = response.text
        cus = Customization(
                        target_word=search_word,
                        target_url=search_url,
                        html_str=html_str,
                        )
        contents_list_list = cus.execute()
        try:
            if len(contents_list_list) == 0:
                return
        except TypeError:
            return

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

            save_tsv_gz_file_by_appending_method(self.local_path, save_file_name, self.data_filed , item)
            
    def customized_parse(self, response):
        """
        run DE module
        """
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
        
        html_str = response.text
        cus = Customization(
                        target_word=search_word,
                        target_url=search_url,
                        html_str=html_str,
                        )
        contents_list_list = cus.execute()
        try:
            if len(contents_list_list) == 0:
                yield scrapy.Request(
                        search_url, 
                        meta={'attribute': target_list},
                        callback=self.extract_parse,
                        dont_filter=True,
                        headers=headers,
                        )

        except TypeError:
            raise Exception('get skip url')

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
            
            save_tsv_gz_file_by_appending_method(self.local_path, save_file_name, self.data_filed , item)

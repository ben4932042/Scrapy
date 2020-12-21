"""
Google Search crawler
"""
import os
import datetime
import glob
import re
import pandas as pd
import scrapy
from dotenv import load_dotenv, find_dotenv
from fake_useragent import UserAgent
from dependencies.customization_google_search import Customization
from dependencies import judge_skip_word
from dependencies import replace_word
from dependencies import get_hash256
from ..items import GoogleSearchItem
load_dotenv(find_dotenv())

class GooglesearchSpider(scrapy.Spider): #pylint: disable=abstract-method
    """
    main class function
    """
    name = 'googlesearch_each'
    start_urls = ['https://www.google.com/']
    skip_url_list = ['www.youtube.com', 'www.bilibili.com']
    skip_word_list = ['焦點新聞', '相關搜尋', '搜尋結果', '建議搜尋篩選器', '影片']
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
    def __init__(self, category_tag=None): #pylint: disable=super-init-not-called
        """
        initial setting
        """
        if category_tag is None:
            raise scrapy.exceptions.CloseSpider("Lost parameter: category_tag")
        self.category_tag = category_tag
    def start_requests(self): #pylint: disable=too-many-locals
        """
        Allocate url into each parse
        """
        local_path = os.getenv("GOOGLE_LOCAL_PATH")
        execute_month = datetime.datetime.now().strftime('%Y%m')
        google_search_url_path_each_tag = f'{local_path}/url/{execute_month}/{self.category_tag}'
        file_name_list = glob.glob(f'{google_search_url_path_each_tag}/*.csv')
        if len(file_name_list) == 0:
            raise scrapy.exceptions.CloseSpider("No raw url file need to crawl")
        for file_name in file_name_list:
            search_word_index = int(file_name.split('/')[-1][:-4])
            self.logger.info(f"start to crawl index {search_word_index}")
            tmp_df = pd.read_csv(file_name)
            contents_array = tmp_df.to_numpy().tolist()
            del tmp_df
            content_list_list = []
            for content_list in contents_array:
                content_tmp_list = [
                    [content_list[0],
                     content_list[1],
                     content_list[2],
                     content_list[3],
                     content_list[i]]
                    for i in range(4, len(content_list))
                    ]
                content_list_list += content_tmp_list
            del contents_array
            for content_list in content_list_list:
                content_search_word = content_list[3]
                content_url = content_list[4]

                if isinstance(content_url, float): #pylint: disable=no-else-continue
                    continue  # content_url == nan
                elif not re.search('http://|https://', content_url):
                    continue
                elif judge_skip_word(
                        target=content_url, skip_word_list=self.skip_url_list) > 0:
                    continue
                elif judge_skip_word(
                        target=content_search_word, skip_word_list=self.skip_word_list) > 0:
                    continue
                else:
                    search_url = content_list[4]
                    user_agent = UserAgent()
                    headers = {'user-agent': user_agent.random}
                    try:
                        # pylint: disable=anomalous-backslash-in-string
                        domain = re.search("//[a-z|A-Z|0-9|\.]+/", search_url).group().split('/')[2]
                    except Exception: #pylint: disable=broad-except
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

    def extract_parse(self, response): #pylint: disable=inconsistent-return-statements
        """
        crawl ec
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

    def customized_parse(self, response): #pylint: disable=inconsistent-return-statements
        """
        crawl forum
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

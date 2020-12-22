import os
import csv
import gzip
import pymongo
import re
import sys
from dependencies import save_tsv_gz_file_by_appending_method
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def execute(url: str):
    domain = re.search("//[a-z|A-Z|0-9|\.|-]+/", url).group().split('/')[2]
    if fetch_domain(domain=domain):
        return True
    else:
        return False

def fetch_domain(domain: str):
    for customize in customize_domain:
        if re.findall(customize, domain):
            return 1
    return 0
if __name__ == "__main__":

    file_name = sys.argv[1]
    client = pymongo.MongoClient(os.getenv("MONGO_HOST"))
    db = client[os.getenv("MONGO_COLLECTION")]
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


    data_filed_header = ['_id', 'source', 'searchWord', 'tag_layer1', 'tag_layer2', 'tag_layer3', 'title', 'text', 'url', 'createtime']
    for data_dict in db['google_search'].find():
        try:
            if execute(data_dict['url']):
                save_tsv_gz_file_by_appending_method(
                    './',
                    f'{file_name}_custimized.tsv.gz',
                    data_filed_header=data_filed_header,
                    data_filed_dict=data_dict,
                )
            else:
                save_tsv_gz_file_by_appending_method(
                    './',
                    f'{file_name}_extract.tsv.gz',
                    data_filed_header=data_filed_header,
                    data_filed_dict=data_dict,
                )
        except AttributeError:
            save_tsv_gz_file_by_appending_method(
                './',
                f'{file_name}_extract.tsv.gz',
                data_filed_header=data_filed_header,
                data_filed_dict=data_dict,
            )
    client.close()

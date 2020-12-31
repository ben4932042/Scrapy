import os
from dotenv import load_dotenv, find_dotenv
import pymongo
import redis
load_dotenv(find_dotenv())

class GoogleSearchMongoPipeline(object):

    def open_spider(self, spider):
        db_name = os.getenv("MONGO_COLLECTION")
        self.db_client = pymongo.MongoClient(os.getenv("MONGO_HOST"))
        self.db = self.db_client[db_name]

    def process_item(self, item, spider):
        self.insert_article(item)
        return item

    def insert_article(self, item):
        item = dict(item)
        table_name = item['source']
        if not table_name == '':
            self.db[table_name].insert_one(item)

    def close_spider(self, spider):
        self.db_client.close()

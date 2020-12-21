import scrapy

class GoogleSearchItem(scrapy.Item):
    _id = scrapy.Field()    
    source = scrapy.Field()
    searchWord = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    createtime = scrapy.Field()

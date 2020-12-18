import scrapy

class GoogleSearchItem(scrapy.Item):
    _id = scrapy.Field()    
    source = scrapy.Field()
    tag_layer1 = scrapy.Field()
    tag_layer2 = scrapy.Field()
    tag_layer3 = scrapy.Field()
    searchWord = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    createtime = scrapy.Field()

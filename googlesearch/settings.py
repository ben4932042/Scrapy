BOT_NAME = 'googlesearch'

SPIDER_MODULES = ['googlesearch.spiders']
NEWSPIDER_MODULE = 'googlesearch.spiders'

RETRY_ENABLED = False
DOWNLOAD_TIMEOUT = 5

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

#LOG
LOG_LEVEL="DEBUG"
LOG_SHORT_NAMES=False
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 10
CONCURRENT_REQUESTS_PER_IP = 10

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent":"",
        }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'external_scrapy.middlewares.ExternalScrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'googlesearch.middlewares.GooglesearchScrapyDownloaderMiddleware': 543,
}

RETRY_HTTP_CODES = [429]

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
'googlesearch.pipelines.GetquotesPipeline': 400,
}



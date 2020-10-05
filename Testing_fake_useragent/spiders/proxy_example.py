"""
scrapy the free proxy
"""
import json
import scrapy
from bs4 import BeautifulSoup


class ProxyExampleSpider(scrapy.Spider):
    """Proxy Generator"""
    name = 'proxy_example'
    allowed_domains = ['www.us-proxy.org']
    start_urls = ['http://www.us-proxy.org/']

    def parse(self, response):
        """main function"""
        soup = BeautifulSoup(response.text, 'lxml')
        trs = soup.select("#proxylisttable tr")
        for tr_ in trs:
            tds = tr_.select("td")
            if len(tds) > 6:
                ip_ = tds[0].text
                port = tds[1].text
                if_scheme = tds[6].text
                if if_scheme == 'yes':
                    scheme = 'https'
                else: scheme = 'http'
                proxy = "%s://%s:%s"%(scheme, ip_, port)

                meta = {
                    'port': port,
                    'proxy': proxy,
                    'dont_retry': True,
                    'download_timeout': 3,
                    '_proxy_scheme': scheme,
                    '_proxy_ip': ip_
                        }

                yield scrapy.Request(
                            'https://httpbin.org/ip',
                            callback=self.proxy_check_available,
                            meta=meta,
                            dont_filter=True,
                            )

    def proxy_check_available(self, response):
        """ check proxy functionable"""
        proxy_ip = response.meta['_proxy_ip']
        if proxy_ip == json.loads(response.text)['origin']:
            yield {
                'scheme': response.meta['_proxy_scheme'],
                'proxy': response.meta['proxy'],
                'port': response.meta['port']
            }

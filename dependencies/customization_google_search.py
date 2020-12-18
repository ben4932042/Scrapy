import re
import requests
from bs4 import BeautifulSoup
from dependencies.google_search.ec.buy123 import Buy123Customized
from dependencies.google_search.ec.momoshop import momo_customized
from dependencies.google_search.ec.pchome import pchome_customized
from dependencies.google_search.ec.pcone import PconeCustomized
from dependencies.google_search.ec.rakuten import RakutenCustomized
from dependencies.google_search.ec.ruten import RutenCustomized
from dependencies.google_search.ec.shopee import shopee_customized
from dependencies.google_search.ec.taobao import TaobaoCustomized
from dependencies.google_search.ec.yahoo_mall import YahooMallCustomized
from dependencies.google_search.ec.yahoo_sale import YahooSaleCustomized
from dependencies.google_search.ec.yahoo_shopping_center import yahoo_shopping_center_customized
from dependencies.google_search.forum.dcard import DcardCustomized
from dependencies.google_search.forum.kknews import kknews_customized
from dependencies.google_search.forum.pixnet import pixnet_customized
from dependencies.py_utils.utils.ai_utils import extractTextByDensity

class Customization():
    """
    return url body
    content_title, content_url, content_text
    """
    def __init__(self, target_word: str, target_url: str, html_str: str):
        self.url = target_url
        self.word = target_word.split('+推薦')[0]
        self.html_str = html_str
        self.customize_domain = [
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
        
    def execute(self):
        domain = re.search("//[a-z|A-Z|0-9|\.]+/", self.url).group().split('/')[2]
        if self._fetch_domain(domain=domain):
            return self._website_customized()
        else:
            return self._extract_customized()
        
    def _fetch_domain(self, domain: str):
        for customize in self.customize_domain:
            if re.findall(customize, domain):
                return 1
        return 0
    
    def _website_customized(self):
        if 'shopee.tw' in self.url:
            shopee_contents = shopee_customized(search_word=self.word, target_url=self.url)
            return shopee_contents
        elif 'return.com.tw' in self.url:
            ruten_contents = RutenCustomized(target_url=self.url).execute()
            return ruten_contents       
        elif 'momoshop.com.tw' in self.url:
            momo_contents = momo_customized(search_word=self.word, target_url=self.url)
            return momo_contents
        elif 'www.pcone.com.tw' in self.url:
            pcone_contents = PconeCustomized(target_url=self.url).execute()
            return pcone_contents
        elif 'pchome.com.tw' in self.url:
            pchome_contents = pchome_customized(search_word=self.word, target_url=self.url)
            return pchome_contents
        elif 'pcstore.com.tw' in self.url:
            pcstore_contents = pchome_customized(search_word=self.word, target_url=self.url)
            return pcstore_contents 
        elif 'world.taobao.com' in self.url:
            taobao_contents = TaobaoCustomized(target_url=self.url).execute()
            return taobao_contents
        elif 'buy123.com.tw' in self.url:
            buy123_contents = Buy123Customized(target_url=self.url).execute()
            return buy123_contents
        elif 'www.rakuten.com.tw' in self.url:
            rakuten_contents = RakutenCustomized(target_url=self.url).execute()
            return rakuten_contents
        elif 'www.return.com.tw' in self.url:
            ruten_contents = RutenCustomized(target_url=self.url).execute()
            return ruten_contents
        elif 'tw.buy.yahoo.com' in self.url:
            yahoo_shopping_center_contents = yahoo_shopping_center_customized(
                                                                    search_word=self.word,
                                                                    target_url=self.url,
                                                                    )
            return yahoo_shopping_center_contents
        elif 'tw.bid.yahoo.com' in self.url:
            yahoo_sale_contents = YahooSaleCustomized(target_url=self.url).execute()
            return yahoo_sale_contents
        elif 'tw.mall.yahoo.com' in self.url:
            yahoo_mall_contents = YahooMallCustomized(target_url=self.url).execute()
            return yahoo_mall_contents
        
        elif 'feebee.com.tw' in self.url:
            pass
        elif 'my-best.com' in self.url:
            pass             
        elif 'biggo.com.tw' in self.url:
            pass
        
        elif 'kknews.cc' in self.url:
            kknews_contents = kknews_customized(target_url=self.url)
            return kknews_contents
        elif 'blog.xuite.net' in self.url:
            pass
        elif 'www.dcard.tw' in self.url:
            dcard_contents = DcardCustomized(target_url=self.url).execute()
            return dcard_contents
        elif 'pixnet.net' in self.url:
            pixnet_contents = pixnet_customized(target_url=self.url)
            return pixnet_contents
        else:
            raise Exception('domain format wrong!')

    def _extract_customized(self):
        """
        Dependencies on Project py-utils
        """
        try:
            content_title = BeautifulSoup(self.word, 'lxml').title.text
        except:
            content_title = ''
        content_url = self.url
        content_text = extractTextByDensity().extract_by_html_str(html_str=self.html_str)
        
        return [[content_title, content_url, content_text]]


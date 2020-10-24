"""
Generate the fake user agent to scrapy.
"""
from fake_useragent import UserAgent
ua = UserAgent()
# ie useragent
print(ua.ie)
# chrome useragent
#print(ua.chrome)
#
#print(ua.firefox)

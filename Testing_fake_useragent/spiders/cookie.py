"""show cookies"""
import browsercookie
chrome_cookiejar = browsercookie.chrome()
for cookie in chrome_cookiejar:
    print(cookie)

import requests
import random
import string
import json
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
from datetime import datetime
from fake_useragent import UserAgent

def pchome_customized(search_word: str, target_url: str):

    if not re.search('pchome.com.tw|pcstore.com.tw', target_url):
        return
    pchome_contents_result = []
    headers = {
        'cookie': 'ECC={}',
        'User-Agent': '',
        }

    ua = UserAgent()
    cookie_len = random.randint(10,20)
    cookie = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(cookie_len))
    headers['User-Agent'] = ua.firefox
    headers['cookie'] = 'ECC={cookie}'.format(cookie=cookie)

    query = search_word
    pages = 2

    prodids = []
    for page in list(range(1, pages)):
        url = 'https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={}&page={}&sort=sale/dc'.format(query, page)
        resp = requests.get(url,headers=headers)
        for prodid in resp.json()['prods']:
            prodids.append(prodid['Id'])
        prodids = list(set(prodids))

    df1 = []
    for i, Id in enumerate(prodids):
        columns, values = [], []
        sleep(0.7)
        ecapi = 'https://mall.pchome.com.tw/ecapi/ecshop/prodapi/v2/prod/{}&fields=Seq,Id,Stmt,Slogan,Name,Nick,Store,PreOrdDate,SpeOrdDate,Price,Discount,Pic,Weight,ISBN,Qty,Bonus,isBig,isSpec,isCombine,isDiy,isRecyclable,isCarrier,isMedical,isBigCart,isSnapUp,isDescAndIntroSync,isFoodContents,isHuge,isEnergySubsidy,isPrimeOnly,isWarranty,isLegalStore,isOnSale,isPriceTask,isBidding,isETicket&_callback=jsonp_prod&1587196620'.format(Id)
        resp = requests.get(ecapi, headers=headers)
        data = re.sub('try{jsonp_prod\(|\}\);\}catch\(e\)\{if\(window.console\)\{console.log\(e\)\;\}','',resp.text)
        data = json.loads(data)[Id+'-000']

        for key, value in data.items():
            columns.append(key)
            values.append(value)
        ndf = pd.DataFrame(data=values, index=columns).T
        df1.append(ndf)
    df1 = pd.concat(df1, ignore_index=True)
    df1 = df1[['Id','Name','Nick']]
    df1['Id'] = df1['Id'].apply(lambda x: re.sub('-000$','',x))


    df2 = []
    for i, Id in enumerate(prodids):
        columns, values = [], []
        sleep(0.7)
        cdn = 'https://ecapi.pchome.com.tw/cdn/ecshop/prodapi/v2/prod/{}/desc&fields=Id,Stmt,Equip,Remark,Liability,Kword,Slogan,Author,Transman,Pubunit,Pubdate,Approve&_callback=jsonp_desc'.format(Id+'-000')
        resp = requests.get(cdn, headers=headers)
        data = re.sub('try\{jsonp_desc\(|\}\);\}catch\(e\)\{if\(window.console\)\{console.log\(e\)\;\}','',resp.text)
        data = json.loads(data)
        data = data[Id]

        for key, value in data.items():
            columns.append(key)
            values.append(value)
        ndf = pd.DataFrame(data=values, index=columns).T
        df2.append(ndf)
    df2 = pd.concat(df2, ignore_index=True)

    df2 = df2[['Id','Stmt','Equip','Remark','Liability','Kword','Slogan']]
    df = pd.merge(df1, df2, how='left',on='Id')

    del df1, df2

    df['Nick'] = df['Nick'].apply(lambda x: BeautifulSoup(x,'lxml').text)
    df['Stmt'] = df['Stmt'].apply(lambda x: BeautifulSoup(x,'lxml').text)
    df['Stmt'] = df['Stmt'].apply(lambda x: BeautifulSoup(x,'lxml').text)
    df['Remark'] = df['Remark'].apply(lambda x: BeautifulSoup(x,'lxml').text)
    df['Liability'] = df['Liability'].apply(lambda x: BeautifulSoup(x,'lxml').text)
    df['Kword'] = df['Kword'].apply(lambda x: BeautifulSoup(x,'lxml').text)
    df['Slogan'] = df['Slogan'].apply(lambda x: BeautifulSoup(x,'lxml').text)

    result_df = pd.DataFrame()
    result_df['Id'] = df['Id']
    result_df['title'] = df['Name'].apply(lambda x: re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', x))
    result_df['text'] = df['Nick'] + df['Stmt'] + df['Equip'] + df['Remark'] + df['Liability'] + df['Kword'] + df['Slogan']
    del df
    result_df['text'] = result_df['text'].apply(lambda x: re.sub('\t|\n|\r|/| |：|:|,|<br/>|\xa0|\u3000', '。', x))

    for product in result_df.values:
        link = 'https://24h.pchome.com.tw/prod/' + product[0]
        title = product[1]
        text = product[2]
        pchome_contents_result.append([title, link, text])
        del title, link, text
    return pchome_contents_result
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# coding=utf-8 
from bs4 import BeautifulSoup
import requests
import csv
import re
import pandas as pd
from pandas import Series,DataFrame
import os
import time
from datetime import datetime
import traceback
import random
import pymongo
import numpy as np


# In[ ]:


def chunks(arr, n):
    return [arr[i:i+n] for i in range(0, len(arr), n)]


# In[ ]:


def getData(link):
    
    url = 'http://pm.kksk.org'+link
    
    index_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'
    }
    flag = True
    try_times = 0
    while flag:
        try:
            proxies = getProxy()
            html = requests.get(url,headers = index_headers,proxies = proxies,verify=False,timeout = (120,180)) # getHtml 
            time.sleep(random.uniform(0.5, 1))#Random time sleep in order to prevent from getting IP banned
            html.encoding = 'gbk'#this web is encoded in gbk
            soup = BeautifulSoup(html.text, "html.parser")

            updatetimefetch = soup.find('div',class_ = 'panel panel-primary hidden-xs')# updatetime fetch
            timefetch = updatetimefetch.find('h3')
            timestring = timefetch.string
            timenum = re.sub('\D','',timestring)# pure number time
            date = timenum[0:8]
            hour = timenum[8:10]

            citynamediv = soup.find('div',class_='panel-title row')#get city name
            citynamefetch = citynamediv.find('h1')
            cityname = citynamefetch.text
            cityname = re.sub("[^a-zA-Z0-9\u4e00-\u9fa5]", '', cityname)
            cityname = cityname[:2]

            tablediv = soup.find('div',class_='panel panel-primary hidden-xs')    

            datalist = []

            for tr in tablediv.findAll('tr'):
                for td in tr.findAll(['td']):
                    datalist.append(td.get_text())

            table = chunks(datalist,11)

            df = DataFrame(table)#transfer from list to dataframe

            df.drop(index = [0],inplace = True)#drop the first row which is average

            df.replace('',np.nan,inplace = True)# replace empty value as NaN
            df.replace(' - ',np.nan,inplace = True)
            df.replace('-',np.nan,inplace = True)

            df.columns = ['WatchPoint','AQI','Level','PrimaryPollution','PM25','PM10','CO','NO2','O3_1h','O3_8h','SO2']#change head

            col_name = df.columns.tolist()# add time to the dataframe head
            col_name.insert(0,'Date')
            col_name.insert(1,'Hour')
            df = df.reindex(columns=col_name)# reindex the dataframe head

            dateList = [date for x in range(0,(df.iloc[:,0].size))]# create time list
            hourList = [hour for x in range(0,(df.iloc[:,0].size))]

            df['Date'] = dateList # add time to the dataframe
            df['Hour'] = hourList

            dict_result = df.to_dict(orient='records')

            print('Get data of '+cityname)
            flag = False
            return dict_result
        
        except BaseException:
            try_times+=1
            if try_times > 20:#Max numbers of trying new ip is 20
                print('Proxy IP failed')
                return -1
                flag = False
            else:
                flag = True


# In[ ]:


from email.mime.text import MIMEText   #
import smtplib
def reportIssue(issueMsg):
    msg = MIMEText(issueMsg, 'plain', 'utf-8')
    fromAddr = 'zhouzeyu@jslcznkj.cn'
    msg['Subject'] = 'Code Error'#Mail subject
    msg['From'] = 'zhouzeyu@jslcznkj.cn'#Mail sender
    msg['To'] = 'zhouzeyu1219@hotmail.com'#Mail receiver

    try:
        # Check Mail sending SMTP server
        server = smtplib.SMTP_SSL('smtp.exmail.qq.com', port = 465) # SMTP default port 25, qq smtplib.SMTP_SSL(host, 465)
        # server.set_debuglevel(1)

        #server.ehlo() 
        #server.starttls()
        server.login(fromAddr, 'Jslc123456') # sendermail and password
        print('login done')
        server.sendmail(fromAddr, ['zhouzeyu1219@hotmail.com'], msg.as_string())
        server.quit()
        print('sent mail')
    except Exception as err:
        print(err)


# In[ ]:


def getProxy():# return new proxy ip
    proxy_pool = [{'https':'http://117.88.5.227:3000'},{'https':'http://117.88.176.186:3000'},
                  {'https':'http://14.153.55.180:3128'},{'https':'http://116.196.85.150:3128'},
                  {'https':'http://60.184.205.123:20866'},{'https':'http://113.124.92.12:9999'}]
    proxy = random.choice(proxy_pool)
    return proxy


# In[ ]:


if __name__ == '__main__':
    print('Started.')
    time.sleep(3000)
    index_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'   
    }
    url = 'http://pm.kksk.org/citylist.php'
    html = requests.get(url,headers = index_headers) # getHtml 
    html.encoding = 'gbk'
    soup = BeautifulSoup(html.text, "html.parser")
    urldiv = soup.find('div',class_='tab-pane',id = 'profile')
    urltable = urldiv.find('table',class_='table table-striped')
    
    linklist = []
    namelist = []
    n1 =  urltable.find_all('a')
    for n2 in n1:
        link = n2.get('href')
        name = n2.get('title')
        linklist.append(link)
        namelist.append(name)


# In[ ]:


while True:
    client = pymongo.MongoClient(host = 'localhost', port = 27017)   # 本地IP，默认端口
    db = client['NationalAir']  # 进入数据库
    col = db['data'] 
    print('Start getting data at ',datetime.now())
    start = datetime.now()
    for i in range(len(linklist)):
        try:
            resultlist = getData(linklist[i])
            for j in resultlist:
            	col.insert_one(j)
        except:
            reportIssue(traceback.format_exc())
            traceback.print_exc(file=open('error.txt','a+'))
            print(datetime.now(),' fail to get data of ',namelist[i])
    print('finish and sleep at ',datetime.now())
    client.close()
    end = datetime.now()
    
    time.sleep(3600-(end-start).seconds)


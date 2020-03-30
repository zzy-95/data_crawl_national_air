#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


def chunks(arr, n):
    return [arr[i:i+n] for i in range(0, len(arr), n)]


# In[3]:


def getData(city):
    
    print('-', city)
    
    url = 'http://www.pm25.in/'+city

    
    html = requests.get(url,timeout=(120,180)) # getHtml 
    html.encoding = 'utf-8'
    soup = BeautifulSoup(html.text, "html.parser")

    updatetimefetch = soup.find('div',class_ = 'live_data_time')# updatetime fetch
    timefetch = updatetimefetch.find('p')
    time = timefetch.string
    timenum = re.sub('\D','',time)# pure number time
    date = timenum[0:8]
    hour = timenum[8:10]

    tablediv = soup.find('div',class_='table')    

    datalist = []

    for tr in tablediv.findAll('tr'):
        for td in tr.findAll(['td']):
            datalist.append(td.get_text())

    table = chunks(datalist,11)

    tb = DataFrame(table)

    tb.replace('_','NaN',inplace = True)# replace empty value as NaN
    tb.replace(' ','NaN',inplace = True)

    tb.columns = ['WatchPoint','AQI','Level','PrimaryPollution','PM2.5','PM10','CO','NO2','O3_1h','O3_8h','SO2']

    col_name = tb.columns.tolist()# add time to the table head
    col_name.insert(0,'Date')
    col_name.insert(1,'Hour')
    tb = tb.reindex(columns=col_name)# add time list to the table

    dateList = [date for x in range(0,(tb.iloc[:,0].size))]# create time list
    hourList = [hour for x in range(0,(tb.iloc[:,0].size))]

    tb['Date'] = dateList
    tb['Hour'] = hourList

    csvName = 'data/' + city + '.csv'
    
    if os.path.exists(csvName)==True:     # write csv with tablehead if no existing file
        tb.to_csv(csvName, index = False, mode = 'a+',header = False)
    else:
        tb.to_csv(csvName,index = False, mode = 'a+')


# In[4]:


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


if __name__ == '__main__':
    print('Started.')
    time.sleep(1800)
    url = 'http://www.pm25.in/'
    html = requests.get(url) # getHtml 
    html.encoding = 'utf-8'
    soup = BeautifulSoup(html.text, "html.parser")
    namesdiv = soup.find('div',class_='all')

    namelist = []
    n1 =  namesdiv.find_all('a')
    for n2 in n1:
        n3 = n2.get('href')
        new_n3 = n3[1:]
        namelist.append(new_n3)
    
    namelist.remove('shannandiqu')
        
    while True:
        print('Start getting data at ',datetime.now())
        start = datetime.now()
        for i in range(len(namelist)):
            try:
                getData(namelist[i])
            except:
                reportIssue(traceback.format_exc())
                traceback.print_exc(file=open('error.txt','a+'))
                print(datetime.now(),' fail to get data of ',i,namelist[i])
        print('finish and sleep at ',datetime.now())
        end = datetime.now()
        time.sleep(3600-(end-start).seconds)


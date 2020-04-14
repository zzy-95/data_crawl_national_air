#!/usr/bin/env python
# coding: utf-8

# In[19]:


# coding=utf-8 
import csv
import re
import pandas as pd
from pandas import Series,DataFrame
import time
import datetime
import traceback
import pymongo
import numpy as np


# In[ ]:


def getData():
    try:
        client = pymongo.MongoClient(host = 'localhost', port = 27017)   # 本地IP，默认端口
        db = client['NationalAir']  # 进入数据库
        col = db['data'] 

        today = datetime.datetime.now()#current time

        date = today.strftime('%Y%m%d')#current date
        hour = today.hour#current hour
        prehour = int(hour) - 1

        offset = datetime.timedelta(days=-1)
        re_date = (today + offset).strftime('%Y%m%d')#yesterday date

        if hour == 0:
            data = col.find({"Date":re_date,"Hour":"23"})
        else:
            if int(hour) <= 10:
                data = col.find({"Date":date,"Hour":"0"+str(prehour)})
            else:
                data = col.find({"Date":date,"Hour":str(prehour)})

        df = pd.DataFrame(list(data))
        #for i in data:
            #df = df.append(i,ignore_index = True)
            
        #print(df)

        newdf = df.sort_values(by = 'AQI')
        newdf['AQIrank'] = newdf.AQI.rank(method = 'min',na_option = 'keep',pct = True,ascending = True)
        newdf.loc[newdf['AQI'] == np.nan,['AQIrank'] ] = np.nan

        newdf = newdf.sort_values(by = 'PM25')
        newdf['PM25rank'] = newdf.PM25.rank(method = 'min',na_option = 'keep',pct = True,ascending = True)
        newdf.loc[newdf['PM25'] == np.nan,['PM25rank'] ] = np.nan

        newdf = newdf.sort_values(by = 'PM10')
        newdf['PM10rank'] = newdf.PM10.rank(method = 'min',na_option = 'keep',pct = True,ascending = True)
        newdf.loc[newdf['PM10'] == np.nan,['PM10rank'] ] = np.nan

        newdf = newdf.sort_values(by = 'CO')
        newdf['COrank'] = newdf.CO.rank(method = 'min',na_option = 'keep',pct = True,ascending = True)
        newdf.loc[newdf['CO'] == np.nan,['COrank'] ] = np.nan

        newdf = newdf.sort_values(by = 'NO2')
        newdf['NO2rank'] = newdf.NO2.rank(method = 'min',na_option = 'keep',pct = True,ascending = True)
        newdf.loc[newdf['NO2'] == np.nan,['NO2rank'] ] = np.nan

        newdf = newdf.sort_values(by = 'O3_1h')
        newdf['O3_1hrank'] = newdf.O3_1h.rank(method = 'min',na_option = 'keep',pct = True,ascending = True)
        newdf.loc[newdf['O3_1h'] == np.nan,['O3_1hrank'] ] = np.nan

        newdf = newdf.sort_values(by = 'O3_8h')
        newdf['O3_8hrank'] = newdf.O3_8h.rank(method = 'min',na_option = 'keep',pct = True,ascending = True)
        newdf.loc[newdf['O3_8h'] == np.nan,['O3_8hrank'] ] = np.nan

        newdf = newdf.sort_values(by = 'SO2')
        newdf['SO2rank'] = newdf.SO2.rank(method = 'min',na_option = 'keep',pct = True,ascending = True)
        newdf.loc[newdf['SO2'] == np.nan,['SO2rank'] ] = np.nan

        if hour == 0:
            csvName = 'data/' + re_date + '23.csv'
            newdf.to_csv(csvName, index = False, mode = 'w+',header = True)
        else:
            if int(hour) <= 10:
                csvName = 'data/' + date+"0"+str(prehour) + '.csv'
                newdf.to_csv(csvName, index = False, mode = 'w+',header = True)
            else:
                csvName = 'data/' + date+str(prehour) + '.csv'
                newdf.to_csv(csvName, index = False, mode = 'w+',header = True)
    except BaseException:
        reportIssue(traceback.format_exc())
        traceback.print_exc(file=open('AirRankerror.txt','a+'))


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
    time.sleep(2400)
    while True:
        print('Start getting data at ',datetime.datetime.now())
        start = datetime.datetime.now()
        getData()
        print('finish and sleep at ',datetime.datetime.now())
        end = datetime.datetime.now()
        time.sleep(3600-(end-start).seconds)


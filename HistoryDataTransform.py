#!/usr/bin/env python
# coding: utf-8

# In[1]:


# coding=utf-8 
import csv
import pandas as pd
import os
import numpy as np
import pymongo


# In[ ]:


client = pymongo.MongoClient(host = 'localhost', port = 27017)   # 本地IP，默认端口
db = client['NationalAir']  # 进入数据库
col = db['historydata'] 


# In[2]:


openpath = 'HistoryData/'


# In[8]:


listFileName = os.listdir(openpath)
for filename in listFileName:
    #print(filename)
    df = pd.read_csv(openpath+filename,encoding = 'utf-8')
    
    a = pd.melt(df,id_vars=['date','hour','type'], var_name = 'WatchPoint')
    #print(a)
    b = a.set_index(['date','hour','type','WatchPoint']).unstack('type')
    #print(b)
    levels = b.columns.levels
    b.columns = levels[1]
    c = b.reset_index()
    #print(c)
    d = c.loc[:,['date','hour','WatchPoint','AQI','PM2.5','PM10','CO','NO2','O3','O3_8h','SO2']]
    
    d.replace('',np.nan,inplace = True)# replace empty value as NaN
    d.columns = ['Date','Hour','WatchPoint','AQI','PM25','PM10','CO','NO2','O3_1h','O3_8h','SO2']#change head
    
    dict_result = d.to_dict(orient='records')
    
    for i in dict_result:
        col.insert_one(i)

    #d.to_csv(savepath+filename, index = None, encoding = 'gb18030')


# In[ ]:





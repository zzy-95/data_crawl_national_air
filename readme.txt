1. 此爬虫AirPollutionDataFetch.py即时从PM25.in网站上抓取全国所有站点数据（除去山南地区 此地区从2017年开始停止更新）
2. 此网站源数据整点更新，但网站数据更新时间不固定
3. 数据输出格式为csv文件，按城市地区分开
4. 每一个小时抓取一次数据，并存入现有文件中
5. 文件表头为['Date','Hour','WatchPoint','AQI','Level','PrimaryPollution','PM2.5','PM10','CO','NO2','O3_1h','O3_8h','SO2']
分别为日期，时间（小时整点），监测点，AQI（空气质量指数），空气质量指数类别（优，良，轻度污染，中度污染，重度污染，严重污染），
首要污染物，PM2.5细颗粒物，PM10可吸入颗粒物，一氧化碳，二氧化碳，臭氧一小时平均，臭氧8小时平均，二氧化硫
6. 网页抓取 请求超时时间为 120s  读取超时时间为 180s 
7. 报错机制为log中显示错误（包括缺失的数据的时间和城市），生成error.txt文档，邮件发送报错提示
8. 如有缺失数据，可在此网站下载 http://beijingair.sinaapp.com/data/beijing/all/20131205/csv 链接中时间按类似格式更改（单日数据）
9. 历史数据来源 http://beijingair.sinaapp.com 百度网盘下载，每周更新

2020.4.2更新
因需求将csv文件名从城市名拼音改为城市名中文

2020.4.9
因网站PM25.in持续宕机，AirPollutionDataFetch.py暂停运行

2020.4.10
1.新爬虫TempNationalAirData.py,与AirPollutionDataFetch.py基本相同，数据源网站为http://pm.kksk.org/。输出为csv文件
2.MongoDBNationalAir.py和TempNationalAirData.py基本相同，输出数据导入服务器MongoDB数据库NationalAir，Collection为data，每个站点每小时数据为一个字典。
为了配合后续排名的代码，空值从字符串‘NaN’改为np.nan（类型为float）。
3.爬虫加入了代理IP池的功能，每次请求页面将从IP池里随机挑选一条IP作为代理IP

2020.4.13
1.NationalAirRank.py为全国站点空气污染因子数据排名
2.此代码从数据库中将当前时间前一小时的全国站点数据提取并根据因子数据进行排名，每个排名数值在每条站点数据后生成
3.生成一个csv文件，文件名为日期加小时
4.HistoryDataTransform.py读取历史数据的csv，将表格格式转换后直接导入数据库
历史数据源https://pan.baidu.com/s/1I701jRwEeD577Wk-6-ulug#list/path=%2F，提取码zc9s
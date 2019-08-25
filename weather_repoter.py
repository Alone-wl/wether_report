#coding=utf-8

from wxpy import *
import requests
from datetime import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler #定时框架
from urllib.request import urlopen
from bs4 import BeautifulSoup
 
bot = Bot(None, 2, None, None, None, None)#登陆微信
#tuling = Tuling(api_key='06aa52c7a9cc4c3c939ca4a5f031eebc')  #图灵机器人api
 
#单个好友
friend = bot.friends().search('吉姆爷爷')[0]#好友的微信昵称，或者你存取的备注
location = friend.city
print(friend)
print(friend.city)
friendlist = [friend]

# #好友列表
# friendlist = [ensure_one(bot.search(remark_name='')),
#     bot.friends().search(remark_name='')[0],
#     bot.friends().search(remark_name='')[0],
#     bot.friends().search(remark_name='')[0]
#     ]
# print(friendlist)
 
def get_weather(location):
    #准备url地址，得出location的结果
    #path ='http://api.map.baidu.com/telematics/v3/weather?location=%s&output=json&ak=TueGDhCvwI6fOrQnLM0qmXxY9N0OkOiQ&callback=?'
    path = 'http://v.juhe.cn/weather/index?format=2&cityname=%s&key=f820855776041b3fe236b2ff36c61bb2'
    url = path % location
    response = requests.get(url)
    results = response.json()
    print(results)
    str1 ='-你的城市: %s' % location
 
    #如果城市错误就按照成都的结果
    if results['error_code'] !=0:
        str1 = '你的地区%s获取失败，请修改资料。默认参数：天津\n' % location
        location ='天津'
        url = path % location
        response = requests.get(url)
        results = response.json()

    str0 = ('这是今天的天气预报！\n来自不太靠谱的长治小哥哥')
    tadayResult = results['result']['today']

    temperature = tadayResult['temperature']
    temperatureStr ='-今日温度:\n\t%s' % temperature
    wind = tadayResult['wind']
    windStr ='-风向:\n\t %s' % wind
    weather = tadayResult['weather']
    weatherStr ='-天气:\n\t %s' % weather
    dressing_advice = tadayResult['dressing_advice']
    dressing_adviceStr ='-穿衣:\n\t %s' % dressing_advice

    str = str0 + '\n' + str1 + '\n' + temperatureStr + '\n' + windStr + '\n' + dressing_adviceStr + '\n'
    return str
 
def get_iciba():
    url = "http://open.iciba.com/dsapi/"
    r = requests.get(url)
    content = r.json()['content']
    note = r.json()['note']
    str = '-每日一句：\n'+content +'\n'+note+ '\n'
    return str
 
#发送函数
def send_message():
    for i in range(len(friendlist)):
        friend = friendlist[i]
        location = friend.city
        print(i+1,'/%s' %len(friendlist), ' 姓名：%s' %friend, ' 地区：%s' %location)
        text = get_weather(friend.city) + '========\n' + get_iciba()
        friend.send(text)

        #发送成功通知我
        bot.file_helper.send(friend)
        bot.file_helper.send('发送完毕')
    return
 
#测试发送
# print('===测试===')
#send_message()

# print('tuling start...')
# @bot.register(friend)
# def auto_replay_person(msg):
#     tuling.do_reply(msg)

#定时器
print('weather repoter start...')
sched = BlockingScheduler()
sched.add_job(send_message,'cron',day_of_week='0-6',hour=2,minute =10)#设定发送的时间
sched.start()

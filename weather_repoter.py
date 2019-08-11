from wxpy import *
import requests
from datetime import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler #定时框架
from urllib.request import urlopen
from bs4 import BeautifulSoup
 
bot = Bot(cache_path=True)#登陆微信
tuling = Tuling(api_key='06aa52c7a9cc4c3c939ca4a5f031eebc')  #图灵机器人api
 
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
    path ='http://api.map.baidu.com/telematics/v3/weather?location=%s&output=json&ak=TueGDhCvwI6fOrQnLM0qmXxY9N0OkOiQ&callback=?'
    url = path % location
    response = requests.get(url)
    result = response.json()
    str1 ='-你的城市: %s' % location
 
    #如果城市错误就按照成都的结果
    if result['error'] !=0:
        str1 = '你的地区%s获取失败，请修改资料。默认参数：天津\n' % location
        location ='天津'
        url = path % location
        response = requests.get(url)
        result = response.json()
    str0 = ('这是今天的天气预报！来自靠谱的长治小哥哥')
    results = result['results']
    # 取出数据字典
    data1 = results[0]
    # 取出pm2.5值
    pm25 = data1['pm25']
    str2 ='-PM2.5 : %s  ' % pm25
    # 将字符串转换为整数 否则无法比较大小
    pm25 = int(pm25)
    if pm25 =='':
        pm25 =0
    # 通过pm2.5的值大小判断污染指数
    if 0 <= pm25 <35:
        pollution ='优'
        pollution_advise = '空气不错，适合多出去走走'
    elif 35 <= pm25 <75:
        pollution ='良'
        pollution_advise = '空气不错，适合多出去走走'
    elif 75 <= pm25 <115:
        pollution ='轻度污染'
        pollution_advise = '空气不太好，不宜在室外做剧烈运动'
    elif 115 <= pm25 <150:
        pollution ='中度污染'
        pollution_advise = '空气较差，记得带上口罩'
    elif 150 <= pm25:
        pollution ='重度污染'
        pollution_advise = '空气很差，还在窝在家里看剧玩游戏吧'
    str3 ='-空气指数: %s' % pollution
    result1 = results[0]
    weather_data = result1['weather_data']
    data = weather_data[0]
    datetime = data['date']
    temperature = data['temperature']
    str4 ='-今日温度:\n\t%s%s' % (datetime,temperature)
    wind = data['wind']
    str5 ='-风向: %s' % wind
    weather = data['weather']
    str6 ='-天气: %s' % weather
    if(str6.find('雨')!=-1 or str6.find('雪')!=-1):
        weather_advice = '雨雪天气记得带伞哦'
    elif(str6.find('暴雨')!=-1):
        weather_advice = '今天有暴雨，还是待在家吧'
    else:
        weather_advice = ''
    message = data1['index']
    str8 ='-穿衣:\n\t %s' % message[0]['des']
    str11 ='-紫外线:\n\t %s' % message[4]['des']
    str = str0 +'\n' + str1 +'\n' + str2 +'\n' + str3 +'\n' + str4 + '\n' + str5 +'\n' + str6 +'\n' + str8 +'\n' + str11 + '\n'
    if(weather_advice != ''):
        Tips = '\t' + pollution_advise + '\n\t' + weather_advice
    else:
        Tips = '\t' + pollution_advise
    str_dic = {'wether':str, 'Tips':Tips}
    return str_dic
 
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
        text = get_weather(friend.city)['wether'] + '========\n' + get_iciba()
        tips = '李子夏的定制Tips:\n' + get_weather(friend.city)['Tips'] + '\n\t如果今早心情恰巧不错的话，顺便吃个早饭也是极好的'
        friend.send(text)
        friend.send(tips)
        #发送成功通知我
        bot.file_helper.send(friend)
        bot.file_helper.send('发送完毕')
    return
 
#测试发送
# print('===测试===')
#send_message()

print('tuling start...')
@bot.register(friend)
def auto_replay_person(msg):
    tuling.do_reply(msg)
#定时器
print('weather repoter start...')
sched = BlockingScheduler()
sched.add_job(send_message,'cron',day_of_week='0-6',hour=8,minute =0)#设定发送的时间
sched.start()

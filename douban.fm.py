#!/usr/bin/python
# coding: utf-8
  
import sys
import os
import subprocess
import getopt
import time
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import getpass
import configparser
from http.cookiejar import CookieJar
  
# 保存到文件
def save(filename, content):
    file = open(filename, 'wb')
    file.write(content)
    file.close()
  
  
# 获取播放列表
def getPlayList(channel='1', opener=None):
    url = 'http://douban.fm/j/mine/playlist?type=n&sid=&pt=0.0&channel=' + channel + '&from=mainsite' #&r=daab079b3c'
#    url = 'http://douban.fm/j/mine/playlist?type=n&sid=&pt=0.0&channel=' + channel
#    url = 'http://douban.fm/j/mine/playlist?type=n&channel=' + channel
    if opener == None:
        return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    else:
        return json.loads(opener.open(urllib.request.Request(url)).read().decode('utf-8'))
  
  
# 发送桌面通知
def notifySend(picture, title, content):
    subprocess.call([
        'notify-send',
        '-i',
        os.getcwd() + '/' + picture,
        title,
        content])
  
  
# 登录douban.fm
def login(username, password):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    while True:
        print('正在获取验证码……')
        captcha_id = opener.open(urllib.request.Request(
            'http://douban.fm/j/new_captcha')).read().strip('"')
        save(
            '验证码.jpg',
            opener.open(urllib.request.Request(
                'http://douban.fm/misc/captcha?size=m&id=' + captcha_id
            )).read())
        captcha = input('验证码: ')
        print('正在登录……')
        response = json.loads(opener.open(
            urllib.request.Request('http://douban.fm/j/login'),
            urllib.parse.urlencode({
                'source': 'radio',
                'alias': username,
                'form_password': password,
                'captcha_solution': captcha,
                'captcha_id': captcha_id,
                'task': 'sync_channel_list'})).read())
        if 'err_msg' in list(response.keys()):
            print(response['err_msg'])
        else:
            print('登录成功')
            return opener
  
  
# 播放douban.fm
def play(channel='1', opener=None):
    while True:
        if opener == None:
            playlist = getPlayList(channel)
        else:
            playlist = getPlayList(channel, opener)
          
        if playlist['song'] == []:
            print('获取播放列表失败')
            break
#                picture,
  
        for song in playlist['song']:
            picture = 'picture/' + song['picture'].split('/')[-1]
  
            # 下载专辑封面
            save(
                picture,
                urllib.request.urlopen(song['picture']).read())
  
            # 发送桌面通知
#            notifySend(
#                picture,
#                song['title'],
#                song['artist'] + '\n' + song['albumtitle'])
  
            # 播放
            player = subprocess.Popen(['mplayer', song['url']])
            time.sleep(song['length'])
            player.kill()
  
  
def main(argv):
    # 默认参数
    channel = '1'
    user = ''
    password = ''
  
    # 获取、解析命令行参数
    try: 
        opts, args = getopt.getopt(
            argv, 'u:p:c:', ['user=', 'password=', 'channel=']) 
    except getopt.GetoptError as error:
        print(str(error))
        sys.exit(1)
  
    # 命令行参数处理
    for opt, arg in opts:
        if opt in ('-u', '--user='):
            user = arg
        elif opt in ('-p', '--password='):
            password = arg
        elif opt in ('-c', '--channel='):
            channel = arg
  
    if user == '':
        play(channel)
    else:
        if password == '':
            password = getpass.getpass('密码：')
        opener = login(user, password)
        play(channel, opener)
  
  
if __name__ == '__main__':
    main(sys.argv[1:])

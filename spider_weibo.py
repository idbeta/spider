#!/usr/bin/env python
# encoding=utf-8
import requests,re,os,sys,time
import codecs
import urllib
import urllib2
import cookielib
import base64
import json
import hashlib
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.PhantomJS(executable_path=r'D:\phantomjs-2.1.1-windows\bin\phantomjs.exe')#这要可能需要制定phatomjs可执行文件的位置
driver.set_window_size(1024, 768) 
sqlite = sqlite3.connect(os.path.dirname(os.path.abspath(sys.argv[0]))+r"\sqlite.db") 
sqlitecursor = sqlite.cursor()

def cur_file_dir():
    return os.path.split(os.path.realpath(__file__))[0]
    
def get_containerid(data):
    return re.findall(',"containerid":"([\d]*?)"',data)[0]
                
def get_fllowers_byphantomjs(uid):    
    murl='http://m.weibo.cn/u/%s'%uid
    driver.get(murl)
    time.sleep(1)
    containerid = get_containerid(driver.page_source)
    cidurl='http://m.weibo.cn/page/tpl?containerid=%s_-_FOLLOWERS&page=1'%containerid
    driver.get(cidurl)
    r = requests.get(cidurl)
    time.sleep(1)
    try:
        maxid = re.findall('"maxPage":([\d]*?),',driver.page_source)[0]
    except Exception,info:
        print cidurl
        driver.save_screenshot('maxid.png')
        print driver.page_source
        print r.status_code
    for i in range(2,int(maxid)+1):
        furl='http://m.weibo.cn/page/tpl?containerid=%s_-_FOLLOWERS&page=%s'%(containerid,i)
        driver.get(furl)
        r = requests.get(furl)
        time.sleep(1)
        try:
            weibo=json.loads( str(re.findall('\[\{"mod_type":.*?\}\]\}\]',driver.page_source)[0]).replace('\\n','') )
        except Exception,info:
            print furl
            driver.save_screenshot('FOLLOWERS.png')
            print driver.page_source
            print r.status_code            
        for ii in range(len(weibo[1]['card_group'])):
            uid= weibo[1]['card_group'][ii]['user']['id']            
            screen_name=weibo[1]['card_group'][ii]['user']['screen_name']
            fansNum=weibo[1]['card_group'][ii]['user']['fansNum']            
            sql=sqlitecursor.execute('''SELECT * from weibo where uid='%s' '''%uid)
            one = sqlitecursor.fetchone()
            if one== None:
                sqlitecursor.execute('''insert into weibo (uid,screen_name,fansNum) values ('%s','%s','%s')'''%(uid,screen_name,fansNum))
                sqlitecursor.execute("VACUUM")
                sqlite.commit()
        time.sleep(10)

def get_fllowers_main_byrequest(uid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }
    murl='http://m.weibo.cn/u/%s'%uid
    r = requests.get(murl)    
    containerid = get_containerid(r.text)
    cidurl='http://m.weibo.cn/page/tpl?containerid=%s_-_FOLLOWERS&page=1'%containerid
    r = requests.get(cidurl)
    try:
        maxid = re.findall('"maxPage":([\d]*?),',r.text)[0]
    except Exception,info:
        print cidurl
        print r.status_code
        print r.text
    for i in range(2,int(maxid)+1):
        furl='http://m.weibo.cn/page/tpl?containerid=%s_-_FOLLOWERS&page=%s'%(containerid,i)
        r = requests.get(furl)
        try:
            weibo=json.loads( str(re.findall('\[\{"mod_type":.*?\}\]\}\]',r.text)[0]).replace('\\n','') )
        except Exception,info:
            print furl
            print r.status_code 
            print r.text                       
        for ii in range(len(weibo[1]['card_group'])):
            uid= weibo[1]['card_group'][ii]['user']['id']            
            screen_name=weibo[1]['card_group'][ii]['user']['screen_name']
            fansNum=weibo[1]['card_group'][ii]['user']['fansNum']            
            sql=sqlitecursor.execute('''SELECT * from weibo where uid='%s' '''%uid)
            one = sqlitecursor.fetchone()
            if one== None:
                sqlitecursor.execute('''insert into weibo (uid,screen_name,fansNum) values ('%s','%s','%s')'''%(uid,screen_name,fansNum))
                sqlitecursor.execute("VACUUM")
                sqlite.commit()
        time.sleep(10)        
        
def get_fllowers(id = 1):    
    sql=sqlitecursor.execute('''select max(id) from weibo''')
    one = sqlitecursor.fetchone()
    if int(one[0]) > id:            
        for i in range(id,int(one[0])):
            sql=sqlitecursor.execute('''select uid from weibo where id=%s'''%i)
            one = sqlitecursor.fetchone()            
            # get_fllowers_byphantomjs(one[0])
            get_fllowers_main_byrequest(one[0])
            print i,one[0]
    else:
        return
    get_fllowers(int(one[0]))
   
if __name__ == '__main__':
    os.chdir(cur_file_dir())
    sqlite.execute('''CREATE TABLE weibo
       (id           INTEGER PRIMARY KEY     autoincrement,
       uid           char(32)    NOT NULL,
       screen_name             TEXT    NOT NULL,
       fansNum            INT     NOT NULL);''')
    sqlitecursor.execute('''VACUUM''')
    sqlite.commit()
    # get_fllowers_byphantomjs(1765148101) 
    get_fllowers_main_byrequest(1765148101)    
    get_fllowers()
    
    

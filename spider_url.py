#!/usr/bin/env python
# encoding=utf-8
import requests,re,os,sys
import codecs
import urllib
from bs4 import BeautifulSoup
from openpyxl import Workbook

def cur_file_dir():
    return os.path.split(os.path.realpath(__file__))[0]

wb = Workbook()
dest_filename = u'电影.xlsx'
ws1 = wb.active  
ws1.title = u"电影top250"

def download_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }
    data = requests.get(url, headers=headers).content
    return data

def getlnk1(doc):   
    linkname='' 
    soup = BeautifulSoup(doc, 'html.parser')
    links=soup.findAll('a') 
    fobj=open(cur_file_dir()+'\\log.txt','w')    
    for i in links: 
        ##判断tag是a的里面，href是否存在。 
        if 'href' in str(i): 
            linkname=i.string
            linkaddr=i['href'] 
            if 'NoneType' in str(type(linkname)):#当i无内容是linkname为Nonetype类型。 
                print linkaddr 
                # fobj.writelines(linkaddr)
            else: 
                print linkname+':'+linkaddr 
                # fobj.writelines(linkname+':'+linkaddr )    

def getlnk2(doc):   
    urls = re.findall("<.*?href.*?>",doc)
##    print urls
    lnklist=[] 
    for n in urls:
        url = re.search(r"=.*?[ >]",n)
        url_box = re.sub("""[= '">]""",'',url.group())
        if url_box == '#':
            continue
        if '/' not in url_box:
            continue
        if ':' not in url_box:
            continue
        print url_box
        lnklist.append(url_box)
##    print lnklist

if __name__ == '__main__':
    url = 'http://www.360.cn'
    name = []
    star_con=[]
    score = []
    info = []
    doc = download_page(url)
    getlnk1(doc)
##    getlnk2(doc)
# -*- coding:utf-8 -*-
import ruliweb
import ppomppu
import fmkorea
import humoruniv
from time import sleep, ctime
from selenium import webdriver
import urllib.parse as parse
import urllib.request as req
import datetime
import os
import sys
from multiprocessing import Pool
PHANTOM_PATH = "C:\\phantomjs\\phantomjs.exe"

#크롤링 사이트 목록 >> DB로 바꾸기 
sites = { 
         'fmkorea' : "http://www.fmkorea.com/index.php?mid=humor",#c1
#        'ppomppu' : "http://www.ppomppu.co.kr/zboard/zboard.php?id=humor",#c2
#        'humoruniv' : "http://web.humoruniv.com/board/humor/list.html?table=pds", #c3
#        'ruliweb' : "http://bbs.ruliweb.com/community/board/300143/list?view_best=1", #c4
#        'todayhumor' : "http://www.todayhumor.co.kr/board/list.php?table=humordata",
        }

def getUrl (site, page):
    # 분석 대상 HTML 가져오기
    browser = webdriver.PhantomJS(PHANTOM_PATH)
    baseUrl = sites.get(site)
    if (site == humoruniv):
        values = {
        'pg': page
        }
    else :        
        values = {
        'page': page
        }

    params = parse.urlencode(values)  
    page_url = baseUrl + "&" + params
    print(page_url)
    browser.get(page_url)
    html = browser.page_source
    return html


def date_compare (contDate):
    contDt = contDate.split('-')
    today = datetime.date.today()
    ago = today - datetime.timedelta(3)
    temp = str(ago).split(':')[0]
    agoDt = temp.split('-')
    if (int(contDt[0]) < int(agoDt[0])) :
        return False
    elif (int(contDt[1]) < int(agoDt[1])):
        return False
    elif (int(contDt[2]) < int(agoDt[2])):
        return False
    return True

def save_file (img_url, file_path, file_name):
    if (os.path.isdir( file_path) is not True):
        os.makedirs(file_path)

    fullFileName = os.path.join(file_path, file_name)
    try:
        req.urlretrieve(img_url, fullFileName)
    except:
        print('==========================')
        print('예외파일: ' + file_path)
        print('==========================')
    return file_path

#def crawl(site):
#    eval(site).parseContent()

#크롤링 실행
if __name__ == "__main__":
    
    siteList = list(sites.keys())
    print('start crawl : ', ctime())


    for site in siteList :
        eval(site).parseContent()

    print("finish")
    
    #pool = Pool(processes = 4)
    #pool.map(crawl, siteList)

    #모든 프로세스를 닫아야함///
    #pool.close()


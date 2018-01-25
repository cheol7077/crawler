# -*- coding:utf-8 -*-
import ruliweb
import ppomppu
import fmkorea
import humoruniv
from time import sleep, ctime
import time
from selenium import webdriver
import urllib.parse as parse
import urllib.request as req
import datetime
import traceback
import os
import sys
from multiprocessing import Pool

DRIVER = 'C:\\chromedriver.exe'

#크롤링 사이트 목록 >> DB로 바꾸기 
sites = { 
         'fmkorea' : "http://www.fmkorea.com/index.php?mid=humor&page=",#c1
         'ppomppu' : "http://www.ppomppu.co.kr/zboard/zboard.php?id=humor&page=",#c2
         'humoruniv' : "http://web.humoruniv.com/board/humor/list.html?table=pds&pg=", #c3
         'ruliweb' : "http://bbs.ruliweb.com/community/board/300143/list?view_best=1&page=1", #c4
        }

def getUrl (site, page):
    # 분석 대상 HTML 가져오기
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    browser = webdriver.Chrome(DRIVER, chrome_options=options)
    baseUrl = sites.get(site)

    page_url = baseUrl + str(page)
    print(page_url)
    browser.get(page_url)
    html = browser.page_source
    return html

def date_compare (contDate):
    contDt = contDate.split('-')
    today = datetime.date.today()
    ago = today - datetime.timedelta(days=3)
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
        r = req.Request(img_url, headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
        res = req.urlopen(r)
        with open(fullFileName, 'wb') as f:
            f.write(res.read())
            f.close()
    except :
        print('==========================')
        traceback.print_exc()
        print(' : ' + img_url + '      저장경로'+ file_path)
        print('==========================')
    return file_path    

def crawl(site):
    eval(site).parseContent()

#크롤링 실행
if __name__ == "__main__":
    siteList = list(sites.keys())
    print('start crawl : ', ctime())
    start_time = time.time()

    try:
        pool = Pool(processes = 4)
        pool.map(crawl, siteList)
        pool.close()
    except KeyboardInterrupt:
        pool.terminate()
        print('KeyboardInterrupt')
    except :
        print('==========================')
        traceback.print_exc()
        print('==========================')
        pool.terminate()
    finally:
        pool.join()
        print("finish : ",  ctime())
        end_time = time.time()
        print('실행시간: {}'.format(end_time - start_time))
        


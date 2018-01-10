# -*- coding:utf-8 -*-
#import ppomppu
import fmkorea
#import threppa
import threading
from time import sleep, ctime
from selenium import webdriver
import urllib.parse as parse
import datetime
from multiprocessing import Pool
PHANTOM_PATH = "C:\\phantomjs\\phantomjs.exe"

#크롤링 사이트 목록 >> DB로 바꾸기 
sites = {#'ppomppu' : "http://www.ppomppu.co.kr/zboard/zboard.php?id=humor", 
        'fmkorea' : "http://www.fmkorea.com/index.php?mid=humor",
#        'todayhumor' : "http://www.todayhumor.co.kr/board/list.php?table=humordata",
#        'threppa' : "http://threppa.com/bbs/board.php?bo_table=0207"
        }

def getUrl (site, page):
    # 분석 대상 HTML 가져오기
    browser = webdriver.PhantomJS(PHANTOM_PATH)
    baseUrl = sites.get(site)
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


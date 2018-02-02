# -*- coding:utf-8 -*-
import connDB
import re
from time import sleep
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import serve

DRIVER = 'C:\\chromedriver.exe'
PPOMPPU_PAGE = 'http://www.ppomppu.co.kr/zboard/zboard.php?id=freeboard&page='
PPOMPU_VIEW = 'http://www.ppomppu.co.kr/zboard/zboard.php?id=freeboard&divpage=1055&no='

ROW_SELECTOR = '#revolution_main_table > tbody > tr'
URL_SELECTOR = 'td:nth-of-type(3) > a'
TITLE_SELECTOR = 'td:nth-of-type(3) > a > font'
HITS_SELECTOR = 'td:nth-of-type(6)'
REC_SELECTOR = 'td:nth-of-type(5)'
DATE_SELECTOR = 'td:nth-of-type(4)'
COCNT_SELECTOR = 'td:nth-of-type(3)'

INIT_PAGE = 1

USING_SELENIUM = True

def parseContent():
    print('ppomppu start!')
    total = 0
    insertValue = 0
    insertFail = 0
    updateValue = 0
    updateFail = 0    
    
    db = connDB.connDB()

    new = True
    page = INIT_PAGE
    
    while new:
        print('ongoing ppomppu page.{}'.format(page))         
        rowList = getRowList(page)

        for row in rowList:
            try:
                dateValue = datetime.strptime(row.select_one(DATE_SELECTOR)['title'], '%y.%m.%d %H:%M:%S')
                timeLimit = datetime.now() - timedelta(days=1)
                
                if (dateValue - timeLimit).total_seconds() <= 0:
                    new = False
                    break
            
                total += 1
            
                bidValue = parse_qs(urlparse(row.select_one(URL_SELECTOR)['href']).query)['no'][0]
                urlValue = PPOMPU_VIEW + bidValue
                titleValue = row.select_one(TITLE_SELECTOR).string
                hitsValue = row.select_one(HITS_SELECTOR).string
                cocntValue = getCocntText(row)
                recValue = getRecText(row)
            
                if db.select(urlValue) == 0:               
                    values = (bidValue, titleValue, dateValue, urlValue, hitsValue, cocntValue, recValue, 'c2')
                    result = db.insert(values)
                    if result != 1:
                        insertFail += 1
                    else:
                        insertValue += 1
                else:
                    values = (hitsValue, cocntValue, recValue, urlValue)    
                    result = db.update(values)
                    if result != 1:
                        updateFail += 1
                    else:
                        updateValue += 1
            except (AttributeError, TypeError):
                print('error at {} page'.format(page))
                continue                                

        page += 1
        sleep(1)
    
    print('exit ppomppu!')    
    print('insert - success: {}, fail: {}'.format(insertValue, insertFail))
    print('update - success: {}, fail: {}'.format(updateValue, updateFail))
    print('total: {} cases'.format(total))
    print('=================================')
    

def getRowList(page): 
    pageUrl = PPOMPPU_PAGE + str(page)
    soup = serve.getSoup(pageUrl)
    rowList = soup.find_all("tr", class_= re.compile(r'list0|1'))
    
    return rowList


def getRecText(row):
    recTag = row.select_one(REC_SELECTOR)

    if recTag.string is None:
        recText = '0'
    else:
        recText = recTag.string.split('-')[0].strip()
    
    return recText


def getCocntText(row):
    cocntTag = row.select_one(COCNT_SELECTOR)
    if cocntTag.select_one('span > span') is None:
        nocText = '0'
    else:
        nocText = cocntTag.select_one('span > span').string
        
    return nocText

if __name__ == "__main__":
    parseContent()
    
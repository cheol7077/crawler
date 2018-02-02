# -*- coding:utf-8 -*-
import bs4
import connDB
import re
from re import search
from bs4 import element
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from time import sleep
import serve

MLBPARK_PAGE = 'http://mlbpark.donga.com/mp/b.php?m=list&b=bullpen&query=&select=&user=&p='
MLBPARK_VIEW = 'http://mlbpark.donga.com/mp/b.php?p=1&b=bullpen&select=&query=&user=&site=donga.com&reply=&source=&sig=h6j9Gg-Yg3DRKfX@hlj9GY-1khlq&id='

ROW_SELECTOR = '#container > div.contents > div.left_cont > div.tbl_box > table > tbody > tr'
DATE_SELECTOR = 'td:nth-of-type(4) > span'
URL_SELECTOR = 'td:nth-of-type(2) > a'
TITLE_SELECTOR = 'td:nth-of-type(2) > a > span.bullpen'
HITS_SELECTOR = 'td:nth-of-type(5) > span'
COCNT_SELECTOR = 'td:nth-of-type(2) > a > span.bullpen > span:nth-of-type(1)'

INIT_PAGE = 1


def parseContent():
    print('mlbpark start!')
    total = 0
    insertValue = 0
    insertFail = 0
    updateValue = 0
    updateFail = 0
    
    db = connDB.connDB()
    
    new = True
    page = INIT_PAGE
    
    while new:
        print('ongoing mlbpark page.{}'.format(page))          
        rowList = getRowList(page)
        
        for row in rowList:
            if bool(re.match('[0-9]', row.select_one('td').text)):
                dateValue = datetime.strptime(getDateText(row), '%Y-%m-%d %H:%M:%S')
                timeLimit = datetime.now() - timedelta(days=1)
                
                if (dateValue - timeLimit).total_seconds() <= 0:
                    new = False
                    break
                
                total += 1
                
                bidValue = parse_qs(urlparse(row.select_one(URL_SELECTOR)['href']).query)['id'][0]
                urlValue = MLBPARK_VIEW + bidValue
                titleValue = getTitleText(row)
                hitsValue = row.select_one(HITS_SELECTOR).string.replace(',', '')
                cocntValue = getCocntText(row)
                recValue = '0'
                
                if db.select(urlValue) == 0:               
                    values = (bidValue, titleValue, dateValue, urlValue, hitsValue, cocntValue, recValue, 'c5')
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
                                        
        page += 30
        sleep(1)
        
    print('exit mlbpark!')    
    print('insert - success: {}, fail: {}'.format(insertValue, insertFail))
    print('update - success: {}, fail: {}'.format(updateValue, updateFail))
    print('total: {} cases'.format(total))
    print('=================================')

def getRowList(page): 
    pageUrl = MLBPARK_PAGE + str(page)
    soup = serve.getSoup(pageUrl)
    rowList = soup.select(ROW_SELECTOR)
    return rowList

def getDateText(row):
    dateText = row.select_one(DATE_SELECTOR).string

    if dateText.count('-') == 0:
        now = datetime.now()
        dateText = str(now.year) + '-' + '{:02d}'.format(now.month) + '-' + str(now.day) + ' ' + dateText
    else:
        dateText += ' 00:00:00'
        
    return dateText


def getTitleText(row):
    titleTag = row.select_one(TITLE_SELECTOR).contents
    
    for element in titleTag:
        if type(element) is bs4.element.NavigableString:
            titleText = element
            break
    
    return titleText


def getCocntText(row):
    cocntTag = row.select_one(COCNT_SELECTOR)
    cocntText = '0'

    if cocntTag is not None:
        if cocntTag['class'][0] == 'replycnt':
            cocntText = cocntTag.string
            cocntText = search('\[(\d+)\]', cocntText).group(1)
    
    return cocntText



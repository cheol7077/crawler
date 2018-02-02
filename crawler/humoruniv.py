# -*- coding:utf-8 -*-

import sys
import os
sys.path.insert(0, "/crawler/site")

import connDB
import serve
from re import search
from bs4 import element
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from time import sleep

DRIVER = 'C:\\chromedriver.exe'
HUMORUNIV_PAGE = 'http://web.humoruniv.com/board/humor/list.html?table=pds&pg='
HUMORUNIV_VIEW = 'http://web.humoruniv.com/board/humor/read.html?table=pds&pg=&number='

ROW_SELECTOR = '#cnts_list_new > div:nth-of-type(1) > table:nth-of-type(2) > tr'
DATE_SELECTOR = 'td.li_date'
URL_SELECTOR = 'td:nth-of-type(2) > a'
HITS_SELECTOR = 'td:nth-of-type(7)'
REC_SELECTOR = 'td:nth-of-type(8) > span'

INIT_PAGE = 0

header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}


def parseContent():
    print('humoruniv start!')
    total = 0
    insertValue = 0
    insertFail = 0
    updateValue = 0
    updateFail = 0
    
    db = connDB.connDB()
    
    new = True
    page = INIT_PAGE
    
    while new:
        print('ongoing humoruniv page.{}'.format(page))      
        rowList = getRowList(page)
        
        for row in rowList:
            if row.has_attr('id'):
                dateValue = getDateText(row)
                timeLimit = datetime.now() - timedelta(days=1)
            
                if (dateValue - timeLimit).total_seconds() <= 0:
                    new = False
                    break
                
                total += 1
            
                bidValue = parse_qs(urlparse(row.select_one(URL_SELECTOR)['href']).query)['number'][0]
                urlValue = HUMORUNIV_VIEW + bidValue
                titleValue = getTitleText(row)
                hitsValue = row.select_one(HITS_SELECTOR).string.strip().replace(',', '')
                cocntValue = getCocntText(row)
                recValue = row.select_one(REC_SELECTOR).string
            
                if db.select(urlValue) == 0:               
                    values = (bidValue, titleValue, dateValue, urlValue, hitsValue, cocntValue, recValue, 'c3')
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
                                        
        page += 1
        sleep(1)
    print('exit humoruniv!')    
    print('insert - success: {}, fail: {}'.format(insertValue, insertFail))
    print('update - success: {}, fail: {}'.format(updateValue, updateFail))
    print('total: {} cases'.format(total))
    print('=================================')

def getRowList(page):
    pageUrl = HUMORUNIV_PAGE + str(page)
    soup = serve.getSoup(pageUrl)
    rowList = soup.select(ROW_SELECTOR)

    return rowList


def getDateText(row):
    tag = row.select_one(DATE_SELECTOR)
    dateTag = tag.select_one('span.w_date').string
    timeTag = tag.select_one('span.w_time').string
    dateText = dateTag + ' ' + timeTag
    return datetime.strptime(dateText, '%Y-%m-%d %H:%M')


def getTitleText(row):
    titleTag = row.select_one(URL_SELECTOR).contents
    
    for child in titleTag:
        if type(child) is element.NavigableString:
            titleText = child.strip()
            break
            
    return titleText


def getCocntText(row):
    tag = row.select_one(URL_SELECTOR)
    cocntText = '0'
    
    cocntTag = tag.find(class_='list_comment_num')
    
    if cocntTag is not None:
        cocntText = cocntTag.string.strip()
        cocntText = search('\[(\d+)\]', cocntText).group(1)
    
    return cocntText
'''
if __name__ == "__main__":
    parseContent()
'''
# -*- coding:utf-8 -*-
import connDB
from datetime import datetime, timedelta
from time import sleep
import serve
from urllib.parse import urlparse

FMKOREA_PAGE = 'http://www.fmkorea.com/index.php?mid=humor&page='
FMKOREA_VIEW = 'http://www.fmkorea.com/'

ROW_SELECTOR = '#bd_486616_0 > div > table > tbody > tr'
DATE_SELECTOR = 'td:nth-of-type(4)n'
URL_SELECTOR = 'td:nth-of-type(2) > a:nth-of-type(1)'
HITS_SELECTOR = 'td:nth-of-type(5)'
COCNT_SELECTOR = 'td:nth-of-type(2)'
REC_SELECTOR = 'td:nth-of-type(6)'

INIT_PAGE = 1

def parseContent():
    print('fmkorea start!')
    total = 0
    insertValue = 0
    insertFail = 0
    updateValue = 0
    updateFail = 0
    timeFlag = 0 
    
    db = connDB.connDB()
    
    new = True
    page = INIT_PAGE
    
    while new:
        print('ongoing fmkorea page.{}'.format(page))        
        rowList = getRowList(page)

        for row in rowList:
            if not row.has_attr('class'):
                dateValue, timeFlag = getDateText(row, timeFlag)
                timeLimit = datetime.now() - timedelta(days=1)
                
                if (dateValue - timeLimit).total_seconds() <= 0:
                    new = False
                    break
                
                total += 1
                
                bidValue = urlparse(row.select_one(URL_SELECTOR)['href']).path.replace('/', '')
                urlValue = FMKOREA_VIEW + bidValue
                titleValue = row.select_one(URL_SELECTOR).string.strip()
                hitsValue = row.select_one(HITS_SELECTOR).string.strip()
                cocntValue = getCocntText(row)
                recValue = getRecText(row)

                if db.select(urlValue) == 0:               
                    values = (bidValue, titleValue, dateValue, urlValue, hitsValue, cocntValue, recValue, 'c1')
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
    print('exit fmkorea!')    
    print('insert - success: {}, fail: {}'.format(insertValue, insertFail))
    print('update - success: {}, fail: {}'.format(updateValue, updateFail))
    print('total: {} cases'.format(total))
    print('=================================')

    
def getRowList(page): 
    pageUrl = FMKOREA_PAGE + str(page)
    soup = serve.getSoup(pageUrl)
    rowList = soup.select(ROW_SELECTOR)

    return rowList


def getDateText(row, timeFlag):
    dateText = row.select_one(DATE_SELECTOR).string.strip()

    if dateText.count('.') == 0:
        if timeFlag == 0:
            timeFlag = configTimeFlag(dateText) 
        if timeFlag == 0: 
            now = datetime.now()          
            dateText = str(now.year) + '-' + '{:02d}'.format(now.month) + '-' + str(now.day) + ' ' + dateText
        elif timeFlag != 0:
            yesterday = datetime.now() - timedelta(1)            
            dateText = str(yesterday.year) + '-' + '{:02d}'.format(yesterday.month) + '-' + str(yesterday.day) + ' ' + dateText
    else:
        dateText = dateText.replace('.', '-') + ' 00:00' 
    return datetime.strptime(dateText, '%Y-%m-%d %H:%M'), timeFlag

def configTimeFlag(dateText):
    now = datetime.now()
    nowT= timedelta(hours = now.hour, minutes = now.minute)    
    dateTextT = timedelta(hours = int(dateText.split(':')[0]), minutes = int(dateText.split(':')[1]))
    if (nowT < dateTextT) :        
        return 1
    else :
        return 0
                
def getCocntText(row):
    tag = row.select_one(COCNT_SELECTOR)
    
    cocntTag = tag.find(class_='replyNum')
    
    if cocntTag is not None:
        cocntText = cocntTag.string
    else:
        cocntText = '0'
    
    return cocntText


def getRecText(row):
    tag = row.select_one(REC_SELECTOR)
    
    if tag.string is not None:
        recText = tag.string.strip()
        if recText == '':
            recText = '0'
    else:
        recText = tag.select_one('span').string
    
    return recText
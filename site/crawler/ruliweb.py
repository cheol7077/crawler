# -*- coding:utf-8 -*-
import connDB
from datetime import datetime, timedelta
from time import sleep
import serve

RULIWEB_PAGE = 'http://bbs.ruliweb.com/community/board/300143/list?cate=497&page='
RULIWEB_VIEW = 'http://bbs.ruliweb.com/community/board/300143/read/' #+boardid

URL_SELECTOR = 'td.subject > div > a'
DATE_SELECTOR = 'td.time'
HITS_SELECTOR = 'td.hit'
COCNT_SELECTOR = 'span > span.num'
REC_SELECTOR = 'td.recomd'

INIT_PAGE = 1

def parseContent():
    print('ruliweb start!')
    total = 0
    insertValue = 0
    insertFail = 0
    updateValue = 0
    updateFail = 0    
    
    db = connDB.connDB()
    new = True
    page = INIT_PAGE
    
    while new:      
        rowList = getRowList(page)
        for row in rowList:    
            dateValue = getDateText(row)
            timeLimit = datetime.now() - timedelta(days=2)            
            if (dateValue - timeLimit).total_seconds() <= 0:
                new = False
                break

            total += 1
            
            bidValue = row.select_one(URL_SELECTOR)['href'].split('?')[0].split('/')[-1]            
            urlValue = RULIWEB_VIEW + bidValue
            titleValue = row.select_one(URL_SELECTOR).text
            
            hitsValue = row.select_one(HITS_SELECTOR).text.strip()
            cocntValue = getCocntText(row)
            recValue = getRecText(row)            
            
            if db.select(urlValue) == 0:               
                values = (bidValue, titleValue, dateValue, urlValue, hitsValue, cocntValue, recValue, 'c4')
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
    print('exit ruliweb!')    
    print('insert - success: {}, fail: {}'.format(insertValue, insertFail))
    print('update - success: {}, fail: {}'.format(updateValue, updateFail))
    print('total: {} cases'.format(total))
    print('=================================')    


def getRowList(page): 
    pageUrl = RULIWEB_PAGE + str(page)
    soup = serve.getSoup(pageUrl)
    rowList = soup.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['table_body'])  
    return rowList

def getDateText(row):
    dateText = row.select_one(DATE_SELECTOR).string.strip()
    
    if dateText.count('.') == 0:
        now = datetime.now()
        dateText = str(now.year) + '-' + '{:02d}'.format(now.month) + '-' + str(now.day) + ' ' + dateText
    else:
        dateText = dateText.replace('.', '-') + ' 00:00'
    
    return datetime.strptime(dateText, '%Y-%m-%d %H:%M')

def getCocntText(row):
    cocntTag = row.select_one(COCNT_SELECTOR)

    if cocntTag is not None:
        cocntText = cocntTag.string.strip()
    else:
        cocntText = '0'
    
    return cocntText

def getRecText(row):
    tag = row.select_one(REC_SELECTOR)
    
    if tag.string is not None:
        recText = tag.string.strip()
    else:
        recText = tag.select_one('span').string
    
    return recText

'''
if __name__ == "__main__":
    parseContent()
'''
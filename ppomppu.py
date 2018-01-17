import re
from selenium import webdriver
import bs4
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pymysql.cursors
import connDB
import serve
import datetime
PHANTOM_PATH = "C:\\phantomjs\\phantomjs.exe"
browser = webdriver.PhantomJS(PHANTOM_PATH)

def parseContent():
    # HTML 분석하기
    page = 0
    loop = True
    while loop:
        page += 1
        html = serve.getUrl('ppomppu', page)
        soup = BeautifulSoup(html, "html.parser")
        boardList = soup.find_all("tr", class_= re.compile(r'list0|list1'))

        for board in boardList :
            for child in board.descendants :     #얘는 자손 전부 들르는애
                if child.name == 'a' and child.attrs['href'] is not '#' :             #tag 명 갖고오는거
                    boardUrl = "http://www.ppomppu.co.kr/zboard/" + child.attrs['href']
                    browser.get(boardUrl)
                    html = browser.page_source
                    soup = BeautifulSoup(html, "html.parser")                

                    #원문링크
                    contentUrl = soup.select_one("#copyurl")
                    contentUrl = contentUrl.attrs['value']
                    
                    #제목
                    title = soup.select_one(".view_title2")
                    title = title.text  #text content string 중에 되는거 ㅋㅋㅋ
                    #날짜
                    date = soup.find(string = re.compile(r"\d\d\d\d[-]\d\d[-]\d\d"))
                    date = date.split(': ')[1].strip()
                    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
                    #본문
                    contents = soup.select_one(".board-contents")
                    content = ""
                    for cont_child in contents.descendants:
                        #img
                        if cont_child.name == 'img':
                            content += "http:" + cont_child.attrs['src'] + "\\"
                        #video
                        elif cont_child.name == 'iframe':
                            content += cont_child.attrs['src'] + "\\"
                        #text
                        elif type(cont_child) is bs4.element.NavigableString :
                            content += cont_child + "\\"        
                    #3일전 데이터만 검사
                    configDate = date.strftime('%Y-%m-%d')
                    if serve.date_compare(configDate) is False:
                        loop = False
                        break;

                    #db에 있는거면 조회수랑 댓글수 가져오기 
                    if not (connDB.select(contentUrl)):                        
                        connDB.insert(title, content, date, contentUrl, 'c2')
                    else :
                        try :
                            commentCnt = soup.select_one('.list_comment').text
                        except AttributeError as attrE:
                            commentCnt = 0
                        else :
                            commentCnt = int(commentCnt)
                        
                        hits = soup.find(string = re.compile(r"조회수: \d+")).strip()
                        hits = hits.split("/")[0].strip()
                        hits = hits.split(": ")[1].strip()    
                        connDB.update(hits, commentCnt, contentUrl)
                            
        if loop is False:
            break;



import re
from selenium import webdriver
import re
from selenium import webdriver
import bs4
from bs4 import BeautifulSoup
import pymysql.cursors
import connDB
import serve
import datetime
browser = webdriver.PhantomJS()

def parseContent():
    # HTML 분석하기
    page = -1
    loop = True
    while loop:
        page += 1
        url = serve.getUrl('humoruniv', page)
        soup = BeautifulSoup(url, "html.parser")
        boardList = soup.select('.li_sbj > a')

        for board in boardList :
            boardUrl = "http://web.humoruniv.com//board/humor/" + board.attrs['href']
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")

            #원문링크
            contentUrl = boardUrl
            #제목
            title = soup.select_one("#ai_cm_title")
            title = title.text  #text content string 중에 되는거 ㅋㅋㅋ
            #날짜
            date = soup.select_one("#if_date > span:nth-of-type(2)").text
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            #본문
            contents = soup.select_one("#cnts")
            content = ""
            for cont_child in contents.descendants:
                #img
                if cont_child.name == 'img':
                    content += cont_child.attrs['src'] + "\\"
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
                connDB.insert(title, content, date, contentUrl, 'c3')
            else :
                hits = soup.select_one('#content_info > span:nth-of-type(5)').text
                replyCnt = soup.find(string = re.compile(r"답글마당"))            
                replyCnt = re.sub('[^0-9]', '', replyCnt)
                connDB.update(hits, replyCnt, contentUrl)

        if loop is False:
            break


import re
from selenium import webdriver
import bs4
from bs4 import BeautifulSoup
import pymysql.cursors
import connDB
import serve
import datetime
PHANTOM_PATH = "C:\\phantomjs\\phantomjs.exe"
browser = webdriver.PhantomJS(PHANTOM_PATH)

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
            browser.get(boardUrl)
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")
            if not (connDB.select(boardUrl)):
                #원문링크
                contentUrl = boardUrl
                #제목
                title = soup.select_one("#ai_cm_title")
                title = title.text  #text content string 중에 되는거 ㅋㅋㅋ
                #날짜
                date = soup.select_one("#if_date > span:nth-of-type(2)").text
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                #3일전 데이터만 검사
                configDate = date.strftime('%Y-%m-%d')
                if serve.date_compare(configDate) is False:
                    loop = False
                    break;

                boardID = boardUrl.split('number=')[-1]
                
                file_path_arr = []
                file_name_arr = []
                #본문
                contents = soup.select_one("#cnts")
                content = ""
                for cont_child in contents.descendants:
                    #img
                    if cont_child.name == 'img':
                        if((cont_child.attrs['src']).startswith('https:') or (cont_child.attrs['src']).startswith('http:')):
                            attachFile = cont_child.attrs['src']    
                        else :
                            attachFile = "https:" + cont_child.attrs['src']
                        content += attachFile                                
                        file_path = 'file'+'/'+str(configDate) +'/'+ 'humoruniv' +'/'+ boardID
                        file_name = attachFile.split('/')[-1]
                        file_path = serve.save_file(attachFile, file_path, file_name)
                        file_name_arr.append(file_name)
                        file_path_arr.append(file_path)
                    #video
                    elif cont_child.name == 'iframe':
                        content += cont_child.attrs['src'] + "\\"
                    #text
                    elif type(cont_child) is bs4.element.NavigableString :
                        content += cont_child
                    content += "\\"

                last_insert_id = connDB.insert(title, content, date, contentUrl, 'c3')
                if (last_insert_id and file_name_arr):
                    for index, file in enumerate(file_name_arr):
                        print(file_name_arr[index], file_path_arr[index])
                        connDB.insertAttachFile(file_name_arr[index], file_path_arr[index], last_insert_id)
            #db에 있는거면 조회수랑 댓글수 가져오기 
            else :
                hits = soup.select_one('#content_info > span:nth-of-type(5)').text
                replyCnt = soup.find(string = re.compile(r"답글마당"))            
                replyCnt = re.sub('[^0-9]', '', replyCnt)
                connDB.update(hits, replyCnt, contentUrl)

        if loop is False:
            break


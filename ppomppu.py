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
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
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
                    link = child.attrs['href'].split('&')
                    boardUrl = "http://www.ppomppu.co.kr/zboard/" + link[0] +'&'+ link[3]
                    contentUrl = boardUrl
                    browser.get(boardUrl)
                    html = browser.page_source
                    soup = BeautifulSoup(html, "html.parser")   
                    
                    #날짜
                    date = soup.find(string = re.compile(r"\d\d\d\d[-]\d\d[-]\d\d"))
                    date = date.split(': ')[1].strip()
                    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
                    #3일전 데이터만 검사
                    configDate = date.strftime('%Y-%m-%d')
                    if serve.date_compare(configDate) is False:
                        loop = False
                        break;        
                    
                    if not (connDB.select(boardUrl)):
                        #원문링크
                        #contentUrl = soup.select_one("#copyurl")
                        #contentUrl = contentUrl.attrs['value']
                        contentUrl = boardUrl
                        #제목
                        title = soup.select_one(".view_title2")
                        title = title.text  #text content string 중에 되는거 ㅋㅋㅋ

                        boardID = boardUrl.split('no=')[-1]

                        file_path_arr = []
                        file_name_arr = []
                        #본문
                        contents = soup.select_one(".board-contents")
                        content = ""
                        for cont_child in contents.descendants:
                            #img
                            if cont_child.name == 'img':
                                if((cont_child.attrs['src']).startswith('https:') or (cont_child.attrs['src']).startswith('http:')):
                                    attachFile = cont_child.attrs['src']    
                                else :
                                    attachFile = "https:" + cont_child.attrs['src']
                                content += attachFile                                
                                file_path = 'file'+'/'+ 'c2' +'/'+ boardID
                                file_name = attachFile.split('/')[-1]
                                file_path = serve.save_file(attachFile, file_path, file_name)
                                file_name_arr.append(file_name)
                                file_path_arr.append(file_path)
                            #video
                            elif cont_child.name == 'iframe':
                                content += cont_child.attrs['src'] + "\\"
                            #audio
                            elif cont_child.name == 'audio':
                                pass
                            #text
                            elif type(cont_child) is bs4.element.NavigableString :
                                cont_child = emoji_pattern.sub(r'',cont_child)
                                content += cont_child
                            content += "\\"
                            
                        try :
                            commentCnt = soup.select_one('.list_comment').text
                        except AttributeError as attrE:
                            commentCnt = 0
                        else :
                            commentCnt = int(commentCnt)
                        
                        hits = soup.find(string = re.compile(r"조회수: \d+")).strip()
                        hits = hits.split("/")[0].strip()
                        hits = hits.split(": ")[1].strip()                            
                        last_insert_id = connDB.insert(boardID, title, content, date, contentUrl, hits, commentCnt, 'c2')
                        if (last_insert_id and file_name_arr):
                            for index, file in enumerate(file_name_arr):
                                connDB.insertAttachFile(file_name_arr[index], file_path_arr[index], last_insert_id)
                    else : #db에 있는거면 조회수랑 댓글수 가져오기 
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



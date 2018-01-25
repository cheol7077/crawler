import re
from selenium import webdriver
import bs4
from bs4 import BeautifulSoup
import pymysql.cursors
import connDB
import serve
import datetime
from extraction import noun
import time
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
    page = -1
    loop = True
    while loop:
        page += 1
        url = serve.getUrl('humoruniv', page)
        soup = BeautifulSoup(url, "html.parser")
        boardList = soup.select('.li_sbj > a')

        for board in boardList :
            start_time = time.time()
            boardUrl = "http://web.humoruniv.com//board/humor/" + board.attrs['href']
            browser.get(boardUrl)
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")
                  
            #날짜
            date = soup.select_one("#if_date > span:nth-of-type(2)").text.strip() #웃긴자료 = 베스트게시물 : 이동시간으로 비교
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            #3일전 데이터만 검사
            configDate = date.strftime('%Y-%m-%d')
            if serve.date_compare(configDate) is False:
                loop = False
                break;
            boardID = boardUrl.split('number=')[-1]
            if not (connDB.select(boardID)):
                #원문링크
                contentUrl = boardUrl
                #제목
                title = soup.select_one("#ai_cm_title")
                title = title.text  #text content string 중에 되는거 ㅋㅋㅋ
                text = title + ' '

                date = soup.select_one("#if_date > span:nth-of-type(1)").text.strip() #게시글 작성시간으로 최신순 정렬 
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                
                boardID = boardUrl.split('number=')[-1]
                
                file_path_arr = []
                file_name_arr = []
                #본문
                contents = soup.select_one("#wrap_copy")
                content = ""
                for cont_child in contents.descendants:
                    #img
                    if cont_child.name == 'img':
                        if((cont_child.attrs['src']).startswith('https:') or (cont_child.attrs['src']).startswith('http:')):
                            attachFile = cont_child.attrs['src']    
                        else :
                            attachFile = "https:" + cont_child.attrs['src']
                        content += attachFile                                
                        file_path = 'file'+'/'+'c3' +'/'+ boardID
                        file_name = attachFile.split('/')[-1]
                        file_path = serve.save_file(attachFile, file_path, file_name)
                        file_name_arr.append(file_name)
                        file_path_arr.append(file_path)
                    #video
                    elif cont_child.name == 'iframe':
                        content += cont_child.attrs['src']
                    #audio
                    elif cont_child.name == 'audio':
                        pass
                    #except_text 태그 잘못 걸리면 빠져나와야함
                    elif cont_child.name == 'div':
                        if(cont_child.attrs['id'] == 'wrap_up_down'):
                           break
                    #text
                    elif type(cont_child) is bs4.element.NavigableString :
                        cont_child = emoji_pattern.sub(r'',cont_child)
                        if 'var mp3str' in cont_child:
                           continue
                        content += cont_child
                        text += cont_child + ' '
                    content += "\\"
                hits = soup.select_one('#content_info > span:nth-of-type(5)').text
                if ',' in hits:
                    hits = hits.replace(',','')
                commentCnt = soup.find(string = re.compile(r"답글마당"))            
                commentCnt = re.sub('[^0-9]', '', commentCnt)
                
                keywords = noun(text)
                last_insert_id = connDB.insert(boardID, title, content, date, contentUrl, hits, commentCnt, 'c3', keywords)
                if (last_insert_id and file_name_arr):
                    for index, file in enumerate(file_name_arr):
                        connDB.insertAttachFile(file_name_arr[index], file_path_arr[index], last_insert_id)
            #db에 있는거면 조회수랑 댓글수 가져오기 
            else :
                hits = soup.select_one('#content_info > span:nth-of-type(5)').text
                if ',' in hits:
                    hits = hits.replace(',','')
                commentCnt = soup.find(string = re.compile(r"답글마당"))            
                commentCnt = re.sub('[^0-9]', '', commentCnt)
                connDB.update(hits, commentCnt, boardID)
            end_time = time.time()
            print('웃대: {}'.format(end_time - start_time))        
        if loop is False:
            break


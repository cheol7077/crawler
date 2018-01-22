# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import bs4
import urllib.parse as parse
import urllib.request as req
import time
import serve
import connDB
import datetime

EXCEPTION = "Video 태그를 지원하지 않는 브라우저입니다."
BASE_URL = "http://www.fmkorea.com/"
HUMOR_URL = BASE_URL+"index.php?mid=humor"
LINK_LIST = "#bd_486616_0 > div > table > tbody > tr > td.title > a:nth-of-type(1)"
CONTENT = "#bd_capture > div.rd_body.clear > article > div"
DATE = "#bd_capture > div.rd_hd.clear > div.board.clear > div.top_area.ngeb > span"
HITS = '#bd_capture > div.rd_hd.clear > div.board.clear > div.btm_area.clear > div.side.fr > span:nth-of-type(1) > b'
COMMENTCNT = '#bd_capture > div.rd_hd.clear > div.board.clear > div.btm_area.clear > div.side.fr > span:nth-of-type(3) > b'
def parseContent():
    page = 0
    loop = True
    lastCont = ''
    while loop:
        page += 1

        html = serve.getUrl('fmkorea', page)
        soup = BeautifulSoup(html, "html.parser")
        titles = soup.select(LINK_LIST)

        for title in titles:
            if title.string is not None:
                title_value = title.string
                link_value = BASE_URL + title.attrs['href']
                content_value = ""
                html = req.urlopen(link_value)
                soup = BeautifulSoup(html, "html.parser")

                date = soup.select_one(DATE)
                date_value = date.string.replace('.', '-')
                date_value = datetime.datetime.strptime(date_value, '%Y-%m-%d %H:%M')
                configDate = date_value.strftime('%Y-%m-%d')

                #3일전 데이터만 검사
                if serve.date_compare(configDate) is False:
                    loop = False
                    break;

                if not (connDB.select(link_value)):
                    boardID = soup.select_one('.document_address > .a').attrs['href']
                    contents = soup.select(CONTENT)

                    file_path_arr = []
                    file_name_arr = []
                    for content in contents:
                        for child in content.descendants:
                            if child.name == 'img' or child.name == 'source':
                                if((child.attrs['src']).startswith('https:') or (child.attrs['src']).startswith('http:')):
                                    attachFile = child.attrs['src']
#                                elif ((child.attrs['src']).startswith('//getfile'):
                                
                                else :
                                    attachFile = "https:" + child.attrs['src']
                                content_value += attachFile                                
                                file_path = 'file'+'/'+str(configDate) +'/'+ 'fmkorea' +boardID
                                file_name = attachFile.split('/')[-1]
                                if(file_name == 'transparent.gif'):
                                    pass
                                else:
                                    file_path = serve.save_file(attachFile, file_path, file_name)
                                    file_name_arr.append(file_name)
                                    file_path_arr.append(file_path) 
                            elif child.name == 'iframe':
                                content_value += child.attrs['src']
                            elif type(child) is bs4.element.NavigableString and child != EXCEPTION:
                                content_value += child
                            content_value += "\\"
                    hits = soup.select(HITS)
                    commentCnt = soup.select(COMMENTCNT)
                    hits = hits[0].text
                    commentCnt = commentCnt[0].text
                #이거
                    connDB.insert(boardID, title_value, content_value, date_value, link_value, hits, commentCnt, 'c1')
                    if (last_insert_id and file_name_arr):
                        for index, file in enumerate(file_name_arr):                            
                            print(file_name_arr[index], file_path_arr[index])
                            connDB.insertAttachFile(file_name_arr[index], file_path_arr[index], boardID)
                
                else : #db에 있는거면 조회수랑 댓글수 가져오기     
                    hits = soup.select(HITS)
                    commentCnt = soup.select(COMMENTCNT)
                    hits = hits[0].text
                    commentCnt = commentCnt[0].text
                    connDB.update(hits, commentCnt, link_value)

                time.sleep(1)

        if loop is False:
            break


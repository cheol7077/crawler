import time
import urllib.request
from bs4 import BeautifulSoup
import pymysql.cursors
import connDB
import serve
import datetime
import urllib.request as req
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
def parseContent():
    page = 0
    loop = True
    while loop:
        page += 1
        html = serve.getUrl('ruliweb', page)
        soup = BeautifulSoup(html, "html.parser")
        for i in range(0, 29): 
            time.sleep(2)
            title = str(soup.select(".table_body div a")[i].text.strip())
            link = soup.select(".table_body div a")[i]
            url_article = str(link.attrs["href"])
            url_article = url_article.split('?')[0]
            hits = soup.select(".hit")[i+3].text.strip()
            replyCnt = str(soup.select(".num_reply")[i].text)
            replyCnt = replyCnt.replace("(", "")
            replyCnt = replyCnt.replace(")", "")
            date = soup.select('.time')[i+3].text.strip()
            date = date.replace(".","-")
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
                configDate = date.strftime('%Y-%m-%d')
            except ValueError as e:
                pass
            else:
                if serve.date_compare(configDate) is False:
                    loop = False
                    break;
            if not (connDB.select(url_article)):
                r = req.Request(url_article, headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
                response = req.urlopen(r)
                soup_article = BeautifulSoup(response, "html.parser")
                contents = soup_article.select_one(".view_content")
                content = ""
                
                time = soup_article.select_one(".regdate").text
                time = time.replace(".","-")
                gdate = time.replace("(","")
                gdate = gdate[0:16]

                gdate = datetime.datetime.strptime(gdate, '%Y-%m-%d %H:%M')
                configDate = gdate.strftime('%Y-%m-%d')

                boardID = url_article.split('/')[-1]
                boardID = boardID.replace('?','')
                file_path_arr = []
                file_name_arr = []

                for item in contents.descendants:
                    if item.name == "img" :
                        if((item.attrs['src']).startswith('https:') or (item.attrs['src']).startswith('http:')):
                            attachFile = item.attrs['src']    
                        else :
                            attachFile = "https:" + item.attrs['src']
                        content += attachFile                                
                        file_path = 'file'+'/'+ 'c4' +'/'+ boardID
                        file_name = attachFile.split('/')[-1]
                        file_path = serve.save_file(attachFile, file_path, file_name)
                        file_name_arr.append(file_name)
                        file_path_arr.append(file_path)
                    elif item.name == "p" :
                        if item.string is not None : 
                            cont = emoji_pattern.sub(r'',item.string)
                            content += cont 
                    #audio
                    elif cont_child.name == 'audio':
                        pass
                    elif item.name == "iframe":
                        content += item.attrs['src']
                    content += '\\'

                last_insert_id = connDB.insert(boardID, title, content, gdate, url_article, hits, replyCnt,'c4')
                if (last_insert_id and file_name_arr):
                    for index, file in enumerate(file_name_arr):
                        connDB.insertAttachFile(file_name_arr[index], file_path_arr[index], last_insert_id)
                        
            else :
                hits =soup.select(".hit")[i+3].text
                replyCnt = str(soup.select(".num_reply")[i].text)
                replyCnt = replyCnt.replace("(", "")
                replyCnt = replyCnt.replace(")", "")
                connDB.update(hits, replyCnt, url_article)
      
        if loop is False:
            break

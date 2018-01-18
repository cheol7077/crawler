import time
import urllib.request
from bs4 import BeautifulSoup
import pymysql.cursors
import connDB
import serve
import datetime


def parseContent():
    page = 0
    loop = True
    while loop:
        page += 1
        html = serve.getUrl('ruliweb', page)
        soup = BeautifulSoup(html, "html.parser")
        for i in range(0, 29): 
            title = str(soup.select(".table_body div a")[i].text.strip())
            link = soup.select(".table_body div a")[i]
            url_article = str(link.attrs["href"])
            url_article = url_article.split('?')[0]
            hits = soup.select(".hit")[i+3].text.strip()
            replyCnt = str(soup.select(".num_reply")[i].text)
            replyCnt = replyCnt.replace("(", "")
            replyCnt = replyCnt.replace(")", "")
            date = soup.select('.time')[i+3].text.strip()
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
                configDate = date.strftime('%Y-%m-%d')
            except ValueError as e:
                pass
            else:
                if serve.date_compare(configDate) is False:
                    loop = False
                    break;
            if not (connDB.select(url_article)):
                response = urllib.request.urlopen(url_article)
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
                        file_path = 'file'+'/'+str(configDate) +'/'+ 'ruliweb' +'/'+ boardID
                        file_name = attachFile.split('/')[-1]
                        file_path = serve.save_file(attachFile, file_path, file_name)
                        file_name_arr.append(file_name)
                        file_path_arr.append(file_path)
                    elif item.name == "p" :
                        if item.string is not None : 
                            content += item.string 
                    elif item.name == "iframe":
                        content += item.attrs['src']
                    content += '\\'

                last_insert_id = connDB.insert(title, content, gdate, url_article, hits, replyCnt,'c4')
                if (last_insert_id and file_name_arr):
                    for index, file in enumerate(file_name_arr):
                        print(file_name_arr[index], file_path_arr[index])
                        connDB.insertAttachFile(file_name_arr[index], file_path_arr[index], last_insert_id)

            else :
                hits =soup.select(".hit")[i+3].text
                replyCnt = str(soup.select(".num_reply")[i].text)
                replyCnt = replyCnt.replace("(", "")
                replyCnt = replyCnt.replace(")", "")
                connDB.update(hits, replyCnt, url_article)

            #time.sleep(1)
        if loop is False:
            break
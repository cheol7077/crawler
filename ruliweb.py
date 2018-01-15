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
                    print("title : " + title)
                    link = soup.select(".table_body div a")[i]
                    url_article = str(link.attrs["href"])
                    print("url_article" + url_article)
                    hits = soup.select(".hit")[i+3].text
                    print("hits = " +str(hits).strip())
                    replyCnt = str(soup.select(".num_reply")[i].text)
                    replyCnt = replyCnt.replace("(", "")
                    replyCnt = replyCnt.replace(")", "")
                    print("reply : " + replyCnt)
                    
                    response = urllib.request.urlopen(url_article)
                    soup_article = BeautifulSoup(response, "html.parser")
                    contents = soup_article.select_one(".view_content")
                    content = ""
                    
                    time = soup_article.select_one(".regdate").text
                    time = time.replace(".","-")
                    gdate = time.replace("(","")
                    gdate = gdate[0:16]
                    print(gdate)
                    gdate = datetime.datetime.strptime(gdate, '%Y-%m-%d %H:%M')
                    print("변경후 : " + str(gdate))
                    configDate = gdate.strftime('%Y-%m-%d')
                    print("configDate = " +str(gdate))
                    for item in contents.descendants:
                     
                     if item.name == "img" :
                             print(item.attrs['src'])
                             content += item.attrs['src'] +"\\"
                     elif item.name == "p" :
                            if item.string is not None : 
                                 print(item.string) 
                                 content += item.string +"\\"
                     elif item.name == "iframe":
                            print(item.attrs['src'])
                            content += item.attrs['src'] +"\\"
            
                    if serve.date_compare(configDate) is False:
                        loop = False
                        break;
                            
                    if not (connDB.select(url_article)):
                                connDB.insert(title, content, gdate, url_article, 'c4')
                    else :    
                                hits =soup.select(".hit")[i+3].text
                                replyCnt = str(soup.select(".num_reply")[i].text)
                                replyCnt = replyCnt.replace("(", "")
                                replyCnt = replyCnt.replace(")", "")
                                connDB.update(hits, replyCnt, url_article)
            
            #time.sleep(1)
        if loop is False:
                break
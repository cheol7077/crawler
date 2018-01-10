# -*- coding:utf-8 -*-
import pymysql.cursors

''' 테이블 생성문
conn = pymysql.connect(
    host='localhost',    
    user='root',
    passwd='hubhub',
    db='community',
    charset='utf8mb4')

cursor = conn.cursor()
cursor.execute("DROP TABLE commu")
sql = '
    CREATE TABLE commu (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        title TEXT,
        content LONGTEXT,
        date date,
        url TEXT, 
        hits int,
        replyCnt int,
        commuID TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
'
cursor.execute(sql)

크롤링 사이트 목록
CREATE TABLE commuID (
        id text
        communityName text
        baseUrl        
)
'''
def insert (title, content, date, url, commuID) :
    conn = pymysql.connect(host='localhost',
        user = 'root',
        password = 'hubhub',
        db='community',
        charset='utf8mb4')
    
    with conn.cursor() as cursor:

        sql = '''INSERT INTO commu (title, content, date, url, hits, replyCnt, commuID)
                    VALUES (%s, %s, %s, %s, null, null, %s)'''
        cursor.execute(sql, (title, content, date, url, commuID))
        conn.commit()        
        conn.close()

def update (hits, replyCnt, conturl) :
    conn = pymysql.connect(host='localhost',
        user = 'root',
        password = 'hubhub',
        db='community',
        charset='utf8mb4')
    
    with conn.cursor() as cursor:

        sql = '''UPDATE commu SET hits=%s, replyCnt=%s where url=%s'''
        cursor.execute(sql, (int(hits), int(replyCnt), conturl))
        conn.commit()        
        conn.close()

#selectdDB
def select (conturl) :
    conn = pymysql.connect(host='localhost',
        user = 'root',
        password = 'hubhub',
        db='community',
        charset='utf8mb4')
    
    with conn.cursor() as cursor:
        sql = '''SELECT url from commu where url = %s'''
        cursor.execute(sql, (conturl))
        result = cursor.fetchall()
        conn.close()
        return result;


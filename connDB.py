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
        date datetime,
        url TEXT, 
        hits int,
        commentCnt int,
        communityID TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
'
cursor.execute(sql)

크롤링 사이트 목록
CREATE TABLE communityID (
        id text
        communityName text
        baseUrl        
)

#이미지 저장db
sql = '
     CREATE TABLE attachFile (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        file_name TEXT,
        path TEXT,
        commu_id_fk integer,
        foreign KEY (commu_id_fk) REFERENCES commu(id)
            ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'
'''
def insert (title, content, date, url, communityID) :
    conn = pymysql.connect(host='localhost',
        user = 'root',
        password = 'hubhub',
        db='community',
        charset='utf8mb4')
    
    with conn.cursor() as cursor:

        sql = '''INSERT INTO commu (title, content, date, url, hits, commentCnt, communityID)
                    VALUES (%s, %s, %s, %s, null, null, %s)'''
        cursor.execute(sql, (title, content, date, url, communityID))
        conn.commit()
        last_insert_id = cursor.lastrowid    
        conn.close()
        return last_insert_id

def update (hits, commentCnt, conturl) :
    conn = pymysql.connect(host='localhost',
        user = 'root',
        password = 'hubhub',
        db='community',
        charset='utf8mb4')
    
    with conn.cursor() as cursor:

        sql = '''UPDATE commu SET hits=%s, commentCnt=%s where url=%s'''
        cursor.execute(sql, (int(hits), int(commentCnt), conturl))
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

def insertAttachFile(file_name, file_path, commu_id) :
    conn = pymysql.connect(host='localhost',
        user = 'root',
        password = 'hubhub',
        db='community',
        charset='utf8mb4')

    with conn.cursor() as cursor:
        sql = '''INSERT INTO attachFile (file_name, path, commu_id_fk)
                    VALUES (%s, %s, %s)'''
        cursor.execute(sql, (file_name, file_path, commu_id))
        conn.commit()
        conn.close()



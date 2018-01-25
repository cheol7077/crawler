# -*- coding:utf-8 -*-
import pymysql.cursors

def insert (boardID, title, content, date, url, hits, commentCnt, communityID, keywords) :
    conn = pymysql.connect(host='localhost',
        user = 'root',
        password = 'hubhub',
        db='community',
        charset='utf8mb4')
    
    with conn.cursor() as cursor:

        sql = '''INSERT INTO board (boardID, title, content, date, url, hits, commentCnt, communityID, keywords)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(sql, (boardID, title, content, date, url, hits, commentCnt, communityID, keywords))
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

        sql = '''UPDATE board SET hits=%s, commentCnt=%s where url=%s'''
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
        sql = '''SELECT url from board where url = %s'''
        cursor.execute(sql, (conturl))
        result = cursor.fetchall()
        conn.close()
        return result;

def insertAttachFile(file_name, file_path, board_id) :
    conn = pymysql.connect(host='localhost',
        user = 'root',
        password = 'hubhub',
        db='community',
        charset='utf8mb4')

    with conn.cursor() as cursor:
        sql = '''INSERT INTO attachFile (file_name, path, board_id_fk)
                    VALUES (%s, %s, %s)'''
        cursor.execute(sql, (file_name, file_path, board_id))
        conn.commit()
        conn.close()


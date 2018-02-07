# -*- coding:utf-8 -*-
import pymysql

class connDB:    
    def __init__(self):    
        self.conn = pymysql.connect(host='localhost',
                    user = 'root',
                    password = 'hubhub',
                    db='community',
                    charset='utf8mb4')
        self.cursor = self.conn.cursor()
        
    def __del__(self): #객체 소멸시 하는일
        self.cursor.close()
        self.conn.close()
        print('DB connection is closed')

    def insert (self, values) : #bid, title, keywords, date, url, hits, cocnt, rec, cid
        try:
            sql = '''INSERT INTO board (bid, title, date, url, hits, cocnt, rec, cid)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            result = self.cursor.execute(sql, values)
            self.conn.commit()                
        except Exception as e:
            print('insert err: '+e)  
            result = 0   
        return result        

    def update (self, values) : #hits, cocnt, rec, url
        try:
            sql = '''UPDATE board SET hits=%s, cocnt=%s, rec=%s where url=%s'''
            result = self.cursor.execute(sql, values)
            self.conn.commit()                
        except Exception as e:
            print('update err: '+e)  
            result = 0   
        return result  

    def select (self, values) :
        sql = '''SELECT url from board where url = %s'''
        self.cursor.execute(sql, values)
        result = self.cursor.rowcount                
        return result



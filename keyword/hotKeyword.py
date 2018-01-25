import pymysql
import math
''
ABBREVIATION = ['것', '나', '사람', '등', '때', '년', '말', '일', '때문', '문제', '사회', '중', '씨', '지금', '속', '하나', '집',
                '월', '데', '자신', '경우', '명', '생각', '시간', '그녀', '앞', '번', '여자', '개', '전', '사실', '점', '정도', '원', '소리', '애', '정말', '시', '고', '위해', '강',
                '모두', '새끼', '를', '분', '몸', '그냥', '뒤', '어', '여성', '함', '수', '뭐', '또', '그', '거', '회']

def connect():
    conn = pymysql.connect(host='localhost', 
                           user='root',
                           password='hubhub',
                           db='community',
                           charset='utf8mb4')
    
    return conn

def wordCount(cur):
    word_total = {}
    
    sql = """SELECT keywords
                FROM board"""
    cur.execute(sql)
    for row in cur.fetchall():
        words = row[0].split(',')
        for word in words:
            if word != '' and not (word in ABBREVIATION):
                if not (word in word_total):
                    word_total[word] = 0
                word_total[word] += 1
                
    keys = sorted(word_total.items(), key=lambda x:x[1], reverse=True)
    
    return keys

def perDay(cur):
    sql = """SELECT date_format(date, "%Y-%c-%d"), count(*)
                FROM board
                GROUP BY day(date)"""
    cur.execute(sql)
    
    D = cur.fetchall()
    return D
    
def numberOfPosts(cur):
    sql = """SELECT count(*)
                FROM board"""
    cur.execute(sql)   
    total =  cur.fetchall()
    return total[0][0]

def amountOfDay(cur, day):
    sql = """SELECT count(*)
                FROM board
                WHERE date_format(date, '%%Y-%%c-%%d') = %s"""
    cur.execute(sql, day)
    
    return cur.fetchall()

def theWordOfTheDay(cur, day, px_dic):
    word_day = {}

    sql = """SELECT keywords
                FROM board
                WHERE date_format(date, '%%Y-%%c-%%d') = %s"""
    cur.execute(sql, day)
    
    for row in cur.fetchall():
        words = row[0].split(',')
        for word in words:
            if word != '':
                if word in px_dic:
                    if word in word_day:
                        word_day[word] += 1
                    else:
                        word_day[word] = 1
                            
    return word_day

if __name__ == '__main__':
    conn = connect()
    cur = conn.cursor()
    
    px_dic = {}
    py_dic = {}
    pxy_dic = {}
    ixy_dic = {}
    word_avg = {}
    result_dic = {}
    result_val = {}
    
    keys = wordCount(cur)
    T = numberOfPosts(cur)
    for word, count in keys[:70]:
        px_dic[word] = count/T
    
    #print(px_dic)
    pd = perDay(cur)
    
    for day in pd:
        aod = amountOfDay(cur, day[0])
        for count in aod:
            py_dic[day[0]] = count[0]/T
    #print(py_dic)
    
    for day in py_dic:     
        wtList = theWordOfTheDay(cur, day, px_dic)
        wtList = sorted(wtList.items(), key=lambda x:x[1], reverse=True)   
        word_dic = {}
        for wt in wtList:
            word_dic[wt[0]] = wt[1]/T
        pxy_dic[day] = word_dic
    
    #print(pxy_dic)

    for date in pxy_dic:
        ixy_val = {}
        for word in pxy_dic[date]:
            ixy_val[word] = math.log10(pxy_dic[date][word]/(py_dic[date]*px_dic[word]))
        ixy_dic[date] = ixy_val
    
    #print(ixy_dic)
    cnt = 0
    sum = 0
    
    for word in px_dic:
        for date in ixy_dic:
            if word in ixy_dic[date]:
                cnt += 1
                sum += ixy_dic[date][word]
        word_avg[word] = sum/cnt
    
    for date in ixy_dic:
        
        result_val = {}
        for word in ixy_dic[date]:
            result_val[word] = ixy_dic[date][word] - word_avg[word]
        
        result_val = sorted(result_val.items(), key=lambda x:x[1], reverse=True)
        result_dic[date] = result_val
    
    for date in result_dic:
        print(date)
        for word in result_dic[date]:
            if word[1] > 0:
                print(word)
    conn.close()
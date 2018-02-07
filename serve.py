# -*- coding:utf-8 -*-
import time
import multiprocessing
from multiprocessing import Pool
from crawler import fmkorea, ppomppu, humoruniv, ruliweb, mlbpark

header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
sites =  ('fmkorea', 'ppomppu', 'humoruniv', 'ruliweb', 'mlbpark')

def crawl(site): # 예외가 있으면 알리고 계속해야지 멈추면 안됨.. log 필요성
    start_time = time.time()
    #print('start ' +site+ ' crawl : ', time.ctime())
    try:
        eval(site).parseContent()
    except Exception as e:
        print('except from {} '.format(site))
        print(e)
    finally:
        end_time = time.time()
        print('실행시간: {}'.format(end_time - start_time))
    return site

#크롤링 실행
if __name__ == "__main__":    
    with Pool(processes = len(sites)) as p:
        fsites = [p.apply_async(crawl, (site,)) for site in sites]
        for fsite  in fsites:
            try:
                print('finish ' +fsite.get(timeout=7200)+ ' : ', time.ctime())
            except multiprocessing.TimeoutError:
                print ('Failed at:', fsite.get())
                continue           
        p.close()
        p.join()
              
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup, UnicodeDammit
import urllib.request as req
header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}


def getSoup (page_url):    
    try:
        r = req.Request(page_url, headers = header)
        html = req.urlopen(r).read()
        charset = UnicodeDammit(html).original_encoding
        soup = BeautifulSoup(html, "lxml", from_encoding=charset)
        return soup
    except Exception as e:
        print('page error : {}, error message : {}'.format(page_url, e))
        return None
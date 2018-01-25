# -*- coding:utf-8 -*-
from konlpy.tag import Twitter

def noun(text):
    twitter = Twitter()
    result = ''
        
    malist = twitter.pos(text)
        
    for i, word in enumerate(malist):
        if word[1] == 'Noun':
            if i != len(malist)-1:
                result += word[0] + ','
            else:
                result += word[0]
                    
    return result
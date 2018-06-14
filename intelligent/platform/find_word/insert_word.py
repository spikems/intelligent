# coding:utf-8
import pymysql
import os
import traceback
import logging

logging.basicConfig(level=logging.INFO)
dir_path = os.path.dirname(os.path.abspath(__file__))
conn = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='cognitive_phrases',
                       charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)
"""
1:属性词表  2:评价词表
"""
def insert_run(tablename, industry, words):
    lword = words.split('#')
    dupword = []
    alword = []
    for word in lword:
        try:
            if tablename == 1:
                cur.execute('insert into attribute(word,industry_id) values(%s,%s) ', (word.strip(), industry))
                conn.commit()
            elif tablename == 2:
                cur.execute('insert into evaluation(evaluation,industry_id) values(%s,%s)', (word.strip(), industry))
                conn.commit()
            logging.info(' insert %s is successful' % word)
            alword.append(word)
        except:
            dupword.append(word)
            logging.info('%s is duplicate' % word)
    return alword, dupword

if __name__ == '__main__':
    tablename = 1
    industry = 1
    words = '试色#色泽#膏体#上妆#状态#品质#涂抹#纯度#版型#皮质#修复#配方'
    insert_run(tablename, industry, words)

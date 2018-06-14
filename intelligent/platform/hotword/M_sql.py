#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import pymysql
import logging
import traceback
reload(sys)
conn = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='cognitive_phrases',
                   charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)
sys.setdefaultencoding('utf-8')

class mysqls(object):

    def __init__(self,):
        pass

    def alter_table(self, sql,Flag=False):
        logging.info(sql)
        if not Flag:
            cur.execute(sql)
            conn.commit()
        else:
            cur.execute(sql,Flag)
            conn.commit()

    def read_product(self,brand,industry):
        cur.execute("select * from product where industry=%s and brand =%s",(int(industry),brand))
        conn.commit
        return cur.fetchall()

    def read_brands(self,industry):
        cur.execute("select *  from brands where industry=%s",int(industry))
        conn.commit()
        return cur.fetchall()

    def read_component(self,industry):
        cur.execute("select component from component where industry_id=%s",int(industry))
        conn.commit()
        return cur.fetchall()

    def read_category(self,industry):
        cur.execute('select * from category where industry=%s',int(industry))
        conn.commit()
        return cur.fetchall()

    def read_attr(self,industry):
        #属性词
        cur.execute('select * from attribute where industry_id in (0,%s)',int(industry))
        return cur.fetchall()

    def read_evalue(self,industry):
        cur.execute('select * from evaluation where industry_id in (0,%s)',int(industry))
        return cur.fetchall()

    def read_phrase(self,industry):
        cur.execute('select * from phrase')
        return cur.fetchall()

    def read_syn(self,):
        cur.execute('select * from sysnonyms')
        return cur.fetchall()

if __name__ == "__main__":
    ins = mysqls()
    result = ins.read_phrase()
    print result
    # sql = 'select brands_name from brands where industry ;'
    # attword, opinionword, AP_phrase,sysn =ins.run('大众',1)

    # for i,j in result.items():
    #     print i,j

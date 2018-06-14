#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import pymysql
import logging
import traceback
reload(sys)
conn = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='cognitive_phrases',
                   charset='utf8')
cur = conn.cursor()
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

    def read_table(self, sql):
        logging.info(sql)
        cur.execute(sql)
        conn.commit()
        return cur.fetchall()

if __name__ == "__main__":
    ins = mysqls()
    attword, opinionword, AP_phrase,sysn =ins.run('大众',1)

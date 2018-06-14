#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import pymysql
import logging
import traceback
reload(sys)
conn = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='cognitive_phrases',
                   charset='utf8')

connbase = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='dm_base',
                   charset='utf8')

curbase = connbase.cursor()
cur = conn.cursor()
sys.setdefaultencoding('utf-8')

class mysqls(object):

    def __init__(self,):
        pass

    # 取出与品牌不对应的词
    def ambiguous(self,moniterword):
        ambiguous_word = set()
        curbase.execute('select brands_name from brands')
        connbase.commit()
        result = curbase.fetchall()
        for sub in result:
            brand = sub[0].encode('utf-8', 'ignore').strip().upper()
            if brand != moniterword:
                # ambiguous_word.add(product)
                ambiguous_word.add(brand)
        return ambiguous_word

    def alter_table(self, sql,Flag=False):
        if not Flag:
            cur.execute(sql)
            conn.commit()
        else:
            cur.execute(sql,Flag)
            conn.commit()

    def read_table(self, sql):
        cur.execute(sql)
        conn.commit()
        return cur.fetchall()

    def read_category(self,industry):
        cur.execute('select category,sysnonyms from category where industry =%s',industry)
        conn.commit()
        return cur.fetchall()

    def read_attr(self,industry_id):
        #属性词
        cur.execute('select word,sysnonyms from attribute where industry_id in (0,%s)', industry_id)
        return cur.fetchall()

    def read_evalue(self,industry_id):
        cur.execute('select evaluation,sysnonyms from evaluation where industry_id in (0,%s)',industry_id)
        return cur.fetchall()

    def run(self,moniterword,industry_id):
        sysn_dict = {}  # word===>sysnon
        attword = []
        AP_phrase = []
        opinionword = []
        attword.append(moniterword)
        for wgroup  in self.read_category(industry_id):
            value ,keys = wgroup
            attword.append(value.encode('utf-8'))
            for w in keys.split('|'):
                if w:
                    sysn_dict[w.encode('utf-8')]=value.encode('utf-8')
        for group in self.read_attr(industry_id):
            att,sysn =group
            attword.append(att.encode('utf-8'))
            if sysn :
                for w in sysn.split('|'):
                    sysn_dict[w.encode('utf-8')]=att.encode('utf-8')

        for group in self.read_evalue(industry_id):
            opi,sysn =group
            opinionword.append(opi.encode('utf-8'))
            if sysn :
                for w in sysn.split('|'):
                    sysn_dict[w.encode('utf-8')]=opi.encode('utf-8')
        for att in attword:
            for opi in opinionword:
                AP_phrase.append(att+opi)

        sql = 'select phrase from phrase where industry_ids in (0,%s)'%industry_id
        for group in self.read_table(sql):
            AP_phrase.append(group[0])

        return attword,opinionword,AP_phrase,sysn_dict

if __name__ == "__main__":
    ins = mysqls()
    # sql = 'select brands_name from brands where industry ;'
    attword, opinionword, AP_phrase,sysn =ins.run('大众',1)
    print attword[:2]
    print opinionword[:2]
    print AP_phrase[:2]
    print sysn.items()[:2]
    # for i,j in result.items():
    #     print i,j

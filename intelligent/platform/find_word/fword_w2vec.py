# usr/bin/env python
# -*- coding:utf-8 -*-
'''
use word2veb expand  special word
'''
import logging
import gensim
import os, sys
import traceback
import pymysql


dir_path = os.path.dirname(os.path.abspath(__file__))
conn = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='cognitive_phrases',
                       charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)

#单例模式
def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class Word2vecFindw(object):
    def __init__(self,):
        self.model = gensim.models.Word2Vec.load("%s/model/mz.model"%dir_path)
    def run(self,word,typeid=2,is_dup=False):
        word = word.decode('utf-8','ignore')
        try:
            result = [i[0].encode('utf-8', 'ignore') for i in self.model.most_similar(word,topn=50)]
            if is_dup:  # 去除重复
                al_word = self.sql_select(typeid)
                filter_result = [i for i in result if i not in al_word]
                self.sql_insert(result,typeid)
                return filter_result
            return result
        except:
            traceback.print_exc()
            return False


    # 导入重复数据
    def sql_insert(self,lword,typeid):
        typeid = int(typeid)
        for w in lword:
            try:
                cur.execute('insert into dupword(word,species) values(%s,%s) ', (w,typeid))
                conn.commit()
            except:
                traceback.print_exc()


    # 读取重复数据
    def sql_select(self,typeid):
        typeid = int(typeid)
        already_word = []
        sql = 'select word from dupword where species=%s'%typeid
        try:
            cur.execute(sql)
            conn.commit()
            for sub in cur.fetchall():
                already_word.append(sub['word'].strip().encode('utf-8', 'ignore'))
            return already_word
        except:
            traceback.print_exc()


if __name__ == '__main__':
    word = '兰蔻'
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    if not word:
        logging.error('word not find,quit')
        sys.exit(1)
    ins = Word2vecFindw()
    result = ins.run(word,is_dup=True)
    for word in result:
        print word

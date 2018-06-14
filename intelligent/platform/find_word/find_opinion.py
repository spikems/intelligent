#!/usr/bin/python
#-*- coding:utf-8 -*-
"""
A FIND OPINION WORD APPLICATION
"""

import sys
import os
import re
import jieba
import pymysql
import heapq
from pyltp import Postagger
from pyltp import Parser
from jieba.norm import norm_cut
from collections import Counter
from optparse import OptionParser
dir_path = os.path.dirname(os.path.abspath(__file__))
jieba.load_userdict("%s/conf/jieba_lexicon" % dir_path)
from intelligent.platform.find_word.t_cognition import mysqls
from intelligent.platform.find_word.conf.setting import *
from intelligent.platform.find_word.MakeSentence import MakeSentence
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
LTP_DATA_DIR = '%s/../hotword/ltp_data' % dir_path  # ltp模型目录的路径
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`

# logger = logging.getLogger(__name__)
conn = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='cognitive_phrases',
                       charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)

def read_opinion(industry):
    opinionword = set()
    cur.execute('select evaluation from evaluation where industry_id in (0,%s)',(industry,))
    conn.commit()
    for word in cur.fetchall():
        w = word['evaluation'].encode('utf-8','ignore').strip()
        opinionword.add(w)
    logger.info( 'how many opinion word :%s'%len(opinionword))
    return opinionword

class Opinion(object):
    def __init__(self,Dsent, industry_id):
        self.industry_id = industry_id
        self.Dsent = Dsent
        self.postagger = Postagger()  # 初始化实例
        self.postagger.load_with_lexicon(pos_model_path, '%s/conf/posttags.txt' % dir_path)
        self.sql = mysqls()
        self.opinionword = read_opinion(self.industry_id)
        self.n_v = []


    def cut_word(self, sents):
        # 分词
        words = [i.encode('utf-8', 'ignore') for i in norm_cut(sents)]  # HMM=False
        return words


    def word_sex(self, ):
        # 获取词性
        postags = list(self.postagger.postag(self.words))  # 词性标注
        num = 0
        #副词或者名词后面一个词
        for tag in postags:
            if tag in ['d']:
                if num+1 < len(postags):
                    if num != 0 and postags[num + 1] in ['n','v']:
                        if self.words[num+1] not in self.opinionword \
                            and len(self.words[num + 1].decode('utf-8','ignore')) > 1:
                            self.n_v.append(self.words[num + 1])
            #动词或者n词
            if tag in ['a','i','b'] :
                if self.words[num] not in self.opinionword\
                        and len(self.words[num].decode('utf-8','ignore')) > 1:
                    self.n_v.append(self.words[num])
            num += 1
        return postags

    def prepare(self, ):
        for id, sentences in self.Dsent.items():
            split_sentence = re.split(ur'[,，()（）、： …～？。！. !?]?', sentences.decode('utf-8', 'ignore').strip())
            for sent in split_sentence:
                self.words = self.cut_word(sent.encode('utf-8', 'ignore'))
                self.postags = self.word_sex()
                cword = Counter(self.n_v)

                lresult = heapq.nlargest(500, cword.items(), key=lambda x: x[1])
                # lword = []
                # for rg in lresult:
                #     w, n = rg
                #     lword.append(w)
                # self.sql.insert(self.industry_id, lword)
        self.postagger.release()  # 释放模型
                # self.parser.release()  # 释放模型
                # outfile.close()
        return lresult


if __name__ == "__main__":
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)

    # logging configure
    import logging.config
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

    moniterword = '欧莱雅'
    sen_ins = MakeSentence(keyword=moniterword,day=1)
    logger.info('find words')
    Dsents = sen_ins.extract_sentence()
    logger.info('length Dsent:%s'%len(Dsents))
    # Dsents = {1: '欧莱雅美丽漂亮难看'}
    ins = Opinion( Dsents, industry_id=1)
    attd = ins.prepare()
    for rg in attd:
        w, n = rg
        print w, n

# coding:utf-8
import sys
import os
import re
import json
import jieba
import heapq
from collections import Counter
from pyltp import Postagger
from pyltp import Parser
from jieba.norm import norm_cut
dir_path = os.path.dirname(os.path.abspath(__file__))
jieba.load_userdict("%s/conf/jieba_lexicon" % dir_path)
from intelligent.platform.find_word.t_cognition import mysqls
from intelligent.platform.find_word.conf.setting import *
from intelligent.platform.find_word.MakeSentence import MakeSentence
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
LTP_DATA_DIR = '%s/../hotword/ltp_data' % dir_path  # ltp模型目录的路径
# cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
# par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`

"""
1:形容词或者副词动词前面的n词,top100,放在句子首位的n的需要加权重
2:输出到attriword,从而保证结果不重复,存入表中
"""

class FindAttribute(object):
    def __init__(self, moniter_word, Dsent, industry_id):
        self.moniter_word = moniter_word
        self.industry_id = industry_id
        self.Dsent = Dsent
        self.postagger = Postagger()  # 初始化实例
        self.postagger.load_with_lexicon(pos_model_path, '%s/conf/posttags.txt' % dir_path)
        # self.parser = Parser()  # 初始化实例
        # self.parser.load(par_model_path)  # 加载模型
        self.sql = mysqls()
        self.carattributes, self.sysn, self.dup_word = self.sql.run(industry_id)
        self.n_v = []

    def cut_word(self, sents):
        # 分词
        words = [i.encode('utf-8', 'ignore') for i in norm_cut(sents)]  # HMM=False
        num = 0
        # 处理同义词
        for w in words:
            if w in self.sysn.keys():
                words[num] = self.sysn[w]
            num += 1
        return words

    def word_sex(self, ):
        # 获取词性
        postags = list(self.postagger.postag(self.words))  # 词性标注
        num = 0
        #副词或者形容词前面的一个词
        for tag in postags:
            if tag in ['a', 'd']:
                if num != 0 and postags[num - 1] in ['n', 'v']:
                    if self.words[num - 1] not in self.carattributes \
                            and len(self.words[num - 1].decode('utf-8','ignore')) > 1:
                        self.n_v.append(self.words[num - 1])
            #动词或者n词
            if tag in ['n', 'v'] and num == 0:
                if self.words[num] not in self.carattributes\
                        and len(self.words[num].decode('utf-8','ignore')) > 1:
                    # self.words[num] not in self.dup_word \
                    self.n_v.append(self.words[num])
            num += 1
        # print '词性', '\t'.join(postags)
        return postags

    def prepare(self, ):
        for id, sentences in self.Dsent.items():
            split_sentence = re.split(ur'[,，()（）、： …～？。！. !?]?', sentences.decode('utf-8', 'ignore').strip())
            for sent in split_sentence:
                self.words = self.cut_word(sent.encode('utf-8', 'ignore'))
                self.postags = self.word_sex()

        # self.segmentor.release()  # 释放模型
        # outfile = open('attribute_dup.txt', 'a')
        # for word in set(self.n_v):
        cword = Counter(self.n_v)
        lresult = heapq.nlargest(500, cword.items(), key=lambda x: x[1])
        lword = []
        for rg in lresult:
            w, n = rg
            lword.append(w)
        # self.sql.insert(self.industry_id, lword)
        self.postagger.release()  # 释放模型
        # self.parser.release()  # 释放模型
        # outfile.close()
        return lresult

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)  # filename='logger.log',
    moniterword = '欧莱雅'
    # sen_ins = MakeSentence(keyword=moniterword,day=30)
    # logging.info('find words')
    # Dsents = sen_ins.extract_sentence()
    Dsents = {1: '欧莱雅美丽'}
    ins = FindAttribute(moniterword, Dsents, industry_id=1)
    attd = ins.prepare()
    for rg in attd:
        w, n = rg
        print w, n

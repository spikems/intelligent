# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import gensim, logging
from gensim.models import KeyedVectors
from gensim.models.word2vec import Word2Vec
dir_path = os.path.dirname(os.path.abspath(__file__))

# 单例模式
def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class w2vModel(object):
    def __init__(self):
        self.wordvecs = KeyedVectors.load_word2vec_format('%s/model/full_300_sgram_min40.bin' % (dir_path), binary=True,
                                                          limit=500000)
    def codec(self, word):
        if type(word) == unicode:
            return word
        elif type(word) == str:
            return word.decode('utf-8')
        elif type(word) == list:
            if len(word) > 0:
                if type(word[0]) != unicode:
                    return [w.decode('utf-8') for w in word]
                else:
                    return word
            else:
                return word

    # test
    def sim(self, word, topn=30):
        word = self.codec(word)

        # print('sim(%s)' % word.encode('utf-8'))
        # print('=' * 40)
        output = []
        try:
            rets = self.wordvecs.similar_by_word(word, topn)

            for w, s in rets:
                output.append('%s\t%s' % (w.encode('utf-8'), s))
                # print('\n'.join(output))

        except KeyError as e:
            logging.info('Error: {0}'.format(e))

        return output

    def rank(self, word, wlist):

        word = self.codec(word)
        wlist = self.codec(wlist)

        # print('rank(%s:%s)' % (word.encode('utf-8'),
        #                        ' '.join([w.encode('utf-8') for w in wlist])))
        # print('=' * 40)
        dist = []

        try:
            for w in wlist:
                dist.append(self.wordvecs.similarity(word, w))
            idx = np.argmax(dist)
            dist = ['%.2f' % d for d in dist]
            # print('%s %s' % (wlist[idx].encode('utf-8'), ['%.2f' % d for d in dist]))
            return wlist[idx], dist
        except KeyError as e:
            logging.info('Error: {0}'.format(e))
            return -1, dist

    def like(self, pos, neg):

        pos = self.codec(pos)
        neg = self.codec(neg)

        # print('like(%s, %s)' % (
        #     ' '.join([w.encode('utf-8') for w in pos]),
        #     ' '.join([w.encode('utf-8') for w in neg])))
        # print('=' * 40)
        try:
            # r= wordvecs.most_similar(positive=[u'京东', u'刘强东'], negative=[u'阿里'])
            r = self.wordvecs.most_similar(positive=pos, negative=neg)
            # for s, v in r:
            # print s.encode('utf-8')
            return r
        except KeyError as e:
            logging.info('Error: {0}'.format(e))
            return None

    def run(self, stype, query,topn=30):
        """
        stype :1 .求近义词 sim    2 .找距离最近    3.词向量加减结果  like
        if stype == 1:
        """
        outword = []
        try :
            if stype == 1:
                # print('=' * 40)
                output = self.sim(query, topn)
                # print('\n'.join(output))
                if output:
                    outword.append(stype)
                    outword.append(output)
                return outword
            elif stype == 2:
                # print('=' * 40)
                word, dist = self.rank(query[0], query[1])
                # print word,dist
                if len(dist) == len(query[1]):
                    outword.append(stype)
                    outword.append(word)
                    outword.append(dist)
                return outword

            elif stype == 3:
                # for q in query:
                # print('=' * 40)
                output = self.like(query[0], query[1])
                if output:
                    outword.append(stype)
                    outword.append(output)
                return outword
        except:
            return output

if __name__ == "__main__":
    w2v = w2vModel()
    stype = 2
    query = ('省油', ['骐达', '雅阁', '科鲁兹', '路虎', '捷达'])
    topn = 30
    w2v.run(stype,query,topn)
    # if stype == 1:
    #     output = w2v.sim(query, topn=30)
    #     print('\n'.join(output))
    # elif stype == 2:
    #     wlist[idx], dist = w2v.rank(query[0], query[1])
    #     print('%s %s' % (wlist[idx].encode('utf-8'), ['%.2f' % d for d in dist]))
    # elif stype == 3:
    #     output = w2v.like(q[0], q[1])
    #     for s, v in ss:
    #         print s.encode('utf-8')
# ================================================================
# query1 = [
#     # brand and nz
#     '骐达',
#     '科鲁兹',
#     '宝马',
#     '奔驰',
#     '雅阁',
#     '淘宝',
#     '京东',
#     '可口可乐',
#     '倩碧',
#     # aspects
#     '故障率',
#     '动力',
#     '外观',
#     '油耗',
#     # opinion
#     '吐血',
#     '不爽',
#     '长草',
#     '酒精味',
#     '酒精',
#     '还可以',
#     '轻松',
#     '透气',
#     '恶心',
#     '异响',
#     '漏水',
#     '省油',
#     '费油',
#     '熄火',
#     '缺陷'
# ]
#
# query2 = [
#     ('省油', ['骐达', '雅阁', '科鲁兹', '路虎', '捷达']),
#     ('费油', ['骐达', '雅阁', '科鲁兹', '路虎', '捷达'])
# ]
#
# query3 = [
#     (['京东', '马云'], ['刘强东']),
#     (['领动', '郑恺'], ['胡歌']),
#     (['悦诗风吟', '吴亦凡'], ['李敏镐'])
# ]




            # w2v.load(sys.argv[1])
            #
            # for q in query1:
            #     print('=' * 40)
            #     w2v.sim(q)
            #
            # for q in query2:
            #     print('=' * 40)
            #     w2v.rank(q[0], q[1])
            #
            # for q in query3:
            #     print('=' * 40)
            #     w2v.like(q[0], q[1])

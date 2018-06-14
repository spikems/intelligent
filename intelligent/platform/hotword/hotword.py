#!/usr/bin/env python
# coding=utf-8
import sys
import logging
import traceback
import jieba
import redis
import heapq
import os

reload(sys)
sys.setdefaultencoding('utf-8')
from optparse import OptionParser
from collections import Counter
from jieba.norm import norm_cut, norm_seg
from intelligent.common.exldeal import XLSDeal
from intelligent.platform.hotword.keywordmaster import semevalword
from intelligent.platform.hotword.generalword_filter import GeneralWordFilter
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)


class HotWord(object):
    """
    function:Statistical frequency
    parameter: top_num : after counting the word ,how many top word we take
            method : what method is used to count word frequency  such as tfidf ,chi
    output:keyword \t word :frequency and word length>=3
    """

    def __init__(self, inputfile, outputfile, method, word_length=2, top_num=300, keyword='大众'):
        """
        :param inputfile: type :excel Second column title ,Third column text
        :param outputfile: type excel First column word ,second freq
        :param method: only support tfidf
        :param word_length: limit word lenth ;
        :param top_num: how many top word you want you get
        :param keyword:  now is nouseful
        """
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.top_num = top_num
        self.word_length = word_length
        self.method = method
        self.keyword = keyword
        self._redis = redis.Redis(host='192.168.241.46', db=1)  # get idf from redis
        self.oGWF = GeneralWordFilter()  #general word

    def summons_article(self):
        """

        :return:lwords type list includes some articles such as [article one ,article tow ]
        warning only get 50000 article
        """
        lwords = []
        lLines = XLSDeal().XlsToList(self.inputfile)
        num = 0
        for line in lLines:
            num += 1
            if num >=50000:
                break 
            line = line.strip().split('\t')
            if len(line) == 2:
                lwords.append(line[1].lower())
            elif len(line) >= 3:
                line = ' %s %s' % (line[1], line[2])
                lwords.append(line.lower())
        return lwords

    def count_words(self, lwords):
        """
        :param lwords:
        :return: dwords type is dict ; key :word#flag value :freq
        """
        jieba.enable_parallel(10)  # start many processes
        word_flags = []  # {word#flag : freq},{word:sex}
        for context in lwords:
            for sub in norm_seg(context):
                w = sub.word
                if self.oGWF.isGeneralWord(w.encode('utf-8')) or w.strip() == '':
                    continue
                if len(w) >= int(self.word_length):
                    key = '%s#%s' % (w, sub.flag)
                    word_flags.append(key)
        logger.info('count is starting')
        jieba.disable_parallel()
        dwords = Counter(word_flags)
        return dwords

    def count_idf(self, dwords):
        """
        compute tfidf ;idf defalut value 1.1
        :param dwords:
        :return: dwords type is dict key:word#flag value tfidf
        """
        del_num = 0
        for keyword, freq in dwords.items():
            word = keyword.split('#')[0]
            if self._redis.get('idf_%s' % word):
                tfidf = freq * float(self._redis.get('idf_%s' % word))  # tf*idf
                dwords[keyword] = [tfidf, freq]
            else:
                dwords[keyword] = [freq*1.1,freq]  # if word  idf can't find ; then delete the word
                del_num += 1
                logger.info('no tfidf word:%s'%word)
        logger.info('the word not in tfidf num:%s' % del_num)
        return dwords

    def tfidf(self):
        """
        control
        :return: ifile ,is a list ; include is string :format (word, tfidf, freq, flag)
        output also list ; ;include is string like '%s\t%s' % (word, tfidf)
        """
        lfile = []
        output = []
        lwords = self.summons_article()
        logger.info('doc num %s'%len(lwords))
        dwords = self.count_words(lwords)
        logger.info('word  num %s' % len(dwords))
        dwordresult = self.count_idf(dwords)
        logger.info('tfidf word num %s' % len(dwordresult))
        sortdword = heapq.nlargest(int(self.top_num), dwordresult.items(), key=lambda x: x[1][0])
        for sub in sortdword:
            keyword = sub[0]
            tfidf = sub[1][0]
            freq = sub[1][1]
            word = keyword.split('#')[0]
            flag = keyword.split('#')[1]
            line = '{}\t{}\t{}\t{}'.format(word, tfidf, freq, flag)
            line2 = '%s\t%s' % (word, tfidf)
            lfile.append(line)
            output.append(line2)
        logger.info('result num :%s'%len(lfile))
        return lfile, output

    def run(self):
        """
        from list to xlsx
        :return:
        """
        if self.method == 'tfidf':
            lfile, output = self.tfidf()
            XLSDeal().toXlsFile(lfile, self.outputfile)
            return output
        elif self.method == 'feelingword':
            word_instance = semevalword(moniterword=self.keyword, infile=self.inputfile, attr_num=20, word_num=1)
            output = []
            for attword, group in word_instance.items():
                for word, num in group:
                    line2 = '%s\t%s' % (word, num)
                    output.append(line2)
            return output

if __name__ == "__main__":
    # logging configure
    infile = '%s/%s' % (os.path.abspath(''), sys.argv[1])
    ins = HotWord(
        inputfile = infile,
        outputfile = 'aa.xlsx',
        #keyword = keyword,
        method='tfidf')
    ins.run()

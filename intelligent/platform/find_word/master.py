# coding:utf-8
import csv
import logging
from intelligent.platform.find_word.MakeSentence import MakeSentence
from intelligent.platform.find_word.find_att import FindAttribute
from intelligent.platform.find_word.fword_w2vec import Word2vecFindw
from intelligent.common.exldeal import XLSDeal
"""
行业:1美妆 2汽车
用途:1.寻找属性词 2.寻找评价词和评价词短语 3.近义词 4.正负面
传入参数:brand:品牌名 ,industry:行业id ;stype:用途 ;outfile :输出文件名
"""

logging.basicConfig(level=logging.INFO)


class FindWord(object):
    def __init__(self, brand, industry, stype, outfile, is_dup=False):
        if not brand or not industry or not stype or not outfile:
            logging.info('arg is wrong')
            exit()
        self.brand = brand
        self.industry = industry
        self.stype = stype
        if outfile.endswith('.xlsx'):
            self.outfile = outfile
        else:
            self.outfile = '%s.xlsx'%outfile
        self.dup = is_dup

    def run(self):
          # requir around 100 words
        if self.stype == 1:
            self.sen_ins = MakeSentence(keyword=self.brand, day=30)
            Dsents = self.sen_ins.extract_sentence()
            ins = FindAttribute(self.brand, Dsents, industry_id=self.industry)
            attd = ins.prepare()
            if attd:
                lfile = []
                for line in attd:
                    word ,num =line
                    sline = '%s\t%s'%(word,num)
                    lfile.append(sline)
                XLSDeal().toXlsFile(lfile, self.outfile)
                return True,[]
            logging.info('attd num :%s'%len(attd))
            return False,[]
        elif self.stype == 2:
            ins = Word2vecFindw()
            result = ins.run(word=self.brand, typeid=self.stype, is_dup=self.dup)
            if result:
                XLSDeal().toXlsFile(result, self.outfile)
                return True,result
        return False,[]


if __name__ == '__main__':
    brand = '兰蔻'
    industry = 1
    stype = 1
    ins = FindWord(brand, industry, stype, outfile='result')
    ins.run()

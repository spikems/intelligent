#!/usr/bin/env python
# coding=utf-8
import sys
import re
import os
reload(sys)
sys.setdefaultencoding('utf-8')
import esm
import hashlib
from intelligent.common.extract_short_text import ExtractShortText
from intelligent.model.es_query import es_query
import logging
logging.basicConfig(level=logging.INFO)
noneed_word = ['钜惠', '下载附件','地址：','电话：','热销中','指导价：','豪礼相送','手续正规','【包邮】','评论反馈有奖','【原价】','网页链接','公证链接：','转发＋关注']
class MakeSentence(object):
    def __init__(self,keyword,day=30):
        self.keyword = keyword
        self.raw_data = es_query(keyword,day) 
        self.esmins =esm.Index()
        self.extract =ExtractShortText()
        self.dup_list = []
        for word in noneed_word:
            self.esmins.enter(word.strip())
        self.esmins.fix()

    def dup_sentence(self,data):
        #according to md5 to remove dup information
        hash_md5 = hashlib.md5(data)
        dataid = hash_md5.hexdigest()
        if dataid in self.dup_list:     #if data exist ,return True,then continue
            return False
        else:
            self.dup_list.append(dataid)
            return data

    def extract_sentence(self,):
        """
        寻找包含关键词的句子
        :return:
        """
        dsent = {}
        num = 0
        allnum =0
        logging.info('raw_data is num :%s'%len(self.raw_data))
        for line in self.raw_data:
            allnum+=1
            linef =line.strip().split('\t')
            sid = linef[0].strip()
            if len(linef) == 2:
                title  = ''
                text  = linef[1].strip()
            else:
                title = linef[1]
                text = linef[2]
            content = title + text
            if self.esmins.query(content)  :
                # MarketInfo.write('%s\t%s\t%s\n'%(sid,title,text))
                continue
            # linesplit = re.split(
            #         ur'[？。！. !?] *',
            #         content.decode(
            #                 'utf-8',
            #                 'ignore').strip())
            text = self.extract.extract_short_text(self.keyword, content, 101)
            if len(text)>100:
                ltext =self.dup_sentence(text)  #长文本进行MD5去重
            else:
                ltext = text
            num+=1
            if ltext:
                dsent[sid] = ltext
        logging.info('num/allnum: %s/%s'%(num,allnum))
        return dsent

if __name__=='__main__':
    sen_ins=MakeSentence(keyword = u'欧莱雅')
    sen_ins.extract_sentence()

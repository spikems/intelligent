#!/usr/bin/env python
# coding=utf-8
import re
import sys
import os
sys.path.append('/home/liuhongyu/wangwei/intelligent')
reload(sys)
sys.setdefaultencoding('utf-8')
import esm
import hashlib
from intelligent.common.exldeal import XLSDeal

noneed_word = ['钜惠', '地址：','电话：','热销中','指导价：']
class MakeSentence(object):

    def __init__(self,keyword,infile):
        self.keyword = keyword
        self.lLines = XLSDeal().XlsToList(infile)
        self.esmins =esm.Index()
        self.dup_list = []
        for word in noneed_word:
            self.esmins.enter(word.strip())
        self.esmins.fix()

    def dup_sentence(self,data):
        #according to md5 to remove dup information
        hash_md5 = hashlib.md5(data[:300])
        dataid = hash_md5.hexdigest()
        if dataid in self.dup_list:     #if data exist ,return True,then continue
            return True
        else:
            self.dup_list.append(dataid)
            return False

    def extract_sentence(self,):
        """
        寻找包含关键词的句子
        :return:
        """
        # MarketInfo = open('Market%s'%self.keyword,'wb')
        # keywordfile = open('have%s'%self.keyword,'wb')
        dsent = {}
        num = 0
        allnum =0
        for line in self.lLines:
            allnum+=1
            linef =line.strip().split('\t')
            sid = linef[0].strip()
            if len(linef) == 2:
                title  = ''
                text  = linef[1].strip()
            else:
                title = linef[1]
                text = linef[2]
            content = title +'。'+ text
            if self.esmins.query(content)  :
                # MarketInfo.write('%s\t%s\t%s\n'%(sid,title,text))
                continue
            content = content[0:10000]
            if  self.dup_sentence(content):      #remove dup data
                continue

            linesplit = re.split(
                    ur'[？。！. !?] *',
                    content.decode(
                            'utf-8',
                            'ignore').strip())
            # ltext = [i[:600] for i in linesplit ] # 只需要包含大众的那句话
            #if i.find(self.keyword) != -1
            ltext = linesplit
            num+=1
            if ltext:
                dsent[sid] = ltext
                # keywordfile.write('%s\t%s\n' % (sid, ''.join(ltext)))

        print 'num/allnum: %s/%s'%(num,allnum)
        # MarketInfo.close()
        # keywordfile.close()
        return dsent

if __name__=='__main__':
    sen_ins=MakeSentence(keyword = u'a',infile='%s/data/tmp.xlsx'%(os.path.abspath('')))
    sen_ins.extract_sentence()

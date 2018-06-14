#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
a tool that judge didi have occured in what happend

input : excel
output : excel add column : grade
"""
# import jieba
import os
import sys
import pymysql
import traceback
import logging
import numpy
import json
import requests
import msgpack
import time
import random
import esm
import django
import zerorpc
import pandas as pd

reload(sys)
sys.setdefaultencoding('utf-8')
from django.shortcuts import render
# from jieba.norm import norm_cut, norm_seg
# from jieba import  suggest_freq
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    # filename=os.path.join(LOG_DIR, "cyberin.log")
)
logger = logging.getLogger(__name__)
dir_path = os.path.dirname(os.path.abspath(__file__))


class DidiSevemal():
    def __init__(self):
        pass

    def load_settting(self):
        """
        prepare three data
        1.esm store data for search
        2.esm ==> opidict ==> huati
        :return:
        """
        Topic_data = {}
        opidict = {}
        pdata = pd.read_excel(ur'%s/data/滴滴话题分类.xlsx' % dir_path, sheetname=u'正面')
        ndata = pd.read_excel(ur'%s/data/滴滴话题分类.xlsx' % dir_path, sheetname=u'负面')
        num = 0
        #load data
        for line in pdata[u'编号'].fillna(0):
            Topic_data[line] = (
            str(pdata[u'一级话题'][num]).encode('utf-8', 'ignore'), str(pdata[u'二级话题'][num]).encode('utf-8', 'ignore'))
            num += 1
        num = 0
        for line in ndata[u'编号'].fillna(0):
            Topic_data[line] = (
            str(ndata[u'一级话题'][num]).encode('utf-8', 'ignore'), str(ndata[u'二级话题'][num]).encode('utf-8', 'ignore'))
            num += 1
        #load opinion word with esm
        opiesm = esm.Index()
        oword = pd.read_excel(ur'%s/data/评价词.xlsx' % dir_path)
        num = 0
        for line in oword[u'话题分类编号'].fillna(0):
            if isinstance(line, int) and line != 0:
                word = oword['word'][num].encode('utf-8', 'ignore').strip()
                opiesm.enter(word)
                opidict[word] = [int(i) for i in str(line).split(',')]
            num += 1
        opiesm.fix()
        return Topic_data, opidict, opiesm

    def main(self, infile,outfile):

        # self.reload_jieba()
        # writer = pd.ExcelWriter('output.xlsx')
        Topic_data, opidict, opiesm = self.load_settting()
        data = pd.read_excel(infile)
  #      outfile = infile.split('.xlsx')[0] + 'result' + '.xlsx'
        noopinum = 0

        nline = []
        lfirst = []
        lseconde = []
        try :
            data[u'序号'][:1]
        except:
            logger.error('no column name id')
            sys.exit(1)

        for num in range(len(data[u'序号'])):
            try:
                test_data = {'test_title': str(data[u'主题'][num]).encode('utf-8', 'ignore'),
                             'test_con': str(data[u'摘要'][num]).encode('utf-8', 'ignore')
                             }  # data[u'行业'][num]}
            except:
                logger.error('keyerror ,请检查列标题')
                sys.exit(1)
            # result = json.loads(self.dm_test(test_data))
            content = test_data['test_title'] + test_data['test_con']
            # qword = result['1'].get('reason', '').encode('utf-8', 'ignore')
            # if qword == '没有监控词或者评价词':
                # print test_data.get('test_con')
                # print result['1']['prob']
            words = opiesm.query(content)
            # print words
            if words:
                ftopic = set()
                stopic = set()
                for opi in words:
                    if opidict[opi[1]]:
                        for topic_id in opidict[opi[1]]:
                            try:
                            	stopic.add(Topic_data[topic_id][1])
                            	ftopic.add(Topic_data[topic_id][0])
                            except:
                                continue   
                            # data[u'二级标题'][num]= Topic_data[topic_id][1]
                            logger.info('#'.join(Topic_data[topic_id]))
                lfirst.append(' '.join(ftopic))
                lseconde.append(' '.join(stopic))
                nline.append(num)
            else:
                noopinum += 1
        s1 = pd.Series(lfirst, index=nline)
        s2 = pd.Series(lseconde, index=nline)
        data[u'一级标题'] = s1
        data[u'二级标题'] = s2
        data.to_excel(outfile, sheet_name='abc', index=False, header=True)
        logger.info('have no topic num:%s' % noopinum)

    def reload_jieba(self, ):
        """ 重新加载 jieba 词典 """
        conn = pymysql.connect(host="192.168.241.45", user="oopin", password="OOpin2007Group", db="dm_base",
                               charset="utf8mb4")
        cursor = conn.cursor()
        cursor.execute(r"select name from feature_word")
        names = [d[0].strip().encode("utf-8", "ignore") for d in cursor.fetchall() if d and d[0] and d[0].strip()]
        [jieba.add_word(name, freq=10000, tag='a') for name in names]

    # @login_required
    def dm_test(self, test_data):
        if test_data:
            test_title = test_data.get('test_title')
            test_con = test_data.get('test_con')
            brand = test_data.get('brand')
            text_type = test_data.get('text_type')
            text_link = test_data.get('text_link')
            industry = test_data.get('industry')
            # print " ".join(jieba.cut(test_con or ""))
            # print " ".join(jieba.cut(test_title or ""))
            project = 'semeval'
            data = [{
                "id": "1",
                "title": " ".join(jieba.cut(test_title or "")),
                "document": " ".join(jieba.cut(test_con or "")),
                "brand": brand,
                "type": text_type,
                "link": text_link,
                "industry": industry,
                "entryid": "0",
            }]
            j_data = requests.post('http://192.168.241.8:8100/tumnus/dm/flm', timeout=120,
                                   data={"project": project,
                                         "param": msgpack.packb(data).decode('ISO-8859-2', 'ignore')}).text
            res = json.dumps({d["id"]: d for d in msgpack.unpackb(j_data.encode('ISO-8859-2', 'ignore'))})
            return res

    def cal_soc_items_type(self, text):
        sleep = 1
        retry = 3
        SOC_URI = 'tcp://192.168.241.41:15200'
        for i in range(retry):  # 重试 3 次
            soc_c = None
            try:
                soc_c = zerorpc.Client(SOC_URI)
                texts = [text]
                types = soc_c.parse(texts)
                return types
            except:
                if i + 1 < retry:
                    rand_sleep = (random.random() + 0.5) * sleep
                    time.sleep(rand_sleep)
                    sleep = sleep * 2 if sleep * 2 < 1000 else 1000
            finally:
                if soc_c:
                    soc_c.close()
        return {"status": "err"}


if __name__ == '__main__':
    # test_data = {'dm_type' : "1",'test_title' : "今天限号  等个滴滴等了20分钟 烦躁 ?? ",
    #              'test_con':'今天限号  等个滴滴等了20分钟 烦躁 ?? ',  'brand':'滴滴' ,
    #              'text_type': '无','text_link':'http://weibo.com/2651702601/Fwicwy52E','industry':'滴滴'}
    ins = DidiSevemal()
    infile = 'data/滴滴.xlsx'
    ins.main(infile,'aa.xlsx')
    # ins.readExl(sys.argv[1])
    # dm_test(test_data)

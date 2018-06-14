#!/usr/bin/env python
# coding=utf-8
import sys
import re
import os
reload(sys)
sys.setdefaultencoding('utf-8')
import esm
import hashlib
import logging

noneed_word = ['导购频道】','钜惠', '下载附件','地址：','电话：','热销中','指导价：','豪礼相送','手续正规',
               '【包邮】','评论反馈有奖','【原价】','网页链接','公证链接：','转发＋关注','扫描下方二维码','到店咨询购买','优惠高达',
               '全球免邮','秒拍视频','今天给大家推荐','降价促销','可分期','音响改装升级','欢迎到店咨询','据报道','转让','据外媒',
               '免息优惠','现车充足','点击下方询价','预定咨询','欲购从速','最低仅需','开启售卖','火热预售','日公告','十年老店',
               '奖品等您拿','置换补贴','现车直降','限量发售','礼包免费送','售价：','详询：','专线：','编辑：','超值礼品','恭迎莅临',
               '欢迎前来品鉴','下载次数:','多重优惠等着您','热线：','记者／','凤凰汽车讯日前','官方获悉','智联科技抢先体验','数据显示：',
               '重大礼','前瞻：','咨询：','享受车展优惠','感恩回馈','4s店：','详询免费','圆满落幕','来源：','日前，','日，',
               '优惠倒计时','新车来袭，','月，','购车狂欢节','电话微信同步','文：','获悉，','首发】','【测试','】','欢迎试驾看车']

"""
传入:品牌名 keyword   raw_data['id\ttitletext']
输出:dsent={'id:content',}
"""

class MakeSentence(object):

    def __init__(self,raw_data,is_marketing=True,is_dup=True):
        self.raw_data = raw_data
        self.esmins =esm.Index()
        self.dup_list = []
        self.is_market = is_marketing
        self.is_dup = is_dup
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
        for line in self.raw_data:
            linef =line.strip().split('\t')
            sid = linef[0].strip()
            if len(linef) >= 2:
                text = linef[1]+'。'+ linef[2]

            if len(text.decode('utf-8','ignore'))>1000:
                continue

            if self.esmins.query(text)  and self.is_market:
                continue
 
            if len(text)>200 and self.is_dup:
                ltext =self.dup_sentence(text)  #长文本进行MD5去重
            else:
                ltext = text
      
            if ltext:
                dsent[sid] = ltext
        num = str(len(dsent))
        logging.info('filter remain num : %s'%num)
        return dsent

if __name__=='__main__':
    sen_ins=MakeSentence(keyword = u'')
    sen_ins.extract_sentence()

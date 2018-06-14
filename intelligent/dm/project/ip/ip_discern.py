#! /usr/bin/python
# -*- coding:utf-8 -*-
import logging
import esm
from intelligent.dm.project.ip.conf.ip_discern_conf import *
from intelligent.model.t_ip_words import IpWords
from intelligent.dm.project.ip.ip_predict import PredictIp
from intelligent.common.util import *
from intelligent.dm.project.ip.conf.ip_discern_conf import ip_types
import sys
import time
import traceback
import jieba
import os
reload(sys)
sys.setdefaultencoding('utf8')


@singleton
class IpDiscern(object):
    def __init__(self):
        self.logger = logging.getLogger('intelligent')
        self.err_logger = logging.getLogger('errinfo')
        self.limit_index_dict = {}
        self.ip_type = None
        start1 = time.time()
        self.ip_words_dict = {}
        self.load_database()
        self.set_limit_ip_words()   # 设置限定词组
        start2 = time.time()
        self.predict = PredictIp()
        project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径
        ip_dict_path = project_path + '/conf/star_ip_word.txt'
        jieba.load_userdict(ip_dict_path)

    def load_database(self):
        # 将所有的数据保存到一个字典中：{'1':[name1:[{}]], '3':[name1:[{}] ]}
        query_obj = IpWords()
        for ip_type in ip_types:
            self.ip_words_dict[ip_type] = query_obj.queryAll(ip_type)

    def set_limit_ip_words(self):
        # 建立限定词组
        for ip_type in self.ip_words_dict:   # 遍历 每一个类型，对应查询到的IP词组，然后制订对应的Index
            ip_name_index = esm.Index()
            for name in self.ip_words_dict[ip_type]:
                ip_name_index.enter(name)
            ip_name_index.fix()
            self.limit_index_dict[ip_type] = ip_name_index

    def filter_words(self, text):
        # 根据限定词过滤文章内容
        final_result = {}
        filter_result = {}
        # 调用PredictIp对象的run函数，这里数据先过规则，再过模型
        if self.ip_type == 'all':
            for ip_type in self.limit_index_dict:
                position_name_datas = self.limit_index_dict[ip_type].query(text)  # 得到文章中有ip_name的数据
                try:
                    if position_name_datas:   # 如果此类型的限定词，能够在句子中找到
                        filter_result = self.predict.run(text, position_name_datas, self.ip_words_dict[ip_type],
                                                         ip_type)
                        for ip_word in filter_result:
                            if ip_word not in final_result:   # 如果没有其他类别同名的IP词汇
                                final_result[ip_word] = filter_result[ip_word]
                            else:                             # 如果已经有了其他类别的IP词汇
                                final_result[ip_word].extend(filter_result[ip_word])
                except:
                    error_info = "filter_word():error  traceback: %s" % (traceback.format_exc())
                    self.err_logger.error(error_info)
        else:   # 如果是单独访问一个类型
            if self.ip_type not in ip_types:
                return None
            position_name_datas = self.limit_index_dict[self.ip_type].query(text)  # 得到文章中有ip_name的数据
            if position_name_datas:
                try:
                    final_result = self.predict.run(text, position_name_datas, self.ip_words_dict[self.ip_type], self.ip_type)
                    for ip_word in filter_result:
                        if ip_word not in final_result:   # 如果没有其他类别同名的IP词汇
                            final_result[ip_word] = filter_result[ip_word]
                        else:                             # 如果已经有了其他类别的IP词汇
                            final_result[ip_word].extend(filter_result[ip_word])
                except:
                    error_info = "filter_word():error  traceback: %s" % (traceback.format_exc())
                    self.err_logger.error(error_info)
        return final_result    # 结构 {name1:{name1数据}, name2:{name2数据}}

    def run(self, list_data):
        # 提取数据
        self.ip_type = list_data[0]['ip_type']   # 提取列表中的第一个元素，获取ip_type
        if self.ip_type not in ip_types.keys():  # 如果输入的type不在已有列表里面，用'all'来
            self.ip_type = 'all'
        list_data = list_data[1:]    # 其余的为数据
        result_data = []
        for data in list_data:
            try:
                one_result = {}
                one_result['id'] = data['id']    # 记录此条结果的 ID
                text ='%s。%s' % (data['title'], data['document'])
                text = text.lower()   # 先将大写字母全部转换为小写的
                if type(text) == unicode:   # 如果是unicode类型
                    text = text.encode('utf-8')
                filter_result = self.filter_words(text)
                # 暂停这里***************************************************************
                if not filter_result:   # 如果没有查到ip词
                    continue
                one_result['result'] = filter_result   # 结构 {name1:{name1数据}, name2:{name2数据}}
                result_data.append(one_result)
                # 记录一条one_result的数据
                result_log = '%s  |  %s' % (str(one_result['id']), one_result['result'].keys())
                self.logger.info(result_log)
            except:
                error_info = "cycle | param : %s     traceback: %s" % (str(data), traceback.format_exc())
                self.err_logger.error(error_info)
        return result_data

if __name__ == '__main__':
    start = time.time()
    test = IpDiscern()
    param = [{'ip_type': 'all'},
             {'id': '1', 'title': '',
              'document': '什么！费德勒和纳达尔竟然抱团组队“互抱大腿”？	小德、穆雷、拉奥尼奇、锦织圭和瓦林卡'},
             ]
    data = test.run(param)
    for result in data:
        print result['id']
        for name in result['result']:
            print name
            print result['result'][name]
        print '*'*100
    print(time.time()-start)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import sys
import os
import copy
import logging
import datetime
import traceback
from time import time
from intelligent.common.util import singleton
from intelligent.platform.key_word_trend.conf.base_conf import statical_result, month_chain
from intelligent.platform.key_word_trend.news_count_trend import news_main
from intelligent.platform.key_word_trend.PGC_count_trend import pgc_main
from intelligent.platform.key_word_trend.UGC_count_trend import ugc_main
from intelligent.platform.key_word_trend.tendency_chart import plot_chart
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径
Init_time = time()

import logging.config
logger=logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.INFO)
@singleton
class TrendKeyWord(object):
    def __init__(self):
        self.display_dict = {'all': ['ratio', 'frequency'], 'ratio': ['ratio'], 'frequency': ['frequency']}
        self.sLogPath = '%s/../../../logs/platform.error' % project_path
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s : %(filename)s[line:%(lineno)d] : %(message)s',
                            filename=self.sLogPath)
        self.err_logger = logging.getLogger(__name__)

    def es_process_data(self, term,should_body, start_time='2017-04-01',time_interval='week'):
        '''
        处理查询到的news类、PGC类、UGC类的各个数据
        :param key_words_dict: {term1:[word1, word2], term2:[word3, word4}
        :return:
        '''
        term = term.replace(' ','').replace('\n','').replace('\t','')
        term_result_dict = {}  # 用来存放一个 term的全部数据
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
        save_excel_path = project_path + '/excel_data/' + now_time
        is_exist = os.path.exists(save_excel_path)
        if not is_exist:   # 判断当前路径是否存在
            os.makedirs(save_excel_path)   # 创建保存的目录
        try:
            news_data = news_main(save_excel_path,term=term,should_body=should_body, start_time=start_time,query_type =time_interval)
            logger.info('new_data:%s'%news_data)
            pgc_data = pgc_main(save_excel_path, term,should_body, start_time ,query_type=time_interval)
            logger.info('pgc_data:%s'%pgc_data)
            ugc_data = ugc_main(save_excel_path, term,should_body, start_time ,query_type=time_interval)
            logger.info('ugc_main',ugc_data)
            logger.info('search time %.2f'%(time() - Init_time))
            term_result_dict[term] = {'ratio': [news_data['ratio'],pgc_data['ratio'], ugc_data['ratio']],
                                      'frequency': [news_data['frequency'], pgc_data['frequency'], ugc_data['frequency']]}
        except Exception as e:
            print e
            error = "es_process_data file error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return term_result_dict

    def paint_process_data(self, term_result_dict, result_type_list, time_interval, output_path=''):
        '''
        先处理画图数据，然后画图
        :param term_result_dict: {term: [one_news_result, one_pgc_result, one_ugc_result}
        :return:
        result_term_data_dict: {term: paint_data_dict}  paint_data_dict={'frequency':[time_list, news_number_list, pgc_number_list, ugc_number_list]}
        '''
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
        if not output_path:  # 如果output_path路径不存在
            output_path = project_path + '/output/' + now_time
            is_exist = os.path.exists(output_path)
            if not is_exist:  # 判断当前路径是否存在
                os.makedirs(output_path)  # 创建保存的目录
        else:
            is_exist = os.path.exists(output_path)
            if not is_exist:
                print output_path, '路径不存在？？？？'
                os.makedirs(output_path)
        result_term_data_dict = {}
        for term in term_result_dict:  #
            paint_data_dict = {}  # 格式为 term1:[[time_list],[news_number_list],[pgc_number_list],[ugc_number_list]]
            for type_display in term_result_dict[term]:  # 结构{'ratio': [], 'frequency': []}
                time_data1 = copy.deepcopy(term_result_dict[term][type_display][1].keys())   # ['一带一路']['ratio']
                time_data2 = copy.deepcopy(term_result_dict[term][type_display][2].keys())  # ['一带一路']['ratio']
                time_data1.sort()
                time_data2.sort()
                time_data1.extend(time_data2[:-4])   # 因为ugc的数据要比pgc领先一两天，因此需要截断ugc的近期日期，以pgc为准
                time_data = list(set(time_data1))
                time_data.sort()  # 对第一个ugc的时间序列进行排序
                time_list = []
                for common_time in time_data:   # 以第一条数据为标准
                    time_list.append(common_time)
                news_number_list = []
                pgc_number_list = []
                ugc_number_list = []
                for one_time in time_list:
                    news_number_list.append(term_result_dict[term][type_display][0][one_time] if one_time in term_result_dict[term][type_display][0] else 0)  # 获取新闻类对应时间的number
                    pgc_number_list.append(term_result_dict[term][type_display][1][one_time] if one_time in term_result_dict[term][type_display][1] else 0)   # 获取pgc类对应时间的number
                    ugc_number_list.append(term_result_dict[term][type_display][2][one_time] if one_time in term_result_dict[term][type_display][2] else 0)  # 获取ugc类对应时间的number
                paint_data_dict[type_display] = [time_list, news_number_list, pgc_number_list, ugc_number_list]
            for type_display in paint_data_dict:
                if type_display not in result_type_list:   # 如果不在 需要的显示范围内
                    continue
                try:
                    save_path = output_path + '/%s' %term.split()[0] + '_' + type_display + '_' + time_interval + '_' + now_time + '.png'
                    print save_path
                    plot_chart(paint_data_dict[type_display][0], paint_data_dict[type_display][1], paint_data_dict[type_display][2], paint_data_dict[type_display][3],
                               term, save_path, type_display=type_display, interval_period=time_interval)
                except:
                    error = "paint_process_data file error. traceback: %s" % traceback.format_exc()
                    self.err_logger.error(error)
            result_term_data_dict[term] = paint_data_dict
        return result_term_data_dict

    def calculated_compare(self, term_date_dict, time_interval, output_path, chain_type='week'):
        '''
        :param term_date_dict: {term: paint_data_dict}  paint_data_dict={'frequency':[time_list, news_number_list, pgc_number_list, ugc_number_list]}
        :param time_interval: 搜索的时间间隔： day以天为间隔，week以week为间隔
        :param chain_type: 环比类型, 周环比|月环比
        :return: result_str_list 得到判断结果
        '''
        result_term_str_dict = {}
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
        for term in term_date_dict:
            try:
                result_str_list = []    # 保存每一条输出的结论
                # ratio_data = term_date_dict[term]["ratio"]   这里只用  frequency来进行处理
                time_list = term_date_dict[term]["frequency"][0]
                news_number_list = term_date_dict[term]["frequency"][1]
                news_result_dict = {}
                pgc_number_list = term_date_dict[term]["frequency"][2]
                pgc_result_dict = {}
                ugc_number_list = term_date_dict[term]["frequency"][3]
                ugc_result_dict = {}
                if time_interval == 'day':
                    if chain_type == 'week':  # 如果是周环比，还是走以前的流程
                        N = len(time_list)
                        for i in range(7, N):
                            news_result_dict[time_list[i]] = news_number_list[i] + news_number_list[i-1] + news_number_list[i-2] + news_number_list[i-3] + news_number_list[i-4] + news_number_list[i-5] + news_number_list[i-6]
                            pgc_result_dict[time_list[i]] = pgc_number_list[i] + pgc_number_list[i-1] + pgc_number_list[i-2] + pgc_number_list[i-3] + pgc_number_list[i-4] + pgc_number_list[i-5] + pgc_number_list[i-6]
                            ugc_result_dict[time_list[i]] = ugc_number_list[i] + ugc_number_list[i-1] + ugc_number_list[i-2] + ugc_number_list[i-3] + ugc_number_list[i-4] + ugc_number_list[i-5] + ugc_number_list[i-6]
                        result_str_list = statical_result(time_interval, news_result_dict, pgc_result_dict, ugc_result_dict, time_list)
                    elif chain_type == 'month':  # 如果是月环比
                        result_str_list = month_chain(news_number_list, pgc_number_list, ugc_number_list, time_list)
                elif time_interval == 'week':
                    N = len(time_list)
                    for i in range(N):
                        news_result_dict[time_list[i]] = news_number_list[i]
                        pgc_result_dict[time_list[i]] = pgc_number_list[i]
                        ugc_result_dict[time_list[i]] = ugc_number_list[i]
                    result_str_list = statical_result(time_interval, news_result_dict, pgc_result_dict, ugc_result_dict, time_list)
                result_term_str_dict[term] = result_str_list
                save_path = output_path + '/%s' % term.split()[0] + now_time + '.txt'
                with open(save_path, 'w') as f:
                    for result_str in result_str_list:
                        f.write(result_str + '\r\n')
            except Exception as e:
                error = "trend_main file error. traceback: %s" % traceback.format_exc()
                self.err_logger.error(error)
        return result_term_str_dict

    def build_search_body(self,synonyms):
        """
        build the core query
        :param synonyms:
        :return:
        """
        should_body = []
        for group in synonyms:
            if  not group:
                continue
            bool_body = {"bool":{"must":[]}}
            for word in group.split():
                multi_body = {
                    "multi_match": {
                    "minimum_should_match": "100%",
                    "query": word,
                    "type": "phrase",
                    "slop": 0,
                    "fields": ["title","text"]}}
                bool_body["bool"]["must"].append(multi_body)
            should_body.append(bool_body)
        return should_body


    def trend_main(self, kword, synonyms, time_interval, result_type, output_path, chain_type):
        '''

        :param term:  关键词的趋势
        :param synonyms:  关键词的同义词，两个词以#隔开
        :param start_time:  # 查看趋势的起始时间
        :param end_time:   # 查看趋势的结束时间
        :param time_interval:  搜索的时间间隔： day以天为间隔，week以week为间隔
        :param result_type:   # 搜索的类型，'all'看全部， 'ratio'看比率，'frequency'看频率
        :param chain_type:  统计环比  'month'月环比   'week'周环比
        :param output_path:
        :return:
        '''

        if result_type not in self.display_dict or not output_path or not kword:
            return False
        l_search_word = []
        l_search_word.append(kword)
        l_search_word.extend(synonyms.split('#'))
        should_body = self.build_search_body(l_search_word)
        logger.info('should body %s'%should_body)
        try:
            term_result_dict = self.es_process_data(term=kword,should_body=should_body,start_time='2017-04-01', time_interval=time_interval)
            term_date_dict = self.paint_process_data(term_result_dict, self.display_dict[result_type], time_interval, output_path=output_path)
            term_str_dict = self.calculated_compare(term_date_dict, time_interval, output_path, chain_type)
        except Exception as e:
            error = "trend_main file error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
            return False
        return True


if __name__ == '__main__':
    term = '佛系'
    synonyms=''
    time_interval = 'week'
    result_type = 'all'
    chain_type = 'week'
    output_path =  './output'
    TrendKeyWord().trend_main(term, synonyms, time_interval, result_type, output_path, chain_type)

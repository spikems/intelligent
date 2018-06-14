# -*- coding:utf-8 -*-
# -*- coding:utf-8 -*-
import logging
import os
import sys
import copy
import xlrd
import datetime
import traceback
import xlsxwriter
from elasticsearch import helpers
from elasticsearch import Elasticsearch
reload(sys)
sys.setdefaultencoding('utf-8')

es = Elasticsearch(["http://192.168.241.35:9200", "http://192.168.241.46:9200", "192.168.241.50:9201",
                    "http://192.168.241.47:9201"], sniffer_timeout=200, timeout=100)


def key_word_es_query(start_time, end_time, term, query_type='day'):
    body = {"query": {"bool": {
                "must": [{"range": {
                    "post_time": {
                        "gte": "%s 00:00:00" % start_time,
                        "lte": "%s 00:00:00" % end_time
                    }}},
                    {"multi_match": {
                        "fields": [
                            "title",
                            "text"],
                        "query": "%s" % (term),
                        "type": "phrase",
                        "minimum_should_match": "100%",
                        "slop": 0
                        }},
                    {
                        "term": {
                            "site_type": {"value": 1}
                        }}],
                        "must_not": [
                            {
                                "terms": {
                                    "site_name": ["今日头条", "一点资讯"]
                                }}]}},
                "aggs": {
                    "date": {
                        "date_histogram": {
                            "field": "post_time",
                            "interval": "%s" % query_type
                        }
                    }
                }
            }
    i = 0  # 设置一个最多访问5次
    while True:
        try:
            i += 1
            if i > 5:
                return {}
            es_count = es.search(index="community2", body=body, size=0)
            break
        except Exception as e:
            print e
    time_number = {}   # 格式{'time1':number1, 'time2':number2}
    for i in es_count['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        time_number[time_record] = article_number
    return time_number


def all_es_query(start_time, end_time, query_type='week'):
    body = {"query": {"bool": {
                "must": [{"range": {
                    "post_time": {
                        "gte": "%s 00:00:00" % start_time,
                        "lte": "%s 00:00:00" % end_time
                    }}},
                    {
                        "term": {
                            "site_type": {"value": 1}
                        }}],
                        "must_not": [
                            {
                                "terms": {
                                    "site_name": ["今日头条", "一点资讯"]
                                }}]}},
                "aggs": {
                    "date": {
                        "date_histogram": {
                            "field": "post_time",
                            "interval": "%s" % query_type
                        }
                    }
                }
            }
    i = 0  # 设置一个最多访问5次
    while True:
        try:
            i += 1
            if i > 5:
                return {}
            es_count = es.search(index="community2", body=body, size=0)
            break
        except Exception as e:
            print e
    total_number = {}   # 格式{'time1':number1, 'time2':number2}
    for i in es_count['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        total_number[time_record] = article_number
    return total_number


def save_excel_file(time_number, total_number, save_path):
    workbook = xlsxwriter.Workbook(save_path)
    sheet = workbook.add_worksheet('predict')
    sheet.write(0, 0, u'日期')
    sheet.write(0, 1, u'文章数')
    sheet.write(0, 2, u'总文章数')
    sheet.write(0, 3, u'占总比例')
    i_row = 1
    result_data = {}
    ratio_data = {}  # 保存比率数据
    frequency_data = {}  # 保存频率数据
    sort_time = copy.deepcopy(time_number.keys())
    sort_time.sort()
    sort_time = sort_time[::-1]     # 将日期从后往前排列
    for n in range(len(sort_time)):    # 抛出最开始的五个数据
        sheet.write(i_row, 0, sort_time[n])  # 必须为unicode
        sheet.write(i_row, 1, int(time_number[sort_time[n]]))
        sheet.write(i_row, 2, int(total_number[sort_time[n]]))
        sheet.write(i_row, 3, float(time_number[sort_time[n]])/float(total_number[sort_time[n]]))
        ratio_data[sort_time[n]] = float(time_number[sort_time[n]]) / float(total_number[sort_time[n]])
        frequency_data[sort_time[n]] = int(time_number[sort_time[n]])
        i_row += 1
    result_data['ratio'] = ratio_data
    result_data['frequency'] = frequency_data
    workbook.close()
    return result_data


def news_main(save_excel_path, term='', query_type='day', time_span=100):
    if not term:
        return {'ratio': [], 'frequency': []}
    date_time = datetime.datetime.now()
    end_time = ((date_time - datetime.timedelta(days=0)).date())
    # start_time = str((date_time - datetime.timedelta(days=time_span)).date())
    start_time = ((date_time - datetime.timedelta(days=time_span)).date())  # 起始时间用时间间隔
    time_number = key_word_es_query(start_time, end_time, term, query_type=query_type)  # 搜索关键词的每周文章数据
    total_number = all_es_query(start_time, end_time, query_type=query_type)        # 搜索关键词的每周总文章数据
    now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    save_path = save_excel_path + '/%s_news_' % term + now_time +'.xlsx'
    result_data = save_excel_file(time_number, total_number, save_path)
    # process_data(term, result_data)
    return result_data

if __name__ == "__main__":
    pass



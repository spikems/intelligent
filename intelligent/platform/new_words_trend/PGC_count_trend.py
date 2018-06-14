# -*- coding:utf-8 -*-
# 微信、微博KOL的计算
import logging
import os
import sys
import xlrd
import copy
import datetime
import traceback
import xlsxwriter
from elasticsearch import helpers
from elasticsearch import Elasticsearch
reload(sys)
sys.setdefaultencoding('utf-8')
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径

es = Elasticsearch(["http://192.168.241.35:9200", "http://192.168.241.46:9200", "192.168.241.50:9201",
                    "http://192.168.241.47:9201"], sniffer_timeout=200, timeout=100)


def wei_key_word_es_query(start_time, end_time, term, query_type='day'):
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
                        "terms": {
                            "site_name": ["微信", "新浪微博"]
                        }},
                        {
                        "term": {
                            "is_kol": {"value": "T"}
                        }}
                ]}},
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
            es_count_1 = es.search(index="community2", body=body, size=0)
            es_count_2 = es.search(index="weixin_weibo", body=body, size=0)
            break
        except Exception as e:
            print e
    time_number_1 = {}  # 用来保存community2里面的  时间：number
    for i in es_count_1['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        time_number_1[time_record] = article_number

    time_number_2 = {}  # 用来保存weixin_weibo里面的   时间：number  时间序列和community2不一致
    for i in es_count_2['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        time_number_2[time_record] = article_number

    time_number = {}  # 用来统一  时间: number
    for time_record in time_number_1:   # 时间序列以 community2 为标准
        if time_record in time_number_2:
            time_number[time_record] = time_number_1[time_record] + time_number_2[time_record]

    return time_number


def wei_all_es_query(start_time, end_time, query_type='week'):
    body = {"query": {"bool": {
                "must": [{"range": {
                    "post_time": {
                        "gte": "%s 00:00:00" % start_time,
                        "lte": "%s 00:00:00" % end_time
                    }}},
                    {
                        "terms": {
                            "site_name": ["微信", "新浪微博"]   # "今日头条", "一点资讯"
                        }},
                    {
                        "term": {
                            "is_kol": {"value": "T"}
                        }}
                ]}},
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
            es_count_1 = es.search(index="community2", body=body, size=0)
            es_count_2 = es.search(index="weixin_weibo", body=body, size=0)
            break
        except Exception as e:
            print e
    total_number_1 = {}  # 用来保存community2里面的  时间：number
    for i in es_count_1['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        total_number_1[time_record] = article_number

    total_number_2 = {}  # 用来保存weixin_weibo里面的   时间：number  时间序列和community2不一致
    for i in es_count_2['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        total_number_2[time_record] = article_number

    total_number = {}  # 用来统一  时间: number
    for time_record in total_number_1:   # 时间序列以 community2 为标准
        total_number[time_record] = total_number_1[time_record] + \
                                    total_number_2[time_record] if time_record in total_number_2 else 0
    return total_number


def app_news_key_word_es_query(start_time, end_time, term, query_type='week'):
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
                        "terms": {
                            "site_name": ["今日头条", "一点资讯"]  #
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
    time_number = {}
    for i in es_count['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        time_number[time_record] = article_number
    return time_number


def app_news_all_es_query(start_time, end_time, query_type='week'):
    body = {"query": {"bool": {
                "must": [{"range": {
                    "post_time": {
                        "gte": "%s 00:00:00" % start_time,
                        "lte": "%s 00:00:00" % end_time
                    }}},
                    {
                        "terms": {
                            "site_name": ["今日头条", "一点资讯"]   #
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
    total_number = {}
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
    frequency_data = {}   # 保存频率数据
    sort_time = copy.deepcopy(time_number.keys())
    sort_time.sort()
    sort_time = sort_time[::-1]  # 将日期从后往前排列
    for n in range(len(sort_time)):  # 抛出最开始的五个数据
        sheet.write(i_row, 0, sort_time[n])  # 必须为unicode
        sheet.write(i_row, 1, int(time_number[sort_time[n]]))
        sheet.write(i_row, 2, int(total_number[sort_time[n]]))
        sheet.write(i_row, 3, float(time_number[sort_time[n]]) / float(total_number[sort_time[n]]))
        ratio_data[sort_time[n]] = float(time_number[sort_time[n]]) / float(total_number[sort_time[n]])
        frequency_data[sort_time[n]] = int(time_number[sort_time[n]])
        i_row += 1
    result_data['ratio'] = ratio_data
    result_data['frequency'] = frequency_data
    workbook.close()
    return result_data


def pgc_main(save_excel_path, term='', query_type='day', time_span=100):
    if not term:
        return {'ratio': [], 'frequency': []}
    date_time = datetime.datetime.now()
    end_time = ((date_time - datetime.timedelta(days=0)).date())
    # start_time = str((date_time - datetime.timedelta(days=time_span)).date())
    start_time = ((date_time - datetime.timedelta(days=time_span)).date())  # 起始时间用时间间隔
    wei_time_number = wei_key_word_es_query(start_time, end_time, term, query_type=query_type)
    wei_total_number = wei_all_es_query(start_time, end_time, query_type=query_type)
    app_news_time_number = app_news_key_word_es_query(start_time, end_time, term, query_type=query_type)
    app_news_total_number = app_news_all_es_query(start_time, end_time, query_type=query_type)
    time_number = {}
    total_number = {}
    for time_record in app_news_time_number:  # 尽量以 community2 为标准

            time_number[time_record] = app_news_time_number[time_record] + \
                                       (wei_time_number[time_record] if time_record in wei_time_number else 0)
    for time_record in app_news_time_number:
        total_number[time_record] = app_news_total_number[time_record] + \
                                    (wei_total_number[time_record] if time_record in wei_total_number else 0)
    now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    save_path = save_excel_path +'/%s_PGC_' % term + now_time + '.xlsx'
    result_data = save_excel_file(time_number, total_number, save_path)
    return result_data


if __name__ == "__main__":
    main()



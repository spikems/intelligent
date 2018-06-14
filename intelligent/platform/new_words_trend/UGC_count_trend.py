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


def bbs_key_word_es_query(start_time, end_time, term, query_type='day'):
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
                            "site_type": {"value": 2}

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
            es_count = es.search(index="community2,weixin_weibo", body=body, size=0)
            break
        except Exception as e:
            print e
    time_number = {}
    for i in es_count['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        time_number[time_record] = article_number
    return time_number


def bbs_all_es_query(start_time, end_time, query_type='week'):
    body = {"query": {"bool": {
                "must": [{"range": {
                    "post_time": {
                        "gte": "%s 00:00:00" % start_time,
                        "lte": "%s 00:00:00" % end_time
                    }}},
                    {
                        "term": {
                            "site_type": {"value": 2}
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
            es_count = es.search(index="community2,weixin_weibo", body=body, size=0)
            break
        except Exception as e:
            print e
    total_number = {}
    for i in es_count['aggregations']['date']['buckets'][:-1]:
        time_record = i['key_as_string'].split()[0]
        article_number = i['doc_count']
        total_number[time_record] = article_number
    return total_number


def weibo_key_word_es_query(start_time, end_time, term, query_type='week'):
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
                            "site_id": {"value": 2}

                        }}],
                        "must_not": [
                            {"term": {
                                "is_kol": {
                                    "value": "T"
                                }
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


def weibo_all_es_query(start_time, end_time, query_type='week'):
    body = {"query": {"bool": {
                "must": [{"range": {
                    "post_time": {
                        "gte": "%s 00:00:00" % start_time,
                        "lte": "%s 00:00:00" % end_time
                    }}},
                    {
                        "term": {
                            "site_id": {"value": 2}
                        }}],
                        "must_not": [
                            {"term": {
                                "is_kol": {
                                    "value": "T"
                                }
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


def app_key_word_es_query(start_time, end_time, term, query_type='week'):
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
                            "site_type": {"value": 15}

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


def app_all_es_query(start_time, end_time, query_type='week'):
    body = {"query": {"bool": {
                "must": [{"range": {
                    "post_time": {
                        "gte": "%s 00:00:00" % start_time,
                        "lte": "%s 00:00:00" % end_time
                    }}},
                    {
                        "term": {
                            "site_type": {"value": 15}
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
    frequency_data = {}  # 保存频率数据
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


def ugc_main(save_excel_path, term='', query_type='day', time_span=100):
    if not term:
        return {'ratio': [], 'frequency': []}
    date_time = datetime.datetime.now()
    end_time = ((date_time - datetime.timedelta(days=0)).date())
    # start_time = str((date_time - datetime.timedelta(days=time_span)).date())
    start_time = ((date_time - datetime.timedelta(days=time_span)).date())  # 起始时间用时间间隔
    bbs_time_number = bbs_key_word_es_query(start_time, end_time, term, query_type=query_type)
    bbs_total_number = bbs_all_es_query(start_time, end_time, query_type=query_type)
    weibo_time_number = weibo_key_word_es_query(start_time, end_time, term, query_type=query_type)
    weibo_total_number = weibo_all_es_query(start_time, end_time, query_type=query_type)
    app_time_number = app_key_word_es_query(start_time, end_time, term, query_type=query_type)
    app_total_number = app_all_es_query(start_time, end_time, query_type=query_type)
    time_number = {}
    total_number = {}
    for time_record in bbs_time_number:
        time_number[time_record] = bbs_time_number[time_record] + \
                                    (weibo_time_number[time_record] if time_record in weibo_time_number else 0) + \
                                    (app_time_number[time_record] if time_record in app_time_number else 0)
    for time_record in bbs_time_number:
        total_number[time_record] = bbs_total_number[time_record] + \
                                    (weibo_total_number[time_record] if time_record in weibo_total_number else 0) \
                                    + (app_total_number[time_record] if time_record in app_total_number else 0)
    now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    save_path = save_excel_path + '/%s_UGC_' % term + now_time + '.xlsx'
    result_data = save_excel_file(time_number, total_number, save_path)
    return result_data


if __name__ == "__main__":
    main()



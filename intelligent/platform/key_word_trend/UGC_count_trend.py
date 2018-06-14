# -*- coding:utf-8 -*-
# 微信、微博KOL的计算
import logging
import os
import sys
import xlrd
import copy
import datetime
import json
import traceback
import xlsxwriter
from elasticsearch import helpers
from elasticsearch import Elasticsearch
reload(sys)
sys.setdefaultencoding('utf-8')
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径

es = Elasticsearch(["http://192.168.241.35:9200", "http://192.168.241.46:9200", "192.168.241.50:9201",
                    "http://192.168.241.47:9201"], sniffer_timeout=False, timeout=1000)


def bbs_key_word_es_query(start_time, end_time, should_body, query_type='week'):
    """
    查询论坛的数据
    :param start_time:
    :param end_time:
    :param term:
    :param query_type:
    :return:
    """
    body = {"query": {"bool": {
                "must": [{"range": {
                    "post_time": {
                        "gte": "%s 00:00:00" % start_time,
                        "lte": "%s 00:00:00" % end_time
                    }}},
                        {"terms":{"site_type": [2,15]}
                        }],
    "minimum_should_match": 1,
    "should":should_body
    }},
                "aggs": {
                    "date": {
                        "date_histogram": {
                            "field": "post_time",
                            "interval": "%s" % query_type
                        }
                    }
                }
            }
    print json.dumps(body)
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
                        "terms":
                            {"site_type": [2,15]}}]}},
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
                    {"query_string": {
                        "fields": [
                            "title",
                            "text"],
                        "query": "%s" % (term),
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
                    {"query_string": {
                        "fields": [
                            "title",
                            "text"],
                        "query": "%s" % (term)
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


def smoothing_process(sort_time, ratio_data, frequency_data):
    N = len(sort_time)  # N代表sort_time的长度
    # 首先进行线性处理
    out_ratio_data = {}
    out_frequency_data = {}
    out_ratio_data[sort_time[0]] = (3.0 * ratio_data[sort_time[0]] + 2.0 * ratio_data[sort_time[1]] + ratio_data[sort_time[2]] - ratio_data[sort_time[4]]) / 5
    out_frequency_data[sort_time[0]] = (3 * frequency_data[sort_time[0]] + 2 * frequency_data[sort_time[1]] + frequency_data[sort_time[2]] - frequency_data[sort_time[4]]) // 5

    out_ratio_data[sort_time[1]] = (4.0 * ratio_data[sort_time[0]] + 3.0 * ratio_data[sort_time[1]] + 2.0 * ratio_data[sort_time[2]] + ratio_data[sort_time[3]]) / 10
    out_frequency_data[sort_time[1]] = (4 * frequency_data[sort_time[0]] + 3 * frequency_data[sort_time[1]] + 2 * frequency_data[sort_time[2]] + frequency_data[sort_time[3]]) // 10

    for i in range(2, N-2):
        out_ratio_data[sort_time[i]] = (ratio_data[sort_time[i-2]] + ratio_data[sort_time[i-1]] + ratio_data[sort_time[i]] + ratio_data[sort_time[i+1]] + ratio_data[sort_time[i+2]]) / 5
        out_frequency_data[sort_time[i]] = (frequency_data[sort_time[i-2]] + frequency_data[sort_time[i-1]] + frequency_data[sort_time[i]] + frequency_data[sort_time[i+1]] + frequency_data[sort_time[i+2]]) // 5

    out_ratio_data[sort_time[N-2]] = (4.0 * ratio_data[sort_time[N-1]] + 3.0 * ratio_data[sort_time[N-2]] + 2.0 * ratio_data[sort_time[N-3]] + ratio_data[sort_time[N-4]]) / 10
    out_frequency_data[sort_time[N-2]] = (4 * frequency_data[sort_time[N-1]] + 3 * frequency_data[sort_time[N-2]] + 2 * frequency_data[sort_time[N-3]] + frequency_data[sort_time[N-4]]) // 10

    out_ratio_data[sort_time[N-1]] = (3.0 * ratio_data[sort_time[N-1]] + 2.0 * ratio_data[sort_time[N-2]] + ratio_data[sort_time[N-3]] - ratio_data[sort_time[N-5]]) / 5
    out_frequency_data[sort_time[N-1]] = (3 * frequency_data[sort_time[N-1]] + 2 * frequency_data[sort_time[N-2]] + frequency_data[sort_time[N-3]] - frequency_data[sort_time[N-5]]) // 5

    # 利用二次函数拟合平滑
    in_r_data = out_ratio_data
    in_f_data = out_frequency_data
    out_r_data = {}
    out_f_data = {}
    out_r_data[sort_time[0]] = (31.0*in_r_data[sort_time[0]] + 9.0*in_r_data[sort_time[1]] - 3.0*in_r_data[sort_time[2]] - 5.0*in_r_data[sort_time[3]] + 3.0*in_r_data[sort_time[4]]) / 35.0
    out_f_data[sort_time[0]] = (31* in_f_data[sort_time[0]] + 9 * in_f_data[sort_time[1]] - 3 * in_f_data[sort_time[2]] - 5 * in_f_data[sort_time[3]] + 3 * in_f_data[sort_time[4]]) // 35

    out_r_data[sort_time[1]] = (9.0 * in_r_data[sort_time[0]] + 13.0 * in_r_data[sort_time[1]] + 12.0 * in_r_data[sort_time[2]] + 6.0 * in_r_data[sort_time[3]] - 5.0 * in_r_data[sort_time[4]]) / 35.0
    out_f_data[sort_time[1]] = (9*in_f_data[sort_time[0]] + 13*in_f_data[sort_time[1]] + 12*in_f_data[sort_time[2]] + 6*in_f_data[sort_time[3]] - 5*in_f_data[sort_time[4]]) / 35

    for i in range(2, N-2):
        out_r_data[sort_time[i]] = (-3.0*in_r_data[sort_time[i-2]]+in_r_data[sort_time[i+2]]+12.0*in_r_data[sort_time[i-1]]+in_r_data[sort_time[i+1]]+17.0*in_r_data[sort_time[i]]) / 35.0
        out_f_data[sort_time[i]] = (-3*in_f_data[sort_time[i-2]]+in_f_data[sort_time[i+2]]+12*in_f_data[sort_time[i-1]]+in_f_data[sort_time[i+1]]+17*in_f_data[sort_time[i]]) // 35

    out_r_data[sort_time[N-2]] = (9.0 * in_r_data[sort_time[N-1]] + 13.0 * in_r_data[sort_time[N-2]] + 12.0 * in_r_data[sort_time[N-3]] + 6.0 * in_r_data[sort_time[N-4]] - 5.0 * in_r_data[sort_time[N-5]]) / 35.0
    out_f_data[sort_time[N-2]] = (9 * in_f_data[sort_time[N-1]] + 13 * in_f_data[sort_time[N-2]] + 12 * in_f_data[sort_time[N-3]] + 6 * in_f_data[sort_time[N-4]] - 5 * in_f_data[sort_time[N-5]]) / 35

    out_r_data[sort_time[N-1]] = (31.0 * in_r_data[sort_time[N-1]] + 9.0 * in_r_data[sort_time[N-2]] - 3.0 * in_r_data[sort_time[N-3]] - 5.0 * in_r_data[sort_time[N-4]] + 3.0 * in_r_data[sort_time[N-5]]) / 35.0
    out_f_data[sort_time[N-1]] = (31 * in_f_data[sort_time[N-1]] + 9 * in_f_data[sort_time[N-2]] - 3 * in_f_data[sort_time[N-3]] - 5 * in_f_data[sort_time[N-4]] + 3 * in_f_data[sort_time[N-5]]) // 35

    # 利用三次函数的拟合平滑
    in_r_data = copy.deepcopy(out_r_data)
    in_f_data = copy.deepcopy(out_f_data)
    out_r_data = {}
    out_f_data = {}

    out_r_data[sort_time[0]] = (69.0*in_r_data[sort_time[0]] + 4.0*in_r_data[sort_time[1]] - 6.0*in_r_data[sort_time[2]] + 4.0*in_r_data[sort_time[3]] - in_r_data[sort_time[4]]) / 70.0
    out_f_data[sort_time[0]] = (69*in_f_data[sort_time[0]] + 4*in_f_data[sort_time[1]] - 6*in_f_data[sort_time[2]] + 4*in_f_data[sort_time[3]] - in_f_data[sort_time[4]]) // 70

    out_r_data[sort_time[1]] = (2.0 * in_r_data[sort_time[0]] + 27.0 * in_r_data[sort_time[1]] + 12.0* in_r_data[sort_time[2]] - 8.0 * in_r_data[sort_time[3]] + 2.0 * in_r_data[sort_time[4]]) / 35.0
    out_f_data[sort_time[1]] = (2*in_f_data[sort_time[0]] + 27*in_f_data[sort_time[1]] + 12*in_f_data[sort_time[2]] - 8*in_f_data[sort_time[3]] + 2*in_f_data[sort_time[4]]) / 35

    for i in range(2, N-2):
        out_r_data[sort_time[i]] = (-3.0 * in_r_data[sort_time[i - 2]] + in_r_data[sort_time[i + 2]] + 12.0* in_r_data[sort_time[i - 1]] + in_r_data[sort_time[i + 1]] + 17.0 * in_r_data[sort_time[i]]) / 35.0
        out_f_data[sort_time[i]] = (-3 * in_f_data[sort_time[i - 2]] + in_f_data[sort_time[i + 2]] + 12 * in_f_data[sort_time[i - 1]] + in_f_data[sort_time[i + 1]] + 17 * in_f_data[sort_time[i]]) // 35

    out_r_data[sort_time[N - 2]] = (2.0 * in_r_data[sort_time[N - 1]] + 27.0 * in_r_data[sort_time[N - 2]] + 12.0*in_r_data[sort_time[N - 3]] - 8.0 * in_r_data[sort_time[N - 4]] + 2.0 * in_r_data[sort_time[N - 5]]) / 35.0
    out_f_data[sort_time[N - 2]] = (2 * in_f_data[sort_time[N - 1]] + 27 * in_f_data[sort_time[N - 2]] + 12 * in_f_data[sort_time[N - 3]] - 8 * in_f_data[sort_time[N - 4]] + 2 * in_f_data[sort_time[N - 5]]) / 35

    out_r_data[sort_time[N - 1]] = (69.0 * in_r_data[sort_time[N - 1]] + 4.0 * in_r_data[sort_time[N - 2]] - 6.0*in_r_data[sort_time[N - 3]] + 4.0 * in_r_data[sort_time[N - 4]] - in_r_data[sort_time[N - 5]]) / 70.0
    out_f_data[sort_time[N - 1]] = (69 * in_f_data[sort_time[N - 1]] + 4 * in_f_data[sort_time[N - 2]] - 6 * in_f_data[sort_time[N - 3]] + 4 * in_f_data[sort_time[N - 4]] - in_f_data[sort_time[N - 5]]) // 70

    return out_r_data, out_f_data


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
    mean_num = 30
    sort_time = sort_time[::-1]  # 将日期从后往前排列
    for n in range(len(sort_time)):  # 抛出最开始的五个数据
        if total_number[sort_time[n]] <= 0:
            total_number[sort_time[n]] = 1
        sheet.write(i_row, 0, sort_time[n])  # 必须为unicode
        sheet.write(i_row, 1, int(time_number[sort_time[n]]))
        sheet.write(i_row, 2, int(total_number[sort_time[n]]))
        sheet.write(i_row, 3, float(time_number[sort_time[n]]) / float(total_number[sort_time[n]]))
        # all_frequency_number = 0  # 5个数据的频数之和
        # all_ratio_number = 0  # 5个数据的比率之和
        # for i in range(mean_num):  # 获取后5数据总和
        #     all_frequency_number += int(time_number[sort_time[n + i]])
        #     all_ratio_number += float(time_number[sort_time[n + i]]) / float(total_number[sort_time[n + i]])
        # ratio_data[sort_time[n]] = all_ratio_number / float(mean_num)
        # frequency_data[sort_time[n]] = all_frequency_number // mean_num
        ratio_data[sort_time[n]] = float(time_number[sort_time[n]]) / float(total_number[sort_time[n]])
        frequency_data[sort_time[n]] = int(time_number[sort_time[n]])
        i_row += 1
    result_r, result_f = smoothing_process(sort_time, ratio_data, frequency_data)
    result_data['ratio'] = result_r
    result_data['frequency'] = result_f
    workbook.close()
    return result_data


def ugc_main(save_excel_path, term,should_body, start_time,query_type='week', time_span=365):
    date_time = datetime.datetime.now()
    end_time = ((date_time - datetime.timedelta(days=0)).date())
    # start_time = str((date_time - datetime.timedelta(days=time_span)).date())
    time_number = bbs_key_word_es_query(start_time, end_time, should_body, query_type=query_type)
    total_number = bbs_all_es_query(start_time, end_time, query_type=query_type)
    # weibo_time_number = weibo_key_word_es_query(start_time, end_time, term, query_type=query_type)
    # weibo_total_number = weibo_all_es_query(start_time, end_time, query_type=query_type)
    # app_time_number = app_key_word_es_query(start_time, end_time, term, query_type=query_type)
    # app_total_number = app_all_es_query(start_time, end_time, query_type=query_type)
    # for time_record in bbs_time_number:
    #     time_number[time_record] = bbs_time_number[time_record] + \
    #                                 (weibo_time_number[time_record] if time_record in weibo_time_number else 0) + \
    #                                 (app_time_number[time_record] if time_record in app_time_number else 0)
    # for time_record in bbs_time_number:
    #     total_number[time_record] = bbs_total_number[time_record] + \
    #                                 (weibo_total_number[time_record] if time_record in weibo_total_number else 0) \
    #                                 + (app_total_number[time_record] if time_record in app_total_number else 0)
    now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    save_path = save_excel_path + '/%s_UGC_' % term + now_time + '.xlsx'
    result_data = save_excel_file(time_number, total_number, save_path)
    return result_data


if __name__ == "__main__":
    main()



# -*- coding:utf-8 -*-
# -*- coding:utf-8 -*-
import logging
import os
import sys
import json
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
                    "http://192.168.241.47:9201"], sniffer_timeout=False, timeout=1000)


def key_word_es_query(start_time, end_time, should_body, query_type='week'):
    """
    search for news for elasticsearch
    :param start_time:
    :param end_time:
    :param should_body:
    :param query_type:
    :return:
    """
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
        "minimum_should_match": 1,
        "should":should_body,
        "must_not": [{
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
    # print json.dumps(body)
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
    # print 'es_count',es_count
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


def smoothing_process(sort_time, ratio_data, frequency_data):
    N = len(sort_time)  # N代表sort_time的长度
    # 首先进行线性处理
    out_ratio_data = {}
    out_frequency_data = {}
    out_ratio_data[sort_time[0]] = (3.0 * ratio_data[sort_time[0]] + 2.0 * ratio_data[sort_time[1]] + ratio_data[
        sort_time[2]] - ratio_data[sort_time[4]]) / 5
    out_frequency_data[sort_time[0]] = (3 * frequency_data[sort_time[0]] + 2 * frequency_data[sort_time[1]] +
                                        frequency_data[sort_time[2]] - frequency_data[sort_time[4]]) // 5

    out_ratio_data[sort_time[1]] = (4.0 * ratio_data[sort_time[0]] + 3.0 * ratio_data[sort_time[1]] + 2.0 * ratio_data[
        sort_time[2]] + ratio_data[sort_time[3]]) / 10
    out_frequency_data[sort_time[1]] = (4 * frequency_data[sort_time[0]] + 3 * frequency_data[sort_time[1]] + 2 *
                                    frequency_data[sort_time[2]] + frequency_data[sort_time[3]]) // 10

    for i in range(2, N-2):
        out_ratio_data[sort_time[i]] = (ratio_data[sort_time[i - 2]] + ratio_data[sort_time[i - 1]] + ratio_data[
            sort_time[i]] + ratio_data[sort_time[i + 1]] + ratio_data[sort_time[i + 2]]) / 5
        out_frequency_data[sort_time[i]] = (frequency_data[sort_time[i - 2]] + frequency_data[sort_time[i - 1]] +
                                            frequency_data[sort_time[i]] + frequency_data[sort_time[i + 1]] +
                                            frequency_data[sort_time[i + 2]]) // 5

    out_ratio_data[sort_time[N - 2]] = (4.0 * ratio_data[sort_time[N - 1]] + 3.0 * ratio_data[sort_time[N - 2]] + 2.0 *
                                    ratio_data[sort_time[N - 3]] + ratio_data[sort_time[N - 4]]) / 10
    out_frequency_data[sort_time[N - 2]] = (
                                       4 * frequency_data[sort_time[N - 1]] + 3 * frequency_data[sort_time[N - 2]] + 2 *
                                       frequency_data[sort_time[N - 3]] + frequency_data[sort_time[N - 4]]) // 10

    out_ratio_data[sort_time[N - 1]] = (3.0 * ratio_data[sort_time[N - 1]] + 2.0 * ratio_data[sort_time[N - 2]] +
                                        ratio_data[sort_time[N - 3]] - ratio_data[sort_time[N - 5]]) / 5
    out_frequency_data[sort_time[N - 1]] = (
                                           3 * frequency_data[sort_time[N - 1]] + 2 * frequency_data[sort_time[N - 2]] +
                                           frequency_data[sort_time[N - 3]] - frequency_data[sort_time[N - 5]]) // 5

    # 利用二次函数拟合平滑
    in_r_data = out_ratio_data
    in_f_data = out_frequency_data
    out_r_data = {}
    out_f_data = {}
    out_r_data[sort_time[0]] = (31.0 * in_r_data[sort_time[0]] + 9.0 * in_r_data[sort_time[1]] - 3.0 * in_r_data[
        sort_time[2]] - 5.0 * in_r_data[sort_time[3]] + 3.0 * in_r_data[sort_time[4]]) / 35.0
    out_f_data[sort_time[0]] = (31 * in_f_data[sort_time[0]] + 9 * in_f_data[sort_time[1]] - 3 * in_f_data[
        sort_time[2]] - 5 * in_f_data[sort_time[3]] + 3 * in_f_data[sort_time[4]]) // 35

    out_r_data[sort_time[1]] = (9.0 * in_r_data[sort_time[0]] + 13.0 * in_r_data[sort_time[1]] + 12.0 * in_r_data[
        sort_time[2]] + 6.0 * in_r_data[sort_time[3]] - 5.0 * in_r_data[sort_time[4]]) / 35.0
    out_f_data[sort_time[1]] = (9 * in_f_data[sort_time[0]] + 13 * in_f_data[sort_time[1]] + 12 * in_f_data[
        sort_time[2]] + 6 * in_f_data[sort_time[3]] - 5 * in_f_data[sort_time[4]]) / 35

    for i in range(2, N-2):
        out_r_data[sort_time[i]] = (-3.0 * in_r_data[sort_time[i - 2]] + in_r_data[sort_time[i + 2]] + 12.0 * in_r_data[
            sort_time[i - 1]] + in_r_data[sort_time[i + 1]] + 17.0 * in_r_data[sort_time[i]]) / 35.0
        out_f_data[sort_time[i]] = (-3 * in_f_data[sort_time[i - 2]] + in_f_data[sort_time[i + 2]] + 12 * in_f_data[
            sort_time[i - 1]] + in_f_data[sort_time[i + 1]] + 17 * in_f_data[sort_time[i]]) // 35

    out_r_data[sort_time[N - 2]] = (9.0 * in_r_data[sort_time[N - 1]] + 13.0 * in_r_data[sort_time[N - 2]] + 12.0 *
                                    in_r_data[sort_time[N - 3]] + 6.0 * in_r_data[sort_time[N - 4]] - 5.0 * in_r_data[
                                        sort_time[N - 5]]) / 35.0
    out_f_data[sort_time[N - 2]] = (9 * in_f_data[sort_time[N - 1]] + 13 * in_f_data[sort_time[N - 2]] + 12 * in_f_data[
        sort_time[N - 3]] + 6 * in_f_data[sort_time[N - 4]] - 5 * in_f_data[sort_time[N - 5]]) / 35

    out_r_data[sort_time[N - 1]] = (31.0 * in_r_data[sort_time[N - 1]] + 9.0 * in_r_data[sort_time[N - 2]] - 3.0 *
                                    in_r_data[sort_time[N - 3]] - 5.0 * in_r_data[sort_time[N - 4]] + 3.0 * in_r_data[
                                        sort_time[N - 5]]) / 35.0
    out_f_data[sort_time[N - 1]] = (31 * in_f_data[sort_time[N - 1]] + 9 * in_f_data[sort_time[N - 2]] - 3 * in_f_data[
        sort_time[N - 3]] - 5 * in_f_data[sort_time[N - 4]] + 3 * in_f_data[sort_time[N - 5]]) // 35

    # 利用三次函数的拟合平滑
    in_r_data = copy.deepcopy(out_r_data)
    in_f_data = copy.deepcopy(out_f_data)
    out_r_data = {}
    out_f_data = {}

    out_r_data[sort_time[0]] = (69.0 * in_r_data[sort_time[0]] + 4.0 * in_r_data[sort_time[1]] - 6.0 * in_r_data[
        sort_time[2]] + 4.0 * in_r_data[sort_time[3]] - in_r_data[sort_time[4]]) / 70.0
    out_f_data[sort_time[0]] = (69 * in_f_data[sort_time[0]] + 4 * in_f_data[sort_time[1]] - 6 * in_f_data[
        sort_time[2]] + 4 * in_f_data[sort_time[3]] - in_f_data[sort_time[4]]) // 70

    out_r_data[sort_time[1]] = (2.0 * in_r_data[sort_time[0]] + 27.0 * in_r_data[sort_time[1]] + 12.0 * in_r_data[
        sort_time[2]] - 8.0 * in_r_data[sort_time[3]] + 2.0 * in_r_data[sort_time[4]]) / 35.0
    out_f_data[sort_time[1]] = (2 * in_f_data[sort_time[0]] + 27 * in_f_data[sort_time[1]] + 12 * in_f_data[
        sort_time[2]] - 8 * in_f_data[sort_time[3]] + 2 * in_f_data[sort_time[4]]) / 35

    for i in range(2, N-2):
        out_r_data[sort_time[i]] = (-3.0 * in_r_data[sort_time[i - 2]] + in_r_data[sort_time[i + 2]] + 12.0 * in_r_data[
            sort_time[i - 1]] + in_r_data[sort_time[i + 1]] + 17.0 * in_r_data[sort_time[i]]) / 35.0
        out_f_data[sort_time[i]] = (-3 * in_f_data[sort_time[i - 2]] + in_f_data[sort_time[i + 2]] + 12 * in_f_data[
            sort_time[i - 1]] + in_f_data[sort_time[i + 1]] + 17 * in_f_data[sort_time[i]]) // 35

    out_r_data[sort_time[N - 2]] = (2.0 * in_r_data[sort_time[N - 1]] + 27.0 * in_r_data[sort_time[N - 2]] + 12.0 *
                                    in_r_data[sort_time[N - 3]] - 8.0 * in_r_data[sort_time[N - 4]] + 2.0 * in_r_data[
                                        sort_time[N - 5]]) / 35.0
    out_f_data[sort_time[N - 2]] = (2 * in_f_data[sort_time[N - 1]] + 27 * in_f_data[sort_time[N - 2]] + 12 * in_f_data[
        sort_time[N - 3]] - 8 * in_f_data[sort_time[N - 4]] + 2 * in_f_data[sort_time[N - 5]]) / 35

    out_r_data[sort_time[N - 1]] = (69.0 * in_r_data[sort_time[N - 1]] + 4.0 * in_r_data[sort_time[N - 2]] - 6.0 *
                                    in_r_data[sort_time[N - 3]] + 4.0 * in_r_data[sort_time[N - 4]] - in_r_data[
                                        sort_time[N - 5]]) / 70.0
    out_f_data[sort_time[N - 1]] = (69 * in_f_data[sort_time[N - 1]] + 4 * in_f_data[sort_time[N - 2]] - 6 * in_f_data[
            sort_time[N - 3]] + 4 * in_f_data[sort_time[N - 4]] - in_f_data[sort_time[N - 5]]) // 70
    return out_r_data, out_f_data


def save_excel_file(time_number, total_number, save_path):
    """
    result_data is a dict ;key is radio and frequency ;values is
    :param time_number:
    :param total_number:
    :param save_path:
    :return:
    """
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
        if total_number[sort_time[n]] <= 0:
            total_number[sort_time[n]] = 1
        sheet.write(i_row, 0, sort_time[n])  # 必须为unicode
        sheet.write(i_row, 1, int(time_number[sort_time[n]]))
        sheet.write(i_row, 2, int(total_number[sort_time[n]]))
        sheet.write(i_row, 3, float(time_number[sort_time[n]])/float(total_number[sort_time[n]]))
        # all_frequency_number = 0   # 5个数据的频数之和
        # all_ratio_number = 0    # 5个数据的比率之和
        # for i in range(mean_num):  # 获取后5数据总和
        #     all_frequency_number += int(time_number[sort_time[n+i]])
        #     all_ratio_number += float(time_number[sort_time[n+i]]) / float(total_number[sort_time[n+i]])
        # ratio_data[sort_time[n]] = all_ratio_number / float(mean_num)
        # frequency_data[sort_time[n]] = all_frequency_number // mean_num
        ratio_data[sort_time[n]] = float(time_number[sort_time[n]]) / float(total_number[sort_time[n]])
        frequency_data[sort_time[n]] = int(time_number[sort_time[n]])
        i_row += 1
    result_r, result_f = smoothing_process(sort_time, ratio_data, frequency_data)
    result_data['ratio'] = result_r
    result_data['frequency'] = result_f
    workbook.close()
    # print 'result_data',result_data
    return result_data


# def process_data(term, result_data):
#     time_data = copy.deepcopy(result_data.keys())
#     time_data.sort()
#     x_list = []
#     y_list = []
#     for t_d in time_data:
#         x_list.append(t_d)
#         y_list.append(result_data[t_d] if t_d in result_data else 0)
#     title = 'news类 \"' + term + '\" 趋势'
#     save_path = term + 'news_' + '.png'
#     plot_chart(x_list, y_list, title, save_path)


def news_main(save_excel_path, term,should_body,start_time,query_type='week', time_span=365):
    date_time = datetime.datetime.now()
    end_time = ((date_time - datetime.timedelta(days=0)).date())
    # start_time = str((date_time - datetime.timedelta(days=time_span)).date())
    time_number = key_word_es_query(start_time, end_time, should_body, query_type=query_type)  # 搜索关键词的每周文章数据
    total_number = all_es_query(start_time, end_time, query_type=query_type)        # 搜索每周总文章数据
    now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    save_path = save_excel_path + '/%s_news_' % term + now_time +'.xlsx'
    result_data = save_excel_file(time_number, total_number, save_path)
    # process_data(term, result_data)
    return result_data

if __name__ == "__main__":
    pass



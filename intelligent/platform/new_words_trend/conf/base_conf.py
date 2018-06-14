# -*- coding:utf-8 -*-
import copy
# 前端传参各个参数的范围
time_interval = ['week', 'day']
result_type = ['all', 'ratio', 'frequency']


def statical_result(interval_time, news_result_dict, pgc_result_dict, ugc_result_dict, time_list):
    N = len(time_list)
    result_str_list = []
    # 上周数据对比
    now_del, last_del = (1, 8)
    if interval_time == 'week':
        now_del, last_del = (1, 2)
    print now_del, last_del
    news_now_week_number = news_result_dict[time_list[N - now_del]]  # 最近七天数据
    news_last_week_number = news_result_dict[time_list[N - last_del]]  # 最近7-14天数据
    pgc_now_week_number = pgc_result_dict[time_list[N - now_del]]  # 最近七天数据
    pgc_last_week_number = pgc_result_dict[time_list[N - last_del]]  # 最近7-14天数据
    ugc_now_week_number = ugc_result_dict[time_list[N - now_del]]  # 最近七天数据
    ugc_last_week_number = ugc_result_dict[time_list[N - last_del]]  # 最近7-14天数据
    # 获取历史最高数据
    news_sort_dict = sorted(news_result_dict.items(), key=lambda item: item[1], reverse=True)
    pgc_sort_dict = sorted(pgc_result_dict.items(), key=lambda item: item[1], reverse=True)
    ugc_sort_dict = sorted(ugc_result_dict.items(), key=lambda item: item[1], reverse=True)
    news_max_time, news_max_number = news_sort_dict[0]  # news 最高7天的数据
    pgc_max_time, pgc_max_number = pgc_sort_dict[0]
    ugc_max_time, ugc_max_number = ugc_sort_dict[0]
    # 输入出结论, 与上周数据对比
    news_now_week_number = news_now_week_number if news_now_week_number > 1 else 1
    news_last_week_number = news_last_week_number if news_last_week_number > 1 else 1
    news_max_number = news_max_number if news_max_number > 1 else 1

    pgc_now_week_number = pgc_now_week_number if pgc_now_week_number > 1 else 1
    pgc_last_week_number = pgc_last_week_number if pgc_last_week_number > 1 else 1
    pgc_max_number = pgc_max_number if pgc_max_number > 1 else 1

    ugc_now_week_number = ugc_now_week_number if ugc_now_week_number > 1 else 1
    ugc_last_week_number = ugc_last_week_number if ugc_last_week_number > 1 else 1
    ugc_max_number = ugc_max_number if ugc_max_number > 1 else 1

    result_str_list.append("news类与上周环比增长: %.2f" % (
        (float(news_now_week_number - news_last_week_number) / news_last_week_number) * 100) + '%'
                           if news_now_week_number > news_last_week_number
                           else "news类与上周环比下降: %.2f" % (
        (float(news_last_week_number - news_now_week_number) / news_last_week_number) * 100) + '%')

    result_str_list.append("PGC类与上周环比增长: %.2f" % (
        (float(pgc_now_week_number - pgc_last_week_number) / pgc_last_week_number) * 100) + '%'
                           if pgc_now_week_number > pgc_last_week_number
                           else "PGC类与上周环比下降: %.2f" % (
        (float(pgc_last_week_number - pgc_now_week_number) / pgc_last_week_number) * 100) + '%')

    result_str_list.append("UGC类与上周环比增长: %.2f" % (
        (float(ugc_now_week_number - ugc_last_week_number) / ugc_last_week_number) * 100) + '%'
                           if ugc_now_week_number > ugc_last_week_number
                           else "UGC类与上周环比下降: %.2f" % (
        (float(ugc_last_week_number - ugc_now_week_number) / ugc_last_week_number) * 100) + '%')
    # 与最高时期对比
    result_str_list.append("news类最高数据日期为: %s" % news_max_time + ", 与之环比下降: %.2f" % (
        (float(news_max_number - news_now_week_number) / news_max_number) * 100) + '%')

    result_str_list.append("PGC类最高数据日期为: %s" % pgc_max_time + ", 与之环比下降: %.2f" % (
        (float(pgc_max_number - pgc_now_week_number) / pgc_max_number) * 100) + '%')

    result_str_list.append("UGC类最高数据日期为: %s" % ugc_max_time + ", 与之环比下降: %.2f" % (
        (float(ugc_max_number - ugc_now_week_number) / ugc_max_number) * 100) + '%')

    return result_str_list


def month_chain(news_number_list, pgc_number_list, ugc_number_list, time_list):
    '''
    用于月环比的数据
    '''

    result_str_list = []  # 保存返回结果
    news_result_dict, pgc_result_dict, ugc_result_dict = {}, {}, {}
    for i in range(len(time_list)):
        news_result_dict[time_list[i]] = news_number_list[i]
        pgc_result_dict[time_list[i]] = pgc_number_list[i]
        ugc_result_dict[time_list[i]] = ugc_number_list[i]
    time_data_dict = {}  # 存放 {'2017-06': [], ''}
    for time_data in time_list:
        year_month = '-'.join(time_data.split('-')[:-1])   # 把 2017-06-05改变为 2017-06
        time_data_dict[year_month] = time_data_dict.get(year_month, []) + [time_data]
    sort_time_data_dict = copy.deepcopy(time_data_dict.keys())  # 保存有序的列表
    sort_time_data_dict.sort()
    if len(time_data_dict[sort_time_data_dict[0]]) < 15:  # 如果第一个月份的天数不大于15，去除
        sort_time_data_dict.remove(sort_time_data_dict[0])
    if len(time_data_dict[sort_time_data_dict[-1]]) < 15:  # 如果最后一个月份的天数不大于15，去除
        sort_time_data_dict.remove(sort_time_data_dict[-1])
    # 用每个月的平均每天来代表
    news_result_month_number = {'max_num': ('', 0.0)}  # {'2017-06' : number1, 'max_num' : (月, 数字)}  用 max_num 保存最高月份和数目
    pgc_result_month_number = {'max_num': ('', 0.0)}
    ugc_result_month_number = {'max_num': ('', 0.0)}
    for month in sort_time_data_dict:
        news_month_all_number = 0
        pgc_month_all_number = 0
        ugc_month_all_number = 0
        for one_day in time_data_dict[month]:
            news_month_all_number += news_result_dict[one_day]
            pgc_month_all_number += pgc_result_dict[one_day]
            ugc_month_all_number += ugc_result_dict[one_day]
        news_result_month_number[month] = float(news_month_all_number) / len(time_data_dict[month])
        if news_result_month_number['max_num'][1] < news_result_month_number[month]:
            news_result_month_number['max_num'] = (month, news_result_month_number[month])

        pgc_result_month_number[month] = float(pgc_month_all_number) / len(time_data_dict[month])
        if pgc_result_month_number['max_num'][1] < pgc_result_month_number[month]:
            pgc_result_month_number['max_num'] = (month, pgc_result_month_number[month])

        ugc_result_month_number[month] = float(ugc_month_all_number) / len(time_data_dict[month])
        if ugc_result_month_number['max_num'][1] < ugc_result_month_number[month]:
            ugc_result_month_number['max_num'] = (month, ugc_result_month_number[month])

    # 对比上个月结果
    now_month = sort_time_data_dict[-1]
    last_month = sort_time_data_dict[-2]
    news_max_month = news_result_month_number['max_num'][0]
    pgc_max_month = pgc_result_month_number['max_num'][0]
    ugc_max_month = ugc_result_month_number['max_num'][0]
    news_result_month_number[now_month] = news_result_month_number[now_month] if news_result_month_number[now_month] > 1 else 1
    news_result_month_number[last_month] = news_result_month_number[last_month] if news_result_month_number[last_month] > 1 else 1
    news_result_month_number[news_max_month] = news_result_month_number[news_max_month] if news_result_month_number[news_max_month] > 1 else 1

    pgc_result_month_number[now_month] = pgc_result_month_number[now_month] if pgc_result_month_number[now_month] > 1 else 1
    pgc_result_month_number[last_month] = pgc_result_month_number[last_month] if pgc_result_month_number[last_month] > 1 else 1
    pgc_result_month_number[pgc_max_month] = pgc_result_month_number[pgc_max_month] if pgc_result_month_number[pgc_max_month] > 1 else 1

    ugc_result_month_number[now_month] = ugc_result_month_number[now_month] if ugc_result_month_number[now_month] > 1 else 1
    ugc_result_month_number[last_month] = ugc_result_month_number[last_month] if ugc_result_month_number[last_month] > 1 else 1
    ugc_result_month_number[ugc_max_month] = ugc_result_month_number[ugc_max_month] if ugc_result_month_number[ugc_max_month] > 1 else 1

    result_str_list.append("news类与上月环比增长: %.2f" % (
        (float(news_result_month_number[now_month] - news_result_month_number[last_month]) / news_result_month_number[last_month]) * 100) + '%'
                           if news_result_month_number[now_month] > news_result_month_number[last_month]
                           else "news类与上月环比下降: %.2f" % (
        (float(news_result_month_number[last_month] - news_result_month_number[now_month]) / news_result_month_number[last_month]) * 100) + '%')

    result_str_list.append("PGC类与上月环比增长: %.2f" % (
        (float(pgc_result_month_number[now_month] - pgc_result_month_number[last_month]) / pgc_result_month_number[last_month]) * 100) + '%'
                           if pgc_result_month_number[now_month] > pgc_result_month_number[last_month]
                           else "PGC类与上月环比下降: %.2f" % (
        (float(pgc_result_month_number[last_month] - pgc_result_month_number[now_month]) / pgc_result_month_number[last_month]) * 100) + '%')

    result_str_list.append("UGC类与上月环比增长: %.2f" % (
        (float(ugc_result_month_number[now_month] - ugc_result_month_number[last_month]) / ugc_result_month_number[last_month]) * 100) + '%'
                           if ugc_result_month_number[now_month] > ugc_result_month_number[last_month]
                           else "UGC类与上月环比下降: %.2f" % (
        (float(ugc_result_month_number[last_month] - ugc_result_month_number[now_month]) / ugc_result_month_number[last_month]) * 100) + '%')

    # 与最高时期对比

    result_str_list.append("news类最高数据日期为: %s" % news_max_month + ", 与之环比下降: %.2f" % (
        (float(news_result_month_number[news_max_month] - news_result_month_number[now_month]) / news_result_month_number[news_max_month]) * 100) + '%')


    result_str_list.append("PGC类最高数据日期为: %s" % pgc_max_month + ", 与之环比下降: %.2f" % (
        (float(pgc_result_month_number[pgc_max_month] - pgc_result_month_number[now_month]) / pgc_result_month_number[pgc_max_month]) * 100) + '%')


    result_str_list.append("UGC类最高数据日期为: %s" % ugc_max_month + ", 与之环比下降: %.2f" % (
        (float(ugc_result_month_number[ugc_max_month] - ugc_result_month_number[now_month]) / ugc_result_month_number[ugc_max_month]) * 100) + '%')

    return result_str_list
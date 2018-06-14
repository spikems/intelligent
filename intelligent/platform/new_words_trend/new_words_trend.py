# -*- coding:utf-8 -*-
import sys
import os
import copy
import logging
import datetime
import traceback
import xlsxwriter
from intelligent.common.util import singleton
from conf.base_conf import statical_result, month_chain
from intelligent.model.t_trend_words import WordsTrend
from intelligent.platform.new_words_trend.news_count_trend import news_main
from intelligent.platform.new_words_trend.PGC_count_trend import pgc_main
from intelligent.platform.new_words_trend.UGC_count_trend import ugc_main
from intelligent.platform.new_words_trend.tendency_chart import plot_chart
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径


@singleton
class TrendKeyWord(object):
    def __init__(self):
        self.display_dict = {'all': ['ratio', 'frequency'], 'ratio': ['ratio'], 'frequency': ['frequency']}
        self.sLogPath = '%s/../../../logs/platform.error' % project_path
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s : %(filename)s[line:%(lineno)d] : %(message)s',
                            filename=self.sLogPath)
        self.err_logger = logging.getLogger(__name__)

    def select_terms(self):
        # 从数据库中读取term的的数据
        try:
            dm_obj = WordsTrend()
            terms_list = dm_obj.queryAll()  # 获取所有的 需要查询的 word
            # dm_obj.set_type()   # 将查询的词在数据库中的状态修改为 1，代表已查询,  暂时不做修改
        except:
            error = "news_words_trend file error.  traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return terms_list

    def es_process_data(self, key_words_dict, time_interval='week', chain_interval_num=30):
        '''
        处理查询到的news类、PGC类、UGC类的各个数据
        :param key_words_dict: {term1:[word1, word2], term2:[word3, word4}
        :return:
        '''
        term_result_dict = {}  # 用来存放一个 term的全部数据
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
        save_excel_path = project_path + '/excel_data/' + now_time
        is_exist = os.path.exists(save_excel_path)
        if not is_exist:   # 判断当前路径是否存在
            os.makedirs(save_excel_path)   # 创建保存的目录
        for term in key_words_dict:
            try:
                one_news_result = {}  # 存放一个term的news结果
                one_pgc_result = {}   # 存放一个term的pgc结果
                one_ugc_result = {}   # 存放一个term的ugc结果
                two_news_result = {}  # 存放一个term的news结果
                two_pgc_result = {}  # 存放一个term的pgc结果
                two_ugc_result = {}  # 存放一个term的ugc结果
                for k_word in key_words_dict[term]:  # 遍历每一个词的同义词
                    print '查询%s的ES数据：' % k_word
                    # news_data 类型格式 {'ratio': {time:ratio_number} 'frequency':{time:frequency_number}}
                    news_data = news_main(save_excel_path, k_word, query_type=time_interval, time_span=(chain_interval_num*2+10))
                    pgc_data = pgc_main(save_excel_path, k_word, query_type=time_interval, time_span=(chain_interval_num*2+10))
                    ugc_data = ugc_main(save_excel_path, k_word, query_type=time_interval, time_span=(chain_interval_num*2+10))
                    print '查询%s成功' % k_word
                    for t_d in news_data['ratio']:  # 把不同k_word的news_data的number加起来
                        one_news_result[t_d] = one_news_result.get(t_d, 0) + (news_data['ratio'][t_d] if t_d in news_data['ratio'] else 0)
                    for t_d in pgc_data['ratio']:   # 同上累计pgc的数据
                        one_pgc_result[t_d] = one_pgc_result.get(t_d, 0) + (pgc_data['ratio'][t_d] if t_d in pgc_data['ratio'] else 0)
                    for t_d in ugc_data['ratio']:  # 同上累计ugc的数据
                        one_ugc_result[t_d] = one_ugc_result.get(t_d, 0) + (ugc_data['ratio'][t_d] if t_d in ugc_data['ratio'] else 0)

                    for t_d in news_data['frequency']:  # 把不同k_word的news_data的number加起来
                        two_news_result[t_d] = two_news_result.get(t_d, 0) + (news_data['frequency'][t_d] if t_d in news_data['frequency'] else 0)
                    for t_d in pgc_data['frequency']:   # 同上累计pgc的数据
                        two_pgc_result[t_d] = two_pgc_result.get(t_d, 0) + (pgc_data['frequency'][t_d] if t_d in pgc_data['frequency'] else 0)
                    for t_d in ugc_data['frequency']:  # 同上累计ugc的数据
                        two_ugc_result[t_d] = two_ugc_result.get(t_d, 0) + (ugc_data['frequency'][t_d] if t_d in ugc_data['frequency'] else 0)
                term_result_dict[term] = {'ratio': [one_news_result, one_pgc_result, one_ugc_result],
                                          'frequency': [two_news_result, two_pgc_result, two_ugc_result]}
            except Exception as e:
                error = "news_words_trend file error. traceback: %s" % traceback.format_exc()
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
                    pass
                    # 暂时不做画图出来
                    # save_path = output_path + '/%s' % term + '_' + type_display + '_' + time_interval + '_' + now_time + '.png'
                    # plot_chart(paint_data_dict[type_display][0], paint_data_dict[type_display][1], paint_data_dict[type_display][2], paint_data_dict[type_display][3],
                    #            term, save_path, type_display=type_display, interval_period=time_interval)
                except:
                    error = "news_words_trend file error. traceback: %s" % traceback.format_exc()
                    self.err_logger.error(error)
            result_term_data_dict[term] = paint_data_dict
        return result_term_data_dict

    def calculated_compare(self, term_date_dict, chain_interval_num=30):
        '''
        :param term_date_dict: {term: paint_data_dict}  paint_data_dict={'frequency':[time_list, news_number_list, pgc_number_list, ugc_number_list]}
        :param time_interval: 搜索的时间间隔： day以天为间隔，    week以week为间隔
        :param chain_interval_num: 环比类型, 周环比|月环比,  用天衡量， 月环比为30天，周环比为7天
        :return: result_str_list 得到判断结果
        '''
        result_term_str_dict = {}
        for term in term_date_dict:
            try:
                time_list = term_date_dict[term]["frequency"][0]
                news_number_list = term_date_dict[term]["frequency"][1]
                pgc_number_list = term_date_dict[term]["frequency"][2]
                ugc_number_list = term_date_dict[term]["frequency"][3]
                all_freq_dict = []  # 存放三个类别加起来的数据，格式：[日期1的总数，日期2的总数....]
                N = len(time_list)
                for i in range(N):
                    all_freq_dict.append(news_number_list[i] + pgc_number_list[i] + ugc_number_list[i])
                now_time_number = 0   # 代表当前月或者周的数据
                last_time_number = 0  # 代表上一个月或者周的数据
                for i in range(chain_interval_num):
                    now_time_number += (all_freq_dict[N-1-i] if N-1-i >= 0 else 0)  # 如果ES搜索的数据集还够30天，则多余的为0
                    last_time_number += (all_freq_dict[N-chain_interval_num - 1 - i] if N-chain_interval_num - 1 - i >= 0 else 0)
                result_term_str_dict[term] = (float(now_time_number - last_time_number) / \
                                             float(last_time_number if last_time_number > 0 else 1)) * 100   # 环比计算结果
            except Exception as e:
                error = "news_words_trend file error. traceback: %s" % traceback.format_exc()
                self.err_logger.error(error)
        return result_term_str_dict

    @staticmethod
    def sort_top_word(term_str_dict, chain_interval_num):
        '''
        :param term_str_dict: {'佛系': 8.0423}
        :return:
        '''
        term_result_list = []
        sort_term_data_list = sorted(term_str_dict.items(), key=lambda item: item[1], reverse=True)
        for term_data in sort_term_data_list[:30]:   # 获取top30
            result_str = "'%s'以%d天作为环比周期, 环比" % (term_data[0], chain_interval_num) + \
                         ('上升 %.2f' % term_data[1]  if term_data[1] >= 0 else '下降 %.2f' % (term_data[1] * -1)) + ' %'
            term_result_list.append((term_data[0], result_str))
        return term_result_list

    def save_word_result(self, output_path, term_result_list):
        try:
            now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
            save_path = output_path + '/result_' + now_time + '.xlsx'
            workbook = xlsxwriter.Workbook(save_path)
            sheet = workbook.add_worksheet('result')
            sheet.write(0, 0, u'趋势词')
            sheet.write(0, 1, u'环比结论')
            i_row = 1
            for term_result in term_result_list:
                sheet.write(i_row, 0, term_result[0])  # 必须为unicode
                sheet.write(i_row, 1, term_result[1])
                i_row += 1
            workbook.close()
        except Exception as e:
            error = "news_words_trend.save_word_result error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)

    def trend_main(self, time_interval, result_type, output_path, chain_interval_num):
        '''
        :param time_interval:  搜索的时间间隔： day以天为间隔，week以week为间隔
        :param result_type:   # 搜索的类型，'all'看全部， 'ratio'看比率，'frequency'看频率
        :param chain_type:  统计环比  'month'月环比   'week'周环比
        :param output_path:
        :return:
        '''
        terms_list = self.select_terms()
        if not terms_list:  # 如果查询词为空，返回False
            return False
        key_words_dict = {}  # 保存{term1:[term1,term1.2]}  这里term1和term1.2代表是term1的同义词，包括本身
        for term in terms_list:
            term = term.strip()
            if not term:   # 如果term是空
                continue
            es_words_list = [term]  # 目前没有同义词，只有本身term
            key_words_dict[term] = es_words_list  # 保存字典
        try:
            term_result_dict = self.es_process_data(key_words_dict, time_interval=time_interval, chain_interval_num=chain_interval_num)
            term_date_dict = self.paint_process_data(term_result_dict, self.display_dict[result_type], time_interval, output_path=output_path)
            term_str_dict = self.calculated_compare(term_date_dict, chain_interval_num)
            term_result_list = self.sort_top_word(term_str_dict, chain_interval_num)  # 统计TOP30结果
            self.save_word_result(output_path, term_result_list)    # 保存结果
        except Exception as e:
            error = "news_words_trend file error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
            return False
        return True


if __name__ == '__main__':
    time_interval = 'day'
    result_type = 'all'
    chain_interval_num = 30
    output_path = project_path + '/output'
    TrendKeyWord().trend_main(time_interval, result_type, output_path, chain_interval_num)
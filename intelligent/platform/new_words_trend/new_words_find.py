# -*- coding:utf-8 -*-
# 新词界面
import os
import logging
import traceback
import xlsxwriter
from dateutil.parser import parse
from datetime import datetime, timedelta
from intelligent.model.t_trend_words import WordsTrend
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径


class NewWordsFind(object):
    def __init__(self):
        self.jieba_word = {'n': '名词', 'nr': '人名', 'nz': '其它专名', 'ag': '形容词性语素', 'ad': '副形词', 'a': '形容词',
                           'b': '区别词', 'c': '连词', 'dg': '副语素', 'd': '副词', 'e': '叹词', 'f': '方位词', 'g': '语素',
                           'h': '前接成分', 'i': '成语', 'j': '简称略语', 'l': '习用语', 'm': '数词', 'ns': '地名', 'p': '介词',
                           'q': '量词', 'r': '代词', 's': '处所词', 't': '时间词', 'u': '助词', 'v': '动词', 'vn': '动名词',
                           'w': '标点符号', 'y': '语气词', 'z': '状态词'}
        self.sLogPath = '%s/../../../logs/platform.error' % project_path
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s : %(filename)s[line:%(lineno)d] : %(message)s',
                            filename=self.sLogPath)
        self.err_logger = logging.getLogger(__name__)

    def process_time(self, time_list):
        '''
            处理时间间隔逻辑
            :return:
        '''
        try:
            end_time = time_list[1]
            end_time_d = parse(end_time)
            end_time_str = str(end_time_d.date() + timedelta(days=1))
        except:
            error = "news_words_find.process_time error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return [time_list[0], end_time_str]

    def search_words(self, search_type, processed_time_list):
        '''
            从数据库查询数据
        :return: [[word1, industry1, word_sex], [], []]
        '''
        try:
            table_obj = WordsTrend()
            result_words_list = table_obj.query_trend_new_words(search_type, processed_time_list)
        except:
            error = "news_words_find.search_words error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return result_words_list

    def drop_words(self, result_words_list, drop_num=5):
        '''
            对应新词，将industry=5的数据删掉
        '''
        try:
            search_words_list = []
            for word_data in result_words_list:
                if word_data[1] != drop_num:
                    search_words_list.append(word_data)
        except:
            error = "news_words_find.drop_words error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return search_words_list

    def process_words_list(self, words_list):
        '''
            处理词性显示的问题
        :return:
        '''
        try:
            result_words_list = []   # [['竞答', '动词'], ['宝卡', '名词']]
            for word_data in words_list:
                if word_data[2] in self.jieba_word:  # 如果词性在里面有
                    word_gender = self.jieba_word[word_data[2]]
                    result_words_list.append([word_data[0], word_gender])
        except:
            error = "news_words_find.process_words_list error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return result_words_list

    def save_excel(self, search_type, result_words_list, output_path):   # 将数据存储到Excel中
        try:
            workbook = xlsxwriter.Workbook(output_path)
            sheet = workbook.add_worksheet('result')
            sheet.write(0, 0, u'新词列表' if search_type=='new' else u'趋势词列表')
            sheet.write(0, 1, u'词性列表')
            i_row = 1
            for term_result in result_words_list:
                sheet.write(i_row, 0, term_result[0] if type(term_result[0])== unicode else term_result[0].decode('utf-8'))  # 必须为unicode
                sheet.write(i_row, 1, term_result[1] if type(term_result[1])== unicode else term_result[1].decode('utf-8'))
                i_row += 1
            workbook.close()
        except:
            error = "news_words_find.save_excel error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)

    def run(self, search_type, time_list, output_path):
        try:
            processed_time_list = self.process_time(time_list)
            result_words_list = self.search_words(search_type, processed_time_list)
            if search_type == 'new':
                result_words_list = self.drop_words(result_words_list)
            result_words_list = self.process_words_list(result_words_list)
            self.save_excel(search_type, result_words_list, output_path)
        except:
            error = "news_words_find.run error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
            return []
        return result_words_list

if __name__ == '__main__':
    obj = NewWordsFind()
    search_type = 'new'
    time_list = ['2018-01-11', '2018-01-16']
    output_path = project_path + '/result.xlsx'
    obj.run(search_type, time_list, output_path)
# -*- coding:utf-8 -*-
import os
import re
import xlrd
import xlsxwriter
from intelligent.common.exldeal import XLSDeal
from intelligent.platform.discern_nature.conf.basic_conf import *
from intelligent.platform.discern_nature.conf.basic_tools import cut_input
from intelligent.platform.discern_nature.conf.basic_tools import dedup_near

# from intelligent.dm.project.discern_nature.nature_model_discern import DiscernModelNature
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径


class DiDiDiscernNature(object):
    def __init__(self):
        self.rule_data_path = project_path + '/conf/didi_filter_word.xlsx'
        self.filter_words = self.read_filter_data()
        self.origin_classification_rule = [u'sns', u'微博', u'论坛', u'问答']
        self.alnum_pattern = re.compile(r'^[\w \t]*//')  # 出现数字字母 //的情况
        self.biaoqing_pattern = re.compile((r'^(\[.{1,6}\])+//'))  # 出现表情
        self.pound_pattern = re.compile(ur'^\#.*滴滴.*\#')  # 话题中出现滴滴
        self.haha_pattern = re.compile(ur'^哈+//')  # 出现哈哈 //的情况
        self.url_pattern = re.compile(u'^(http|https)://[\w\t./ ]+?//')  # 出现链接//的情况
        self.didi_pattern = re.compile(ur'.*(滴滴|快车|顺风车|拼车|出租车|专车|司机|跑).*')  # 后续内容中出现滴滴

        # self.model = DiscernModelNature()

    def read_raw_data(self, raw_data_path):
        read_data = xlrd.open_workbook(raw_data_path)
        table = read_data.sheets()[0]
        result_data = {}
        for i in range(1, table.nrows):
            line = table.row_values(i)
            try:
                order_number = str(int(line[0]))
                origin_classification = line[1].strip() if type(line[1]) == unicode else str(line[2]).strip()
                title = line[2].strip() if type(line[2]) == unicode else str(line[2]).strip()
                document = line[3].strip() if type(line[3]) == unicode else str(line[3]).strip()
                author = line[4].strip() if type(line[4]) == unicode else str(line[4]).strip()
                supervision = line[5].strip() if type(line[5]) == unicode else str(line[5]).strip()
                one_data = [order_number, origin_classification, u''.join(title.lower().split()),
                            u''.join(document.lower().split()), author.lower(), supervision.lower()]
                result_data[i] = one_data
            except Exception as e:
                print line
                print e
        # result_data格式：{id1:one_data1, id2:one_data2}
        return result_data

    def read_filter_data(self):
        read_data = xlrd.open_workbook(self.rule_data_path)
        table = read_data.sheets()[0]
        result_data = {}
        for i in range(1, table.nrows):
            line = table.row_values(i)
            start_rule_words = line[0].strip().lower()
            title_sns_words = line[1].strip().lower()     # 主题(sns)
            document_luntan_words = line[2].strip().lower()   # 摘要(论坛)
            document_weibo_words = line[3].strip().lower()  # 摘要(微博)
            if start_rule_words:
                result_data['start_rule_words'] = result_data.get('start_rule_words', []) + [start_rule_words]
            if title_sns_words:
                result_data['title_sns_words'] = result_data.get('title_sns_words', []) + [title_sns_words]
            if document_luntan_words:
                result_data['document_luntan_words'] = result_data.get('document_luntan_words', []) + [document_luntan_words]
            if document_weibo_words:
                result_data['document_weibo_words'] = result_data.get('document_weibo_words', []) + [document_weibo_words]
        return result_data

    @staticmethod
    def get_duplicate_list(list_data):  # 获取重复的列表数据
        content_data_list = [(list_data[x][2] + u',' + list_data[x][3][:40]) for x in list_data]
        cut_data_list = []
        for data in content_data_list:
            data = data.encode('utf-8')
            one_cut_data = cut_input(data)
            cut_data_list.append(one_cut_data)
        duplicate_list = dedup_near(cut_data_list, 7, 3)   # [ [重复数据组1], [数据组2], [数据组3], [数据组4] ]
        result_dup_list = []
        for d_l in duplicate_list:
            if len(d_l) > 1:  # 如果存在两条以上重复数据，保留一条不重复
                d_l.pop()
                result_dup_list.extend(d_l)
        result_dup_list = list(set(result_dup_list))
        return result_dup_list

    def rule_filter(self, list_data, duplicate_list):
        final_str_data = []  # 返回的最终结果
        for data_id in list_data:
            # 结构 [order_number, origin_classification, title, document, author, supervision]

            # 规则1：如果不是来源于[u'sns', u'微博', u'论坛', u'问答']
            if list_data[data_id][1].lower() not in self.origin_classification_rule:
                one_result = self.process_result(list_data[data_id], u'营销', u'来源')
                final_str_data.append(one_result)
                continue
            # 如果来源是微博，则根据微博单独处理[u'sns', u'微博', u'论坛', u'问答']
            if list_data[data_id][1].lower() == u'微博':
                # 开头内容的去除
                start_judge = False
                for word in self.filter_words['start_rule_words']:
                    if word == u'//':
                        alnum_result = self.alnum_pattern.match(list_data[data_id][3])
                        biaoqing_result = self.biaoqing_pattern.match(list_data[data_id][3])
                        if alnum_result:
                            one_result = self.process_result(list_data[data_id], u'营销', ur'字母\\(开头)')
                            final_str_data.append(one_result)
                            start_judge = True
                            break
                        if biaoqing_result:
                            one_result = self.process_result(list_data[data_id], u'营销', ur'表情\\(开头)')
                            final_str_data.append(one_result)
                            start_judge = True
                            break
                    elif word == u'#':
                        pound_result = self.pound_pattern.match(list_data[data_id][3])
                        if pound_result:
                            pos2 = list_data[data_id][3][2:].find(word)
                            print pos2
                            if pos2 < 40:   # 如果两个 # 之间的长度小于40，
                                didi_result = self.didi_pattern.match(list_data[data_id][3][(pos2+3):])
                                print didi_result
                                if not didi_result:  # 如果后面的内容中没有出现滴滴两个字
                                    one_result = self.process_result(list_data[data_id], u'营销', ur'#话题(开头)')
                                    final_str_data.append(one_result)
                                    start_judge = True
                                    break
                    elif word == u'链接//':   # 开头出现链接
                        url_pattern = self.url_pattern.match(list_data[data_id][3])
                        if url_pattern:
                            one_result = self.process_result(list_data[data_id], u'营销', u'链接\\(开头)')
                            final_str_data.append(one_result)
                            start_judge = True
                            break
                    elif word == u'哈//':
                        haha_pattern = self.haha_pattern.match(list_data[data_id][3])
                        if haha_pattern:
                            one_result = self.process_result(list_data[data_id], u'营销', u'哈\\(开头)')
                            final_str_data.append(one_result)
                            start_judge = True
                            break
                    else:
                        pos = list_data[data_id][3].find(word)
                        if pos == 0:
                            one_result = self.process_result(list_data[data_id], u'营销', word + u'(开头)')
                            final_str_data.append(one_result)
                            start_judge = True
                            break
                if start_judge:
                    continue

                # document中含有过滤词
                document_judge = False
                for word in self.filter_words['document_weibo_words']:
                    if word in list_data[data_id][3]:
                        one_result = self.process_result(list_data[data_id], u'营销', word + u'(微博摘要)')
                        final_str_data.append(one_result)
                        document_judge = True
                        break
                if document_judge:
                    continue

            # 如果来源是sns，  [u'sns', u'微博', u'论坛', u'问答']
            elif list_data[data_id][1].lower() == u'sns':
                # title中含有过滤词
                title_judge = False
                for word in self.filter_words['title_sns_words']:
                    if word in list_data[data_id][2]:
                        one_result = self.process_result(list_data[data_id], u'营销', word + u'(SNS主题)')
                        final_str_data.append(one_result)
                        title_judge = True
                        break
                if title_judge:
                    continue
            # 如果来源是论坛，  [u'sns', u'微博', u'论坛', u'问答']
            elif list_data[data_id][1].lower() == u'论坛':
                # document中含有过滤词
                document_judge = False
                for word in self.filter_words['document_luntan_words']:
                    if word in list_data[data_id][3]:
                        one_result = self.process_result(list_data[data_id], u'营销', word + u'(论坛摘要)')
                        final_str_data.append(one_result)
                        document_judge = True
                        break
                if document_judge:
                    continue

            # 规则0：如果order_number 在重复的数据列表里面，则判定为营销数据
            if data_id in duplicate_list:
                one_result = self.process_result(list_data[data_id], u'营销', u'重复')
                final_str_data.append(one_result)
                continue

            one_result = self.process_result(list_data[data_id], u'自然', u'')
            final_str_data.append(one_result)
        return final_str_data

    @staticmethod
    def process_result(data, result, according, dup_data_str=''):
        data.append(result)
        data.append(according)
        data.append(dup_data_str)
        return u'\t'.join(data).encode('utf-8')

    def run(self, raw_data_path, save_path):
        list_data = self.read_raw_data(raw_data_path)
        duplicate_list = self.get_duplicate_list(list_data)
        result_data = self.rule_filter(list_data, duplicate_list)
        excel_title = [u'序号', u'分类', u'主题', u'摘要', u'作者', u'监控对象', u'(滴滴)结果', u'判断依据']
        result_data.insert(0, u'\t'.join(excel_title).encode('utf-8'))
        XLSDeal().toXlsFile(result_data, save_path)

if __name__ == '__main__':
    test = DiDiDiscernNature()
    test.run('test.xlsx','test_result.xlsx')

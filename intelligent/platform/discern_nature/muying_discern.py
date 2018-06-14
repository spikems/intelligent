# -*- coding:utf-8 -*-
import os
import xlrd
from intelligent.common.exldeal import XLSDeal
from intelligent.platform.discern_nature.conf.basic_conf import *
from intelligent.platform.discern_nature.conf.basic_tools import cut_input
from intelligent.platform.discern_nature.conf.basic_tools import dedup_near

# from intelligent.dm.project.discern_nature.nature_model_discern import DiscernModelNature
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径


class MyDiscernNature(object):
    def __init__(self):
        self.rule_data_path = project_path + '/conf/muying_filter_word.xlsx'
        self.filter_words = self.read_filter_data()
        self.origin_classification_rule = [u'sns', u'微博', u'论坛', u'问答']
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
        return result_data

    def read_filter_data(self):
        read_data = xlrd.open_workbook(self.rule_data_path)
        table = read_data.sheets()[0]
        result_data = {}
        for i in range(1, table.nrows):
            line = table.row_values(i)
            title_rule_words = line[0].strip().lower()
            document_rule_words = line[1].strip().lower()
            author_rule_words = line[2].strip().lower()
            if document_rule_words:
                result_data['document_rule_words'] = result_data.get('document_rule_words', []) + [document_rule_words]
            if title_rule_words:
                result_data['title_rule_words'] = result_data.get('title_rule_words', []) + [title_rule_words]
            if author_rule_words:
                result_data['author_rule_words'] = result_data.get('author_rule_words', []) + [author_rule_words]
        return result_data

    @staticmethod
    def get_duplicate_list(list_data):  # 获取重复的列表数据
        content_data_list = []
        for x in list_data:
            if list_data[x][1] == u'问答':  # 问答去重的数据特殊处理
                start = 0
                for i in range(5):
                    result = list_data[x][3][start:].find(list_data[x][2])
                    if result < 0 or result > 10:  # 如果没有发现,或者中间夹了很多字
                        break
                    else:
                        start += result + len(list_data[x][2])
                content_data_list.append(list_data[x][3][start:start+30])
            else:
                content_data_list.append(list_data[x][3][:30])
        cut_data_list = []
        for data in content_data_list:
            data = data.encode('utf-8')
            one_cut_data = cut_input(data)
            cut_data_list.append(one_cut_data)
        duplicate_list = dedup_near(cut_data_list, 7, 3)   # [ [重复数据组1], [数据组2], [数据组3], [数据组4] ]
        result_dup_list = []
        for d_l in duplicate_list:
            temp_dict = {}
            for i in d_l:
                dup_supervision = list_data[i][5]
                temp_dict[dup_supervision] = temp_dict.get(dup_supervision, []) + [i]   # 不同监控对象，只有一个的不算重复
            for source in temp_dict:
                if len(temp_dict[source]) > 1:
                    result_dup_list.extend(temp_dict[source])
        result_dup_list = list(set(result_dup_list))
        return result_dup_list

    def rule_filter(self, list_data, duplicate_list):
        final_str_data = []  # 返回的最终结果
        for data_id in list_data:
            # 结构 [order_number, origin_classification, title, document, author, supervision]
            # 规则  作者-限定关键词—标题-摘要-重复项（判定先后顺序）
            # 规则0：如果不是来源于[u'sns', u'微博', u'论坛', u'问答']
            if list_data[data_id][1].lower() not in self.origin_classification_rule:
                one_result = self.process_result(list_data[data_id], u'营销', u'来源')
                final_str_data.append(one_result)
                continue

            # 规则1：author中含有过滤词
            author_judge = False
            for word in self.filter_words['author_rule_words']:
                if word in list_data[data_id][4]:
                    one_result = self.process_result(list_data[data_id], u'营销', word + u'(作者)')
                    final_str_data.append(one_result)
                    author_judge = True
                    break
            if author_judge:
                continue

            # 规则2：问答&论坛 里面对特殊品牌，设定特殊限定词
            limit_brands_judge = False
            if list_data[data_id][1].lower() in [u'问答', u'论坛']:
                if list_data[data_id][-1] in my_brands_filter_dict.keys():  # 如果是在特殊母婴品牌，再将特殊词过滤一遍
                    for word in my_brands_filter_dict[list_data[data_id][-1]]:
                        if word in list_data[data_id][3]:
                            one_result = self.process_result(list_data[data_id], u'营销', u'限定')
                            final_str_data.append(one_result)
                            limit_brands_judge = True
                            break
            if limit_brands_judge:
                continue

            # 规则3：title中含有过滤词
            title_judge = False
            for word in self.filter_words['title_rule_words']:
                if word in list_data[data_id][2]:
                    one_result = self.process_result(list_data[data_id], u'营销', word + u'(主题)')
                    final_str_data.append(one_result)
                    title_judge = True
                    break
            if title_judge:
                continue

            # 规则4：document中含有过滤词
            document_judge = False
            for word in self.filter_words['document_rule_words']:
                if word == u'找我':  # 找我&店   找我&进口  找我&需要  同时出现
                    if word in list_data[data_id][3]:
                        together_words_judge = False
                        for t_word in [u'店', u'进口', u'需要']:
                            if t_word in list_data[data_id][3]:
                                one_result = self.process_result(list_data[data_id], u'营销', word + u'&' + t_word + u'(摘要)')
                                final_str_data.append(one_result)
                                together_words_judge = True
                                break
                        if together_words_judge:   # 如果出现这种情况，
                            document_judge = True
                            break
                    continue  # 不管是否，“找我”都必须跳过

                if word in list_data[data_id][3]:
                    one_result = self.process_result(list_data[data_id], u'营销', word + u'(摘要)')
                    final_str_data.append(one_result)
                    document_judge = True
                    break
            if document_judge:
                continue

            # 规则5：如果order_number 在重复的数据列表里面，则判定为营销数据
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
        excel_title = [u'序号', u'分类', u'主题', u'摘要', u'作者', u'监控对象', u'(母婴)结果', u'判断依据']
        result_data.insert(0, u'\t'.join(excel_title).encode('utf-8'))
        XLSDeal().toXlsFile(result_data, save_path)

if __name__ == '__main__':
    # test = DiscernMuying('合生元8月份自然声量.xlsx', '自然声量筛选-通用.xlsx')
    test = MyDiscernNature()
    test.run('test1.xlsx','test_result.xlsx')

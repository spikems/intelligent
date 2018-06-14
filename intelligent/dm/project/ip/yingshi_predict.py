# -*- coding:utf-8 -*-
# 对影视类的数据进行判断
import logging
import traceback
from intelligent.common.util import *
from intelligent.dm.project.ip.conf.ip_discern_conf import *
from intelligent.dm.project.ip.conf.basic_tools import cut_input
from intelligent.dm.project.ip.conf.basic_tools import load_result
from intelligent.dm.project.ip.conf.basic_tools import model_predict
from intelligent.dm.project.ip.conf.basic_tools import remove_ip_rule
from intelligent.dm.project.ip.conf.basic_tools import predicate_ip_rule
from intelligent.dm.project.ip.conf.basic_tools import related_word_process_data


@singleton
class PredictYingShi(object):
    def __init__(self):
        self.err_logger = logging.getLogger('errinfo')
        self.models = None    # 保存影视类模型
        self.ip_words = None    # 保存ip词汇
        self.ip_type = None     # 保存所指的ip_type

    def rule_filter(self, name_position_data, text):
        '''
        规则过滤
        :return:
        '''
        result = {}   # {'name1':[{'prob':1, 'type':'3', 'name':'一代宗师'}],  'name2':[{}]}
        judge_exit = False  # 用来判断一句话中是否存在《ip》的情况
        model_predict_words = {}    # 保存的是需要过模型的数据
        try:
            # 获取经过反向规则判断得到的剩下的数据
            names_list = name_position_data.keys()
            contain_name = remove_ip_rule(self.ip_words, name_position_data, text, names_list)

            for ip_word in contain_name:      # 遍历每一个ip词
                ip_name = self.ip_words[ip_word][0]['ip_name']  # 存储对应ip_name中的ip_name
                if ip_name in result:  # 如果此条ip_name 已经存在结果集里面了
                    continue
                # 根据basic_tools中的规则进行判断
                basic_judge_result = predicate_ip_rule(self.ip_words, ip_word, text, name_position_data,
                                                       contain_name, quotes=True, three_related=True)
                if basic_judge_result:
                    result[ip_name] = load_result(prob=1, ip_type=ip_types[self.ip_type], name=ip_word)
                    continue
                # 走完规则，将此ip放到过模型的数据中，此ip不能是type_noise_ip = 1 的数据
                if not self.ip_words[ip_word][0]['type_noise_ip']:
                    model_predict_words[ip_word] = name_position_data[ip_word]   # 只是一个复制过程，格式完全相同
        except:
            error = "yingshi_rule_filter error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        if judge_exit:  # 如果已经有了《左耳》这种类型，则不对后面的影视ip词进行判定
            return result, {}
        else:
            return result, model_predict_words

    @staticmethod
    def process_data(ip_word, position_data, content, ip_type, tag=None):
        '''
        数据的处理
        :return:
        '''
        first_process_data, word_num = related_word_process_data(position_data, content, ip_type)
        second_process_data = first_process_data.replace('《', '').replace('》', '')  # 删除《 和 》这个两个特征
        process_result = cut_input(second_process_data)  # 做分词处理
        return process_result

    def predict_result(self, models, ip_words, ip_type, text, name_position_data):
        # 开始先赋初始值，只有使用权，没有修改权
        self.models = models
        self.ip_words = ip_words
        self.ip_type = ip_type
        try:
            result, model_predict_words = self.rule_filter(name_position_data, text)
            if model_predict_words:  # 如果含有词，则需要先对数据进行处理，然后再过模型
                for ip_word in model_predict_words:
                    # 对需要过模型的数据进行预处理，返回的处理过的数据
                    
                    if ip_word == '影':
                       if text.find('张艺谋') != -1:
                           result[ip_word] = [{"type" : ip_types[ip_type], "prob" : 0.86, "name" : ip_word}]
                       continue

                    process_text = self.process_data(ip_word, model_predict_words[ip_word],
                                                     content=text, ip_type=self.ip_type)
                    one_list_result = model_predict(self.models, ip_types, process_text, ip_word, self.ip_type)
                    ip_name = self.ip_words[ip_word][0]['ip_name']
                    if one_list_result:
                        result[ip_name] = one_list_result

            return result
        except:
            error = "yingshi_predict.run error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
            return None

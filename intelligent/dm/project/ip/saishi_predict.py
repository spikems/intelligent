# -*- coding:utf-8 -*-
# 对赛事类的数据进行判断
import logging
import traceback
from intelligent.common.util import *
from intelligent.dm.project.ip.conf.ip_discern_conf import *
from intelligent.dm.project.ip.conf.basic_tools import cut_input
from intelligent.dm.project.ip.conf.basic_tools import load_result
from intelligent.dm.project.ip.conf.basic_tools import model_predict
from intelligent.dm.project.ip.conf.basic_tools import remove_ip_rule

@singleton
class PredictSaiShi(object):
    def __init__(self):
        self.err_logger = logging.getLogger('errinfo')
        self.models = None    # 保存影视类模型
        self.ip_words = None    # 保存ip词汇
        self.ip_type = None     # 保存所指的ip_type

    def rule_filter(self, name_position_data, text):
        '''
        赛事规则过滤
        '''
        result = {}  # {'name1':[{'prob':1, 'type':'3', 'name':'一代宗师'}],  'name2':[{}]}
        model_predict_words = {}  # 保存的是需要过模型的数据
        try:
            # 获取经过反向规则判断得到的剩下的数据
            names_list = name_position_data.keys()
            contain_name = remove_ip_rule(self.ip_words, name_position_data, text, names_list)

            for ip_word in contain_name:  # 遍历每一个ip词
                # 判断是否ip词是f1,如是放到过模型的数据中
                if ip_word == 'f1':
                    model_predict_words[ip_word] = name_position_data[ip_word]  # 只是一个复制过程，格式完全相同
                    continue
                ip_name = self.ip_words[ip_word][0]['ip_name']  # 存储对应ip_name中的ip_name
                # 规则一：判断是否是噪音IP   'noise_ip' ：0或1，整形
                if ip_name in result:   # 如果结果中已经有了这条ip_name的同义词了，则选取概率更高的
                    result[ip_name][0]['prob'] = 1
                else:   # 如果结果中没有这个ip_name
                    result[ip_name] = load_result(prob=1, ip_type=ip_types[self.ip_type], name=ip_word)  # 数据对应 'name':[{'prob':1, 'type':'3', 'name':'一代宗师'}]
                continue  # 如果一个ip_word是非噪音ip，则将此ip的prob设为1

        except:
            error = "saishi_rule_filter error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return result, model_predict_words

    @staticmethod
    def process_data(ip_word, position_data, content, ip_type, tag=None):
        related_words = ip_related_words[ip_type]
        word_num = 0
        for word in related_words:
            if word in content:
                content = 'word%d,' % word_num + content
                word_num += 1
        process_result = cut_input(content)  # 做分词处理
        return process_result

    def predict_result(self, models, ip_words, ip_type, text, name_position_data):
        # 开始先赋初始值，只有使用权，没有修改权
        self.models = models
        self.ip_words = ip_words
        self.ip_type = ip_type
        try:
            result, model_predict_words = self.rule_filter(name_position_data, text)
            if model_predict_words:  # 如果含有 f1 ，则需要先对数据进行处理，然后再过模型
                for ip_word in model_predict_words:
                    # 对需要过模型的数据进行预处理，返回的处理过的数据
                    process_text = self.process_data(ip_word, model_predict_words[ip_word],
                                                     content=text, ip_type=self.ip_type)
                    one_list_result = model_predict(self.models, ip_types, process_text, ip_word, self.ip_type)
                    ip_name = self.ip_words[ip_word][0]['ip_name']
                    if one_list_result and ip_name not in result:  # 如果概率大于0.5，且f1的其他同义词没有出现
                        result[ip_name] = one_list_result
            return result
        except:
            error = "saishi_predict.run error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
            return None
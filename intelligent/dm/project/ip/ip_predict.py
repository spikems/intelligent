# -*- coding:utf-8 -*-
'''
用规则过滤数据，再用模型预测数据，返回每条数据的识别结果
'''
from intelligent.common.util import *
from intelligent.dm.project.ip.conf.ip_discern_conf import *
from intelligent.dm.project.ip.yingshi_predict import PredictYingShi
from intelligent.dm.project.ip.saishi_predict import PredictSaiShi
from intelligent.dm.project.ip.xiaoshuo_predict import PredictXiaoShuo
from intelligent.dm.project.ip.star_yingshi_predict import PredictStarYingShi
from intelligent.dm.project.ip.star_sports_predict import PredictStarSport
from intelligent.dm.project.ip.zongyi_predict import PredictZongYi
from intelligent.dm.learn.learner import Learner
import os
import logging
import traceback
import copy


class PredictIp(object):
    def __init__(self):
        self.logger = logging.getLogger("intelligent")
        self.err_logger = logging.getLogger('errinfo')
        self.ip_words = None   # 只能读取，不能修改
        self.ip_type = None
        self.models = {}
        self.project_path = os.path.dirname(os.path.realpath(__file__))
        self.load_model()  # 加载模型

    def load_model(self):
        '''
        加载模型
        :return:
        '''
        path = '%s/%s' % (self.project_path, 'model')
        # 加载ip_models中包含的全部模型
        try:
            for model_name in ip_models:
                if model_name == '5':
                    other_sport_model_dict = {}
                    for other_sport_name in ip_models[model_name]:
                        predictor = Learner(train=False)
                        predictor.load_model(path + "/" + ip_models[model_name][other_sport_name])
                        other_sport_model_dict[other_sport_name] = predictor
                        self.logger.info("load model " + other_sport_name)
                    self.models[model_name] = other_sport_model_dict  # '5':{'篮球':'lanqiu_ip','足球':'zuqiu_ip'...}

                else:
                    predictor = Learner(train=False)
                    predictor.load_model(path + "/" + ip_models[model_name])
                    self.models[model_name] = predictor  # {'3':yingshi_ip.pkl}
                    self.logger.info("load model " + ip_models[model_name])
        except:
            error = "load_model file error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)

    def process_position_name_data(self, raw_data):  # 处理(position,name)数据转为{name:[pos1,pos2]}格式
        result_data = {}
        for data in raw_data:
            add_list = [data[0]]
            if data[1] in self.ip_words:  # 过滤当前ip类型的数据
                result_data[data[1]] = result_data.get(data[1], []) + add_list
        # 从这里处理这种包含情景(1):识别出伊赛亚-托马斯，相同位置包含托马斯，这里只算做伊赛亚托马斯
        try:
            repeat_name_dict = {}
            name_data_bak_1 = copy.deepcopy(result_data.keys())
            name_data_bak_2 = copy.deepcopy(result_data.keys())
            name_data_bak_1.sort(key=lambda x: len(x))
            name_data_bak_2.sort(key=lambda x: len(x))
            # 得到{'伊赛亚—托马斯':['托马斯', '伊赛亚']}  这种类型的数据
            for name in name_data_bak_1:
                name_data_bak_2.remove(name)
                for other_name in name_data_bak_2:
                    if name in other_name:
                        repeat_name_dict[other_name] = repeat_name_dict.get(other_name, []) + [name]
            # 需要得到每个name下的数据，因为 [{暮光之城：暮光}，{暮光之城1: 暮光之城}] 此条数据，如果把【暮光之城】移除掉，
            # 处理【暮光】时数据就会报错， 因此需要最后再处理需要移除的数据
            remove_position_data = {}  # 被包含的名字，需要移除的位置，
            for contain_name in repeat_name_dict:  # 遍历包含名字（伊赛亚托马斯）
                for included_name in repeat_name_dict[contain_name]:  # 遍历被包含名字（['托马斯'，'伊赛亚']）
                    for large_position_data in result_data[contain_name]:  # 循环包含的name数据(伊赛亚托马斯)
                        for small_position_data in result_data[included_name]:  # 循环被包含的name数据(托马斯)
                            # 如果托马斯的position数据包含于伊赛亚托马斯的position数据，则添加到删除位置
                            if small_position_data[0] >= large_position_data[0] and small_position_data[1] <= \
                                    large_position_data[1]:
                                remove_position_data[included_name] = remove_position_data.get(included_name, []) + \
                                                                      [small_position_data]
                    # 遍历include_name中需要删除的数据
            for r_p_name in remove_position_data:
                remove_position_data[r_p_name] = list(set(remove_position_data[r_p_name]))   # 暮光，可能重复暮光之城，同时也重复暮光之城1
                for r_p_data in remove_position_data[r_p_name]:
                    result_data[r_p_name].remove(r_p_data)
                if len(result_data[r_p_name]) == 0:  # 如果included_name的位置数据为0，则删除这条数据
                    del (result_data[r_p_name])
        except:
            error = "process_position_name_data file error. traceback: %s" % traceback.format_exc()
            self.err_logger.error(error)
        return result_data

    def run(self, text, position_name_data, ip_words, ip_type):   # 总控函数
        '''
        :param text: '%s。%s' %(title,document)  标题和内容
        :param position_name_datas:{name1:[{类型1数据},{类型2数据}], name2:[{类型2数据},{类型3数据}]}
        {类型1数据}：{'type_noise_ip':0, 'noise_ip':1, 'type':3, 'name':'一代宗师','determiner': '王家卫、章子怡、....'}
        :return: 结构 {name1:[{类型1判断结果},{类型2判断结果}], name2:{name2数据}}
        {类型1判断结果}：{type:1, name:一代宗师, prob:0.6}
        '''
        # 部分初始化过程在这里进行
        self.ip_words = ip_words  # 只能读取，不能修改
        self.ip_type = ip_type
        name_position_data = self.process_position_name_data(position_name_data)
        # 单独处理某个类别，遍历此类别中的词，对于同一类中，name:[{类数据}](只有一条类数据)
        # ip_model, ip_words, ip_type, text, name_position_data
        if self.ip_type == '3':  # 影视类
            yingshi_predict = PredictYingShi()
            result = yingshi_predict.predict_result(self.models, self.ip_words, self.ip_type, text, name_position_data)
            return result
        elif self.ip_type == '2':  # 赛事类
            saishi_predict = PredictSaiShi()
            result = saishi_predict.predict_result(self.models, self.ip_words, self.ip_type, text, name_position_data)
            return result
        elif self.ip_type == '4':  # 小说类
            xiaoshuo_predict = PredictXiaoShuo()
            result = xiaoshuo_predict.predict_result(self.models, self.ip_words, self.ip_type, text, name_position_data)
            return result
        elif self.ip_type == '1':  # 影视明星类
            star_yingshi_predict = PredictStarYingShi()
            result = star_yingshi_predict.predict_result(self.models, self.ip_words, self.ip_type, text, name_position_data)
            return result
        elif self.ip_type == '5':  # 体育类明星
            star_sport_predict = PredictStarSport()
            result = star_sport_predict.predict_result(self.models, self.ip_words, self.ip_type, text, name_position_data)
            return result
        elif self.ip_type == '6':  # 体育类明星
            zongyi_predict = PredictZongYi()
            result = zongyi_predict.predict_result(self.models, self.ip_words, self.ip_type, text, name_position_data)
            return result


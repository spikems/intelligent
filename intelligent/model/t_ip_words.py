#! /usr/bin/python
# -*- coding:utf-8 -*-
from intelligent.model.modelbase import ModelBase
from intelligent.dm.project.ip.conf.ip_discern_conf import ip_types


class IpWords(ModelBase):

    def __init__(self):
        super(IpWords, self).__init__()
        self.table = 'ip_find'
        self.ip_words_dict = {}

    def queryAll(self, ip_type):
        '''
             get ip words
         '''
        if ip_type not in ip_types:
            return {}
        one_type_ip_words = {}
        sql = 'select name,type,ip_name,tag,determiner,fdeterminer,noise_ip,type_noise_ip,is_english_name,is_cut_word from %s where type = %d' % \
              (self.table, int(ip_type))
        db_datas = super(IpWords, self).query(sql)
        for data in db_datas:
            data['name'] = data['name'].strip().lower()   # 所有的name转为
            if len(data['name']) >= 2:
                add_list = []
                add_list.append(data)
                one_type_ip_words[data['name']] = one_type_ip_words.get(data['name'], []) + add_list   # one_type_ip_data的格式{'name':[{类型一数据},{类型二数据}]} 处理同名的数据
        self.ip_words_dict = one_type_ip_words    # {'3',{name1:, name2:,}}
        return self.ip_words_dict
        #return db_datas     # 传递数据格式[{数据1},{数据2},{数据3},{数据4}]


if __name__ == '__main__':
    test = IpWords()
    test.queryAll('1')

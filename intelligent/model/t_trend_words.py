#! /usr/bin/python
# -*- coding:utf-8 -*-
from intelligent.model.modelbase import ModelBase


class WordsTrend(ModelBase):

    def __init__(self):
        super(WordsTrend, self).__init__()
        self.table = 'trend_word'
        self.new_words_table = 'new_words'
        self.type_dict = {'new': 'all', 'trend': '4'}
        self.trend_word_list = []

    def queryAll(self):
        '''
             get ip words
         '''
        sql = 'select word from %s where industry=4;' % self.new_words_table
        db_datas = super(WordsTrend, self).query(sql)
        for data in db_datas:
            data['word'] = data['word'].strip().lower()   # 所有的name转为
            self.trend_word_list.append(data['word'])
        return self.trend_word_list
        #return db_datas     # 传递数据格式[{数据1},{数据2},{数据3},{数据4}]

    def set_type(self):
        '''
            set the word type, 0表示为查询，1代表已查询
        '''
        for word in self.trend_word_list:
            word = word.encode('utf-8') if type(word) == unicode else word
            sql = "update %s set type=1 where word='%s'" % (self.table, word)
            db_datas = super(WordsTrend, self).operate(sql)

    def copy_words(self):
        '''
            从new_words中更新数据库
        '''
        sql = "insert ignore into %s(word) select word from %s where industry=4;" % (self.table, self.new_words_table)
        db_datas = super(WordsTrend, self).operate(sql)

    def query_trend_new_words(self, search_type, time_list):
        '''
            搜索新词数据和趋势词数据
        :return:
        '''
        industry = self.type_dict[search_type]
        if industry == 'all':  # 代表搜索 新词
            sql = "select * from %s where (update_time between '%s' and '%s') and (word_sex != '0')" \
                  % (self.new_words_table, time_list[0], time_list[1])
        else:     # 代表只显示 趋势词
            sql = "select * from %s where (update_time between '%s' and '%s') and (word_sex != '0') and (industry=%d)" \
                  % (self.new_words_table, time_list[0], time_list[1], int(industry))
        db_datas = super(WordsTrend, self).query(sql)
        result_words_list = []
        for data in db_datas:
            data['word'] = data['word'].strip()  # 所有的name转为
            data['industry'] = int(data['industry']) if data['industry'] else 0
            data['word_sex'] = data['word_sex'].strip()
            result_words_list.append([data['word'], data['industry'], data['word_sex']])
        return result_words_list

if __name__ == '__main__':
    test = WordsTrend()
    test.query_trend_new_words('new', ['2018-01-17', '2018-01-18'])

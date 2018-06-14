# -*- coding:utf-8 -*-
from elasticsearch import Elasticsearch
import sys
import re
import traceback
from elasticsearch import helpers
reload(sys)
sys.setdefaultencoding('utf-8')

es = Elasticsearch(["http://192.168.241.35:9200", "http://192.168.241.46:9200", "192.168.241.50:9201",
                    "http://192.168.241.47:9201"], sniffer_timeout=200, timeout=100)
import os
dir_path = os.path.dirname(os.path.abspath(__file__))

def trim(words):
    return words.replace('\r', '').replace('\t', '').replace('\n', '')

def es_query(word,day=30):
    bodys = {"query": {"bool": {
             "must": [{"range": {
        "post_time": {
            "gte": "now-%sd/d"%day,
            "lte": "now/d"
        }
    }},{"term":{"brands":word}}],
      "must_not":[{"term":{"text_repeat":"T"}},{"term":{"site_type":12}}]}}}
    num =es.count(index = "community2",body=bodys)
  #  print num['count']
    raw_data = []
    if num['count'] >=5000 or day>=0:
        es_re = helpers.scan(es, query=bodys, index="community2")
        for i in es_re:
            j = i['_source']
            try:
                line = '%s\t%s\t%s' % (i['_id'],
                                       re.sub(r'\s', '', str(j['title'])),
                                       re.sub(r'\s', '', str(j['text'])))
                raw_data.append(line)
            except BaseException:
                traceback.print_exc()
        return raw_data
    else:
        day+=30
        return es_query(word,day)
if __name__ == "__main__":
    word = u'兰蔻'    
    es_query(word)

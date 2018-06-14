# -*- coding:utf-8 -*-
from elasticsearch import Elasticsearch
import sys
import re
import traceback
from elasticsearch import helpers
import  logging
import os
reload(sys)
sys.setdefaultencoding('utf-8')

es = Elasticsearch(["http://192.168.241.35:9200", "http://192.168.241.46:9200", "192.168.241.50:9201",
                    "http://192.168.241.47:9201"], sniffer_timeout=200, timeout=100)
dir_path = os.path.dirname(os.path.abspath(__file__))

def trim(words):
    return words.replace('\t', '').replace('\r','').replace('\n','')

def es_query(word,day=90):
    bodys = {"query": {"bool": {
             "must": [{"range": {
        "post_time": {
            "gte": "now-%sd/d"%day,
            "lte": "now/d"
        }
    }},{"multi_match": {
    "fields":["title","text"],
    "query": word,
    "type":"phrase",
    "minimum_should_match": "100%",
    "slop":0}}],
      "must_not":[{"term":{"text_repeat":"T"}},{"term":{"site_type":12}},{"term":{"is_kol":"T"}}]}}}

    num =es.count(index = "community2",body=bodys)
    raw_data = []
    if num['count'] >=5000 or day>=0:
        logging.info('%s : es search all num is %s during %s days'%(word,num['count'],day))
        es_re = helpers.scan(es, query=bodys, index="community2")
        for i in es_re:
            j = i['_source']
            try:
                line = '%s\t%s\t%s' % (i['_id'],
                                       trim(str(j['title'])),
                                       trim(str(j['text'])))
                raw_data.append(line)
            except BaseException:
                traceback.print_exc()
        logging.info('raw data num : %s'%len(raw_data))
        return raw_data
    else:
        day+=30
        return es_query(word,day)

if __name__ == "__main__":
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    # logging configure
    import logging.config
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    word = u'兰蔻'
    ss =es_query(word)
    print ss[0]

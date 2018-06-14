# -*- coding: utf-8 -*-

import json
import time
import uuid
import logging
import datetime
import traceback
import sys
import requests
import md5
import urllib
import urllib2
import hashlib

import dateformatting
from functools32 import lru_cache
from pykafka import KafkaClient
from pykafka.common import OffsetType
sys.path.insert(0, "/home/liuhongyu/intelligent/")
from intelligent.dm.project.intention.master import predict as intentionp
from intelligent.dm.project.brandfind.master import predict as brandfindp

DATA_MIXING_ENABLED = False

# logging configure

import logging.config
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _normalize_text(data):
    """ 处理 title、text 为 None 的情况，会影响挖掘端，空串没问题 """
    if ("title" in data and data["title"] is None) or not "title" in data:
        data["title"] = ""
    if ("text" in data and data["text"] is None) or not "text" in data:
        data["text"] = ""
    if isinstance(data["text"], str):
        data["text"] = data["text"].decode("utf8", "ignore")
    data['text'] = data['text'].strip()
    return data

def _check_post_time(dt):
    ndt = dateformatting.parse(dt)
    if ndt and ndt.strftime("%Y-%m-%d %H:%M:%S") != dt:
        logger.error("Error post time of data:\n%s" % str(data))
        return False
    if ndt < D20160101:
        logger.warning("Post time timeout: %s" % dt)
        return False
    return True

def _md5(s):
    return hashlib.md5(s).hexdigest()


def _interface(requrl, project, cache):
            
    sJs = json.dumps(cache)
    sData = {'project' : project, 'param' : sJs}
    try: 
        req = requests.post(requrl, data = sData)
        req.close()
    except:
        logger.error("Raise exception: \n%s\n" % (traceback.format_exc()))
        

def _start(project, cache):

    sJs = json.dumps(cache)
    if project == 'intention':
        res = intentionp(sJs)
    elif project == 'brandfind':
        res = brandfindp(sJs)
    return res
TOPIC = "community"
GROUP = "test_dm_kafuka"
D20160101 = datetime.datetime(2016, 10, 1, 0, 0, 0)


client = KafkaClient(hosts="192.168.241.40:9092,192.168.241.41:9092,192.168.241.42:9092")
topic = client.topics[TOPIC]

consumer = topic.get_balanced_consumer(
    consumer_group=GROUP,
    managed=True,  # use kafka manager
    fetch_message_max_bytes=10240 * 1024,  # 获取到的数据最大 10M
    num_consumer_fetchers=1,  # 每次获取 1 个数据
    auto_commit_enable=False,  # 自动设置成已经消费
    queued_max_messages=1000,  # buffer 中的数据量
    auto_offset_reset=OffsetType.EARLIEST,  # 当数据出界时的行为
    consumer_timeout_ms=1000,  # 没有数据的话多长时间返回一次 None
    auto_start=True,  # 初始化后不调用 start 就启动
    reset_offset_on_start=False,  # 默认从上一个没有 commit 的地方启动
)


cache = []
while True:
    for message in consumer:
        try:
            data = json.loads(message.value)

            if not _check_post_time(data["post_time"]):
                continue
       
            data = _normalize_text(data)
     
            if not "url" in data:
                data["url"] = ''
                
            id = _md5(data["url"].encode('utf8'))
            dParam = {'id' : id, 'title' : data['title'], 'document' : data['text']}
            cache.append(dParam)
            if len(cache) <= 500:
                 continue
            time.sleep(2)

            ip = "3"
            requrl = "http://192.168.241.%s:8099/tumnus/dm/flm" % ip
            #_start('brandfind', cache)
            #_start('intention', cache)
            _interface(requrl, 'brandfind', cache)
            _interface(requrl, 'intention', cache)
            cache = []
            consumer.commit_offsets()
        except:
          logger.error("Raise exception: \n%s\nWith data: \n%s" % (traceback.format_exc(), message.value))
    logger.info("Sleep 5s...")
    time.sleep(5)


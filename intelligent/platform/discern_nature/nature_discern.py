# -*- coding:utf-8 -*-
from intelligent.common.util import *
from intelligent.platform.discern_nature.didi_discern import DiDiDiscernNature
from intelligent.platform.discern_nature.car_discern import CarDiscernNature
from intelligent.platform.discern_nature.muying_discern import MyDiscernNature
from intelligent.platform.discern_nature.common_discern import AllDiscernNature
from intelligent.platform.discern_nature.meizhuang_discern import MzDiscernNature


@singleton
class DiscernNature(object):
    def __init__(self):
        pass

    def run(self, raw_data_path, save_path, class_type):
        # 识别母婴类的自然声量
        if class_type == 'my':
            MyDiscernNature().run(raw_data_path, save_path)
        elif class_type == 'car':
            CarDiscernNature().run(raw_data_path, save_path)
        elif class_type == 'mz':
            MzDiscernNature().run(raw_data_path, save_path)
        elif class_type == 'all':
            AllDiscernNature().run(raw_data_path, save_path)
        elif class_type == 'didi':
            DiDiDiscernNature().run(raw_data_path, save_path)
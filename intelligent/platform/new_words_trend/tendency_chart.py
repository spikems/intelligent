# -*- coding:utf-8 -*-
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
current_path = os.path.dirname(os.path.realpath(__file__))


def plot_chart(x_list, y_list_0, y_list_1, y_list_2, term, save_path, type_display='', interval_period='week'):
    '''
    [[time_list],[news_number_list],[pgc_number_list],[ugc_number_list]]
    :return:
    '''

    myfont = fm.FontProperties(fname=current_path + '/conf/simsun.ttc')   # 配置字体位置
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)
    ax0.plot(x_list, y_list_0, color='b', linewidth=1)

    ax0.xaxis.grid(True, which='major')
    ax0.yaxis.grid(True, which='major')
    # y0_tick_list = np.linspace(min(y_list_0), max(y_list_0), 5)  # 将y的取值范围分为5份
    # ax0.set_yticks(y0_tick_list)
    ax0.set_xticklabels(x_list, visible=False)
    ax0.set_title('news类%s图：' % type_display + term, fontProperties=myfont)

    ax1.plot(x_list, y_list_1, color='r', linewidth=1)
    ax1.xaxis.grid(True, which='major')
    ax1.yaxis.grid(True, which='major')
    # y1_tick_list = np.linspace(min(y_list_1), max(y_list_1), 5)   # 将y的取值范围分为5份
    # ax1.set_yticks(y1_tick_list)
    ax1.set_xticklabels(x_list, visible=False)
    ax1.set_title('PGC类%s图：' % type_display + term, fontProperties=myfont)

    ax2.plot(x_list, y_list_2, color='g', linewidth=1)
    ax2.xaxis.grid(True, which='major')
    ax2.yaxis.grid(True, which='major')
    # y2_tick_list = np.linspace(min(y_list_2), max(y_list_2), 5)   # 将y的取值范围分为5份
    # ax2.set_yticks(y2_tick_list)
    ax2.set_title('UGC类%s图：' % type_display + term, fontProperties=myfont)
    if interval_period == 'day':  # 如果是以天为单位, 修改横坐标
        if len(x_list) >= 35:   # 如果大于35， 则以7天为一个周期
            xtick_list = []
            max_num = len(x_list)//7 if len(x_list)%7==0 else (len(x_list)//7+1)  # 如果能够被7整除
            for i in range(max_num):
                xtick_list.append(x_list[i*7])
            ax0.set_xticks(xtick_list)
            ax0.set_xticklabels(xtick_list, visible=False)
            ax1.set_xticks(xtick_list)
            ax1.set_xticklabels(xtick_list, visible=False)
            ax2.set_xticks(xtick_list)
            ax2.set_xticklabels(xtick_list, visible=True)
    fig.tight_layout()
    plt.subplots_adjust(hspace=0.3)
    plt.xticks(rotation='vertical')
    plt.savefig(save_path, format='png', dpi=300)
    plt.close('all')

if __name__ == '__main__':
    print current_path
# -*- coding:utf-8 -*-
import os
import xlrd
import xlsxwriter
from intelligent.dm.project.ip.ip_discern import IpDiscern
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径


def read_raw_data(input_path):
    read_data = xlrd.open_workbook(input_path)
    table = read_data.sheets()[0]
    raw_data_dict = {}   # { id1:{}, id2:{} }
    order_id_list = []
    for i in range(1, table.nrows):
        one_result = {}
        line = table.row_values(i)
        try:
            #  {'id': '1', 'title': '', 'document': '卡西击败C罗、梅西获得2017年度金足奖！'},
            i_line = str(int(line[0]))
            title = line[1].strip() if type(line[1]) == unicode else str(line[1]).decode('utf-8').strip()
            document = line[2].strip() if type(line[2]) == unicode else str(line[2]).decode('utf-8').strip()
            one_result['id'] = i_line
            one_result['title'] = title.encode('utf-8')
            one_result['document'] = document.encode('utf-8')
            raw_data_dict[i_line] = one_result
            order_id_list.append(i_line)
        except Exception as e:
            print line
            print e
    return raw_data_dict, order_id_list


def predict_result(type_class, raw_data_dict):
    ip_obj = IpDiscern()
    for i_line in raw_data_dict:
        one_data = [{'ip_type': type_class}, raw_data_dict[i_line]]
        one_result = ''
        if ip_obj.run(one_data):
            one_result = '|'.join(ip_obj.run(one_data)[0]['result'])
        raw_data_dict[i_line]['result'] = one_result
    return raw_data_dict


def save_excel_file(result_list_data, order_id_list, output_path):
    workbook = xlsxwriter.Workbook(output_path)
    sheet = workbook.add_worksheet('predict')
    sheet.write(0, 0, u'ID')
    sheet.write(0, 1, u'主题')
    sheet.write(0, 2, u'摘要')
    sheet.write(0, 3, u'结果')
    i_row = 1
    for i_line in order_id_list:
        sheet.write(i_row, 0, int(i_line))  # 必须为unicode
        sheet.write(i_row, 1, result_list_data[i_line]['title'])
        sheet.write(i_row, 2, result_list_data[i_line]['document'])
        sheet.write(i_row, 3, result_list_data[i_line]['result'])
        i_row += 1
    workbook.close()


def ip_master(type_class, input_path, output_path):
    raw_data_dict, order_id_list = read_raw_data(input_path)
    result_data_dict = predict_result(type_class, raw_data_dict)
    save_excel_file(result_data_dict, order_id_list, output_path)


if __name__ == '__main__':
    type_class = 'all'
    input_path = project_path + '/ip_test.xlsx'
    output_path = project_path + '/result.xlsx'
    ip_master(type_class, input_path, output_path)

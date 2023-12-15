#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - files - raw
# ==========================================
#
#
#
"""
import traceback
from xlrd import open_workbook


def open_file(filepath: str, extension: str = 'xls'):
    """
    :param filepath: directory of file
    :param extension: filter 1 for .xls files, 2 for .ahd files
    :return: step_list -> [[[header of step one], [cycle one in the step], [cycle two in the step]],[[],[]]]
        example:
            [
                [
                    [1, '6/8/2019  8:20:51 PM', 'BLK', 'B'],  # step header
                    # [sequence index, date time, label, value]
                    ['1', 12.30, 87.73, 12.30, 1.30, 12.30, 0.40, 12.30, 0.40, 12.30, 0.44],  # step/sequence 1
                    # [cycle index, time, Ar40 signal, time, Ar39 signal, ..., time, Ar36 signal]
                    ['2', 24.66, 87.70, 24.66, 1.14, 24.66, 0.36, 24.66, 0.35, 24.66, 0.43],  # step/sequence 2
                    ...
                    ['10', 123.06, 22262.68, 123.06, 6.54, 123.06, 8.29, 123.06, 0.28, 123.06, 29.22],
                ],
                [
                    ...
                ]
            ]
    """
    try:
        handler = {'xls': open_raw_xls, 'ahd': open_raw_ahd}[extension.lower()]
    except KeyError:
        print(traceback.format_exc())
        return False
    else:
        return handler(filepath)


def open_raw_xls(filepath):
    try:
        wb = open_workbook(filepath)
        sheets = wb.sheet_names()
        sheet = wb.sheet_by_name(sheets[0])
        value, step_header, step_list = [], [], []
        for row in range(sheet.nrows):
            row_set = []
            for col in range(sheet.ncols):
                if sheet.cell(row, col).value == '':
                    pass
                else:
                    row_set.append(sheet.cell(row, col).value)
            if row_set != [] and len(row_set) > 1:
                value.append(row_set)
        for each_row in value:
            # if the first item of each row is float (1.0, 2.0, ...) this row is the header of a step.
            if isinstance(each_row[0], float):
                each_row[0] = int(each_row[0])
                step_header.append(each_row)
        for step_index, each_step_header in enumerate(step_header):
            row_start_number = value.index(each_step_header)
            try:
                row_stop_number = value.index(step_header[step_index + 1])
            except IndexError:
                row_stop_number = len(value) + 1
            step_values = [
                each_step_header[0:4],
                *list(map(
                    lambda x: [x[0], x[1], x[2], x[1], x[3], x[1], x[4], x[1], x[5], x[1], x[6]],
                    [value[i] for i in range(row_start_number + 2, row_stop_number - 7, 1)]))
            ]
            step_list.append(step_values)
    except Exception as e:
        print('Error in opening the original file: %s' % str(e))
        return False
    else:
        return step_list


def open_raw_ahd(filepath):
    try:
        value, step_header, step_list = [], [], []
        with open(filepath, 'r', encoding='utf-16-le') as f:
            value = f.read()
        value = [[j for j in i.split('\t') if j != ''] for i in value.split('\n')]
        datetime = 'ddmmyyyy'
        if datetime == 'ddmmyyyy':
            dd, mm, yyyy = value[6][1].split('/')
            value[6][1] = '/'.join([mm, dd, yyyy])
        step_count = int(value[12][2])
        step_header = [1, '  '.join(value[6][1:3]), value[0][1], value[8][1]]
        step_list.append([step_header])
        for step_index in range(step_count):
            start_row = 15 + 5 * step_index
            step_list[0].append([
                str(step_index+1),
                float(value[start_row+4][0]), float(value[start_row+4][1]),
                float(value[start_row+3][0]), float(value[start_row+3][1]),
                float(value[start_row+2][0]), float(value[start_row+2][1]),
                float(value[start_row+1][0]), float(value[start_row+1][1]),
                float(value[start_row+0][0]), float(value[start_row+0][1]),
            ])
    except Exception as e:
        print('Error in opening the original file: %s' % str(e))
        return False
    else:
        return step_list



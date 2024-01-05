#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# webarar - raw_file
# ==========================================
#
#
#
"""

import traceback
import os
from xlrd import open_workbook
from datetime import datetime


""" Open raw data file """


def open_file(file_path: str, extension: str = None):
    """
    :param file_path: directory of file
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
    if extension is None:
        extension = str(os.path.split(file_path)[-1]).split('.')[-1]
    try:
        handler = {'xls': open_raw_xls, 'ahd': open_raw_ahd, 'txt': open_raw_txt}[extension.lower()]
    except KeyError:
        print(traceback.format_exc())
        raise FileNotFoundError("Woring File.")
    try:
        data = handler(file_path)
    except (BaseException, Exception):
        print(traceback.format_exc())
        raise ValueError("Fails to open the file(s)")
    else:
        return {'data': data, 'type': extension}


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
                each_row[1] = datetime.strptime(each_row[1], '%m/%d/%Y  %H:%M:%S').isoformat(timespec='seconds')
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
                    # lambda x: [x[0], x[1], x[2], x[1], x[3], x[1], x[4], x[1], x[5], x[1], x[6]],
                    # x[1] = time, x[2] = H2:40, x[3] = H1: 39, x[4] = AX: 38, x[5] = L1: 37, x[6] = L2: 36
                    lambda x: [x[0], x[1], x[6], x[1], x[5], x[1], x[4], x[1], x[3], x[1], x[2]],
                    # in sequence: Ar36, Ar37, Ar38, Ar39, Ar40
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
        contents, step_header, step_list = [], [], []
        contents = [line.rstrip().split('\t') for line in open(filepath, 'r', encoding='utf-16-le')]
        datetime_str = datetime.strptime(contents[6][1]+contents[6][2],
                                         '%d/%m/%Y%H:%M:%S').isoformat(timespec='seconds')
        step_count = int(contents[12][2])
        step_header = [1, datetime_str, contents[0][1], contents[8][1]]
        step_list.append([step_header])
        for step_index in range(step_count):
            start_row = 15 + 5 * step_index
            step_list[0].append([
                str(step_index + 1),
                # in sequence: Ar36, Ar37, Ar38, Ar39, Ar40
                float(contents[start_row + 0][0]), float(contents[start_row + 0][1]),
                float(contents[start_row + 1][0]), float(contents[start_row + 1][1]),
                float(contents[start_row + 2][0]), float(contents[start_row + 2][1]),
                float(contents[start_row + 3][0]), float(contents[start_row + 3][1]),
                float(contents[start_row + 4][0]), float(contents[start_row + 4][1]),
            ])
    except Exception as e:
        print('Error in opening the original file: %s' % str(e))
        return False
    else:
        return step_list


def open_raw_txt(filepath, filter=None):
    """
    Parameters
    ----------
    filter
    filepath

    Returns
    -------

    """
    default_index = (-1, -1)

    def _get_val(a: list, index: tuple):
        return "" if index == (-1, -1) else a[index[0] - 1][index[1] - 1]

    if filter is None:
        # indexes are all int from 1
        filter = {
            'header_len': 29, 'exp_name': (4, 2), 'exp_time': (10, 2),
            'time': 7, 'Ar40': 16, 'Ar39': 15, 'Ar38': 12, 'Ar37': 9, 'Ar36': 8,
            'separator': ',', 'end': ""
        }
    if filter.get('separator', ' ').lower() == 'comma':
        filter['separator'] = ','
    contents = [line.rstrip().split(filter.get('separator', ' ')) for line in open(filepath, 'r', encoding='utf-8')]
    datetime_str = datetime.strptime(_get_val(contents, filter.get('exp_time', default_index)),
                                     ' %d %B %Y %H:%M:%S.%f').isoformat(timespec='seconds')
    name = _get_val(contents, filter.get('exp_name', default_index))
    cycle_list = [[[1, datetime_str, name]]]
    cycle_num = 0
    for line in contents[filter['header_len']:]:
        if line == filter['end'] or line == [filter['end']]:
            break
        cycle_num += 1
        cycle_list[0].append([
            str(cycle_num),
            # Ar36, Ar37, Ar38, Ar39, Ar40
            float(line[filter['time'] - 1]), float(line[filter['Ar36'] - 1]),
            float(line[filter['time'] - 1]), float(line[filter['Ar37'] - 1]),
            float(line[filter['time'] - 1]), float(line[filter['Ar38'] - 1]),
            float(line[filter['time'] - 1]), float(line[filter['Ar39'] - 1]),
            float(line[filter['time'] - 1]), float(line[filter['Ar40'] - 1]),
        ])
    return cycle_list



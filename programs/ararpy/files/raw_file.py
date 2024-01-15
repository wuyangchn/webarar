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

from typing import List, Union
import traceback
import os
import chardet
from xlrd import open_workbook
from datetime import datetime
import dateutil.parser as datetime_parser
from ..calc.arr import get_item

""" Open raw data file """

DEFAULT_SAMPLE_INFO = {}


def open_file(file_path: str, input_filter: List[Union[str, int, bool]]):
    """
    Parameters
    ----------
    file_path:
    input_filter

    Returns
    -------
    step_list -> [[[header of step one], [cycle one in the step], [cycle two in the step]],[[],[]]]
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
    extension = str(os.path.split(file_path)[-1]).split('.')[-1]
    try:
        handler = {'excel': open_raw_xls, 'txt': open_raw_txt}[['txt', 'excel'][int(input_filter[1])]]
    except KeyError:
        print(traceback.format_exc())
        raise FileNotFoundError("Wrong File.")
    data, _ = handler(file_path, input_filter)
    return {'data': data, 'type': extension}


def open_raw_xls(filepath, input_filter=None):
    if input_filter is None:
        input_filter = []
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
        return step_list, {}


def open_raw_txt(file_path, input_filter: List[Union[str, int]]):
    """
    Parameters
    ----------
    input_filter
    file_path

    Returns
    -------

    """
    if not input_filter:
        raise ValueError("Input filter is empty array.")

    if os.path.splitext(file_path)[1][1:].lower() != input_filter[0].strip().lower():
        raise ValueError("The file does not comply with the extension in the given filter.")

    with open(file_path, 'rb') as f:
        contents = f.read()
        encoding = chardet.detect(contents)
        lines = [line.strip().split(['\t', ';', " ", ",", input_filter[3]][int(input_filter[2])])
                 for line in contents.decode(encoding=encoding["encoding"]).split('\r\n')]

    sample_info = get_sample_info([lines], input_filter)
    # print(sample_info)
    name = get_item([lines], input_filter[34:37], default="", based=1)
    if input_filter[131]:  # input_filter[131]: date in one string
        if input_filter[32].strip() != "":
            zero_date = datetime.strptime(get_item([lines], input_filter[46:49], based=1),
                                          input_filter[32]).isoformat(timespec='seconds')
            # zero_time = datetime.strptime(_get_val(contents, filter.get('exp_time', default_index)),
            #                               ' %d %B %Y %H:%M:%S.%f').isoformat(timespec='seconds')
        else:
            print("date string")
            print(get_item([lines], input_filter[46:49], based=1))
            zero_date = datetime_parser.parse(get_item([lines], input_filter[46:49], based=1))
    else:
        zero_date = datetime(year=get_item([lines], input_filter[46:49], based=1),
                             month=get_item([lines], input_filter[52:55], based=1),
                             day=get_item([lines], input_filter[58:61], based=1))

    if input_filter[132]:  # input_filter[132]: time in one string
        if input_filter[33].strip() != "":
            zero_time = datetime.strptime(get_item([lines], input_filter[49:52], based=1),
                                          input_filter[33]).isoformat(timespec='seconds')
        else:
            print("time string")
            print(get_item([lines], input_filter[49:52], based=1))
            zero_time = datetime_parser.parse(get_item([lines], input_filter[49:52], based=1))
    else:
        zero_time = datetime(year=2020, month=12, day=31,
                             hour=get_item([lines], input_filter[49:52], based=1),
                             minute=get_item([lines], input_filter[55:58], based=1),
                             second=get_item([lines], input_filter[61:64], based=1))

    zero_datetime = datetime(zero_date.year, zero_date.month, zero_date.day, zero_time.hour,
                             zero_time.minute, zero_time.second).isoformat(timespec='seconds')

    step_list = [[[1, zero_datetime, name]]]
    break_num = 0
    step_num = 0
    for step_index in range(2000):
        start_row = input_filter[5] + input_filter[27] * step_num + input_filter[28] * step_num
        if lines[start_row] == "" or lines[start_row] == [""]:
            break
        if break_num < input_filter[28]:
            break_num += 1
            continue
        break_num = 0
        step_num += 1
        if input_filter[6] == 0:  # == 0, vertical
            step_list[0].append([
                str(step_num),
                # in sequence: Ar36, Ar37, Ar38, Ar39, Ar40
                float(lines[start_row + input_filter[25] - 1][input_filter[26] - 1]),
                float(lines[start_row + input_filter[25] - 1][input_filter[24] - 1]),
                float(lines[start_row + input_filter[21] - 1][input_filter[22] - 1]),
                float(lines[start_row + input_filter[21] - 1][input_filter[20] - 1]),
                float(lines[start_row + input_filter[17] - 1][input_filter[18] - 1]),
                float(lines[start_row + input_filter[17] - 1][input_filter[16] - 1]),
                float(lines[start_row + input_filter[13] - 1][input_filter[14] - 1]),
                float(lines[start_row + input_filter[13] - 1][input_filter[12] - 1]),
                float(lines[start_row + input_filter[9] - 1][input_filter[10] - 1]),
                float(lines[start_row + input_filter[9] - 1][input_filter[8] - 1]),
            ])
        else:  # == 1, horizontal
            step_list[0].append([
                str(step_num),
                # Ar36, Ar37, Ar38, Ar39, Ar40
                float(lines[start_row][input_filter[26] - 1]), float(lines[start_row][input_filter[24] - 1]),
                float(lines[start_row][input_filter[22] - 1]), float(lines[start_row][input_filter[20] - 1]),
                float(lines[start_row][input_filter[18] - 1]), float(lines[start_row][input_filter[16] - 1]),
                float(lines[start_row][input_filter[14] - 1]), float(lines[start_row][input_filter[12] - 1]),
                float(lines[start_row][input_filter[10] - 1]), float(lines[start_row][input_filter[8] - 1]),
            ])

    return step_list, sample_info


def get_sample_info(file_contents: list, input_filter: list) -> dict:
    """
    Parameters
    ----------
    file_contents
    input_filter

    Returns
    -------

    """
    sample_info = DEFAULT_SAMPLE_INFO.copy()
    sample_info.update({
        "Experiment Name": get_item(file_contents, input_filter[34:37], default="", based=1),
        "Sample Name": get_item(file_contents, input_filter[37:40], default="", based=1),
        "Sample Type": get_item(file_contents, input_filter[40:43], default="", based=1),
        "Step Label": get_item(file_contents, input_filter[43:46], default="", based=1),
        "Zero Date Year": get_item(file_contents, input_filter[46:49], default="", based=1),
        "Zero Time Hour": get_item(file_contents, input_filter[49:52], default="", based=1),
        "Zero Date Month": get_item(file_contents, input_filter[52:55], default="", based=1),
        "Zero Time Minute": get_item(file_contents, input_filter[55:58], default="", based=1),
        "Zero Date Day": get_item(file_contents, input_filter[58:61], default="", based=1),
        "Zero Time Second": get_item(file_contents, input_filter[61:64], default="", based=1),
        "Sample material": get_item(file_contents, input_filter[64:67], default="", based=1),
        "Sample location": get_item(file_contents, input_filter[67:70], default="", based=1),
        "Sample Weight": get_item(file_contents, input_filter[70:73], default="", based=1),
        "Experiment Type": get_item(file_contents, input_filter[73:76], default="", based=1),
        "Step name": get_item(file_contents, input_filter[76:79], default="", based=1),
        "Step unit": get_item(file_contents, input_filter[79:82], default="", based=1),
        "Heating time": get_item(file_contents, input_filter[82:85], default="", based=1),
        "Instrument name": get_item(file_contents, input_filter[85:88], default="", based=1),
        "Researcher": get_item(file_contents, input_filter[88:91], default="", based=1),
        "Analyst": get_item(file_contents, input_filter[91:94], default="", based=1),
        "Laboratory": get_item(file_contents, input_filter[94:97], default="", based=1),
        "J value": get_item(file_contents, input_filter[97:100], default="", based=1),
        "J value error": get_item(file_contents, input_filter[100:103], default="", based=1),
        "Calc params": get_item(file_contents, input_filter[103:106], default="", based=1),
        "Irra name": get_item(file_contents, input_filter[106:109], default="", based=1),
        "Irra label": get_item(file_contents, input_filter[109:112], default="", based=1),
        "Irra position H": get_item(file_contents, input_filter[112:115], default="", based=1),
        "Irra position X": get_item(file_contents, input_filter[115:118], default="", based=1),
        "Irra position Y": get_item(file_contents, input_filter[118:121], default="", based=1),
        "Standard name": get_item(file_contents, input_filter[121:124], default="", based=1),
        "Standard age": get_item(file_contents, input_filter[124:127], default="", based=1),
        "Standard age error": get_item(file_contents, input_filter[127:130], default="", based=1)
    })
    return sample_info

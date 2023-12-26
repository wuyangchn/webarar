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
from typing import List, Tuple, Dict, Union, Optional
import pandas as pd
import traceback
import os
from xlrd import open_workbook
from ..smp import RawData, Sample
from ..calc import raw_funcs, arr


def to_raw(file_path: Union[str, List[str]], **kwargs):
    """ Read raw data from files, can create raw data instance based on the given files
    Raw data will have the structure like:
        [
            [ [ sequence 0 header ], [ measurement cycle 0 data ], [ measurement cycle 1 data ], ...  ],
            [ [ sequence 1 header ], [ measurement cycle 0 data ], [ measurement cycle 1 data ], ...  ],
            ...
            [ [ sequence n - 1 header ], [ measurement cycle 0 data ], [ measurement cycle 1 data ], ...  ],
        ]
    Parameters
    ----------
    file_path
    kwargs

    Returns
    -------

    """
    if isinstance(file_path, list) and len(file_path) == 1:
        file_path: str = file_path[0]
    if isinstance(file_path, list):
        raw = concatenate([to_raw(file) for file in file_path])
    else:
        res = open_file(file_path)
        file_name = str(os.path.split(file_path)[-1]).split('.')[0]
        raw = RawData(name=file_name, data=res['data'], isotopic_num=10, sequence_num=len(res['data']),
                      source=file_path)
    return raw


def concatenate(raws: List[RawData]):
    """
    Parameters
    ----------
    raws

    Returns
    -------

    """
    source = [_raw.source for _raw in raws]
    sequence = [i for _raw in raws for i in _raw.sequence]
    sequence_num = len(sequence)
    return RawData(name='concatenated', source=source, isotopic_num=10, sequence_num=sequence_num,
                   sequence=sequence)


def to_sample(raw: RawData, mapping: Union[zip, list]) -> Sample:
    """
    Parameters
    ----------
    raw
    mapping

    Returns
    -------

    """
    ...


def set_data(raw: RawData, sequence_index: int, isotopic_index: int, data: List[List[float]]):
    """
    Parameters
    ----------
    raw
    sequence_index
    isotopic_index
    data

    Returns
    -------

    """
    ...


def get_data(raw: RawData, sequence_index: Optional[int], isotopic_index: Optional[int]) -> List[List[List[float]]]:
    """
    Parameters
    ----------
    raw
    sequence_index
    isotopic_index

    Returns
    -------

    """
    ...


def set_flag(raw: RawData, sequence_index: int, isotopic_index: int, data: List[List[float]]):
    """
    Parameters
    ----------
    raw
    sequence_index
    isotopic_index
    data

    Returns
    -------

    """
    # raw.flag[isotopic_index][sequence_index] = data
    ...


def get_flag(raw: RawData, sequence_index: Optional[int], isotopic_index: Optional[int]) -> List[List[float]]:
    """
    Parameters
    ----------
    raw
    sequence_index
    isotopic_index

    Returns
    -------

    """
    # return raw.flag[isotopic_index][sequence_index]
    ...


def get_result(raw: RawData, sequence_index: Optional[int], isotopic_index: Optional[int],
               method_index: Optional[List[List[Union[int, str]]]]) -> List[List[float]]:
    """
    Parameters
    ----------
    raw
    sequence_index
    isotopic_index
    method_index

    Returns
    -------

    """
    # return raw.results[isotopic_index][sequence_index][method_index]
    ...


def do_regression(raw: RawData, sequence_index: Optional[List], isotopic_index: Optional[List],
                  flag: Optional[List[List[float]]]):
    """
    Parameters
    ----------
    raw
    sequence_index
    isotopic_index
    flag

    Returns
    -------

    """
    # fitMethod = []
    # linesData, linesResults = [], []
    # selectedData, unselectedData = [], []
    # experimentTime, sequenceLabel, isBlank = [], [], []
    # sequenceName = []
    for sequence in raw.get_sequence(index=None):
        if hasattr(sequence_index, '__getitem__') and sequence.index not in sequence_index:
            continue
        isotope: pd.DataFrame = sequence.get_data_df()
        selected: pd.DataFrame = isotope[sequence.get_flag_df()[list(range(1, 11))]]
        unselected: pd.DataFrame = isotope[~sequence.get_flag_df()[list(range(1, 11))]]
        selected: list = [selected[[isotopic_index*2 + 1, 2 * (isotopic_index + 1)]].dropna().values.tolist()
                          for isotopic_index in list(range(5))]
        # unselected: list = [unselected[[isotopic_index*2 + 1, 2 * (isotopic_index + 1)]].dropna().values.tolist()
        #                     for isotopic_index in list(range(5))]

        for index, isotope in enumerate(selected):
            if hasattr(isotopic_index, '__getitem__') and index not in isotopic_index:
                continue
            res = raw_funcs.get_raw_data_regression_results(isotope)
            try:
                sequence.results[index] = res[1]
                sequence.coefficients[index] = res[2]
            except IndexError:
                sequence.results.insert(index, res[1])
                sequence.coefficients.insert(index, res[2])
            except TypeError:
                sequence.results = [res[1]]
                sequence.coefficients = [res[2]]

        # linesData.append([_res[0] for _res in res])
        # selectedData.append(selected)
        # unselectedData.append(unselected)
        # linesResults.append(sequence.results)
        # fitMethod.append(sequence.fitting_method)
        # experimentTime.append(sequence.datetime)
        # sequenceLabel.append(sequence.type_str)
        # isBlank.append(sequence.is_blank)
        # sequenceName.append(sequence.name)

    # raw_data = {
    #     'selectedData': selectedData, 'unselectedData': unselectedData, 'linesData': linesData,
    #     'linesResults': linesResults, 'fitMethod': fitMethod, 'sequenceLabel': sequenceLabel,
    #     'experimentTime': experimentTime, 'sequenceName': sequenceName, 'isBlank': isBlank
    # }
    #
    # return raw_data


def get_data_df(raw: RawData):
    """
    Parameters
    ----------
    raw

    Returns
    -------

    """
    return pd.DataFrame(raw.data)


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
        handler = {'xls': open_raw_xls, 'ahd': open_raw_ahd}[extension.lower()]
    except KeyError:
        print(traceback.format_exc())
        return False
    else:
        return {'data': handler(file_path), 'type': extension}


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

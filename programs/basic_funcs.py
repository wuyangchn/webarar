#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : basic_funcs.py
# @Author : Yang Wu
# @Date   : 2023/1/23
# @Email  : wuy@cug.edu.cn
import json
import copy
import traceback
from decimal import Decimal
from math import exp, log, cos, acos, ceil, sqrt
from programs import samples

def getJsonDumps(a):
    # return json.dumps(a, default=lambda o: o.__dict__ if hasattr(0, '__dict__') else o, sort_keys=True, indent=4)
    return json.dumps(a, cls=MyEncoder, indent=4)

def getJsonLoads(a):
    return json.loads(a)

def getIrradiationDatetimeByStr(datetime_str: str):
    res = []
    if datetime_str == '' or datetime_str is None:
        return ['', 0]
    cycles = datetime_str.split('S')
    for cycle in cycles:
        [dt, hrs] = cycle.split('D')
        [d, t1, t2] = dt.rsplit('-', 2)
        res = res + [d+'T'+t1+':'+t2, float(hrs)]
    return res

def getMethodFittingLawByStr(method_str: str):
    res = [False] * 3
    try:
        res[['Linear', 'Exponential', 'Power'].index(method_str.capitalize())] = True
    except ValueError:
        res[0] = True
    return res

# 从二维数组中选取指定区域内的部分
def getPartialArry(arry: list, start_row: int, length: int, *cols):
    """
    :param arry: 二维数组
    :param start_row: 开始行，从0开始
    :param length: 行数
    :param cols: 列编号，从0开始，逗号隔开, 如（list, 0, 10, 2, 3, 4）或者（list, 0, 10, *[1, 2, 3]）
    :return: 二维数组
    """
    res = []
    if len(cols) == 1:
        return arry[cols[0]][start_row: start_row+length]
    for each_col in cols:
        if each_col == -1:
            res.append([''] * length)
        elif each_col == -999:
            res.append([0] * length)
        elif each_col == 999:
            res.append([1] * length)
        else:
            res.append([arry[each_col][each_row] for each_row in range(start_row, start_row+length)])
    return res

def thisListIsEmpty(a):
    if not isinstance(a, list) or a == []:
        return True
    for i in a:
        if i not in ['', None]:
            return False
    return True

def removeNone(a: list):
    res = getTransposed(a)
    pop_index = []
    for index, arg in enumerate(res):
        if not isinstance(arg, (tuple, list)):
            return a
        if None in arg:
            pop_index.append(index)
    pop_index.reverse()
    for pop in pop_index:
        res.pop(pop)
    return getTransposed(res)

def getTransposed(a: list):
    try:
        n = max([len(i) for i in a])
        for i in a:
            for j in range(len(i), n):
                i.append('')
        return [[a[k][j] for k in range(len(a))] for j in range(min([len(i) for i in a]))]
    except (Exception, BaseException) as e:
        print(traceback.format_exc())
        return a

def updateDicts(a: dict, b: dict):
    """
    a and b, two dictionary. Return updated a
        For example:
            a = {"1": 1, "2": {"1": 1, "2": 2, "3": 3}}
            b = {"1": 'b', "2": {"1": 'b', "2": 'b'}}
            Will return {"1": 'b', "2": {"1": 'b', "2": 'b', "3": 3}}
    """
    res = {}
    for key, val in a.items():
        if key not in b.keys():
            res[key] = val
        elif isinstance(val, dict):
            res[key] = updateDicts(val, b[key])
        else:
            res[key] = b[key]
    return res

def mergeDicts(a: dict, b: dict):
    """
    a and b, two dictionary. Return updated a
        For example:
            a = {"1": 1, "2": {"1": 1, "2": 2, "3": 3, "5": {}, "6": [1, 2]}}
            b = {"1": 'b', "2": {"1": 'b', "2": 'b', "3": 'b', "4": 'b', "5": {"1": 'b'}, "6": [1, 2, 3]}}
            Will return {'1': 1, '2': {'1': 1, '2': 2, '3': 3, '5': {'1': 'b'}, '6': [1, 2], '4': 'b'}}
    """
    res = copy.deepcopy(a)
    for key, val in b.items():
        if key not in res.keys():
            res[key] = val
        elif isinstance(val, dict):
            res[key] = mergeDicts(res[key], val)
        else:
            continue
    return res

def getProducted(a1: list, a2: list, factor=None):
    if len(a1) != len(a2[0]):
        return []
    if factor is None:
        factor = 1
    return [[sum([a1[i][j] * a2[j][k] for j in range(len(a2))]) * factor for k in range(len(a1))] for i in range(len(a1))]

def setTableData(*args):
    n = max([len(i) for i in args])
    res = []
    for i in args:
        res = res + [i + [''] * (n - len(i))]
    return getTransposed(res)

def getIsochronSetData(total_data: list, set1_index: list, set2_index: list, unselected_index: list):
    set_1, set_2, unslected = [], [], []
    # Remove string and None type in data
    none_index = []
    for each in total_data:
        none_index = none_index + [key for key, val in enumerate(each) if isinstance(val, (str, type(None)))]
    none_index = list(set(none_index))
    none_index.sort(reverse=True)
    for each in total_data:
        for i in none_index:
            each.pop(i)
    set1_index.sort()
    set2_index.sort()
    for col in total_data:
        unslected.append([col[i] for i in unselected_index if i < len(col)])
        set_1.append([col[i] for i in set1_index if i < len(col)])
        set_2.append([col[i] for i in set2_index if i < len(col)])
    return set_1, set_2, unslected

def getScale(s, e, count=5):
    e = Decimal(str(e))
    s = Decimal(str(s))
    count = Decimal(count)
    interval = e - s
    mag = Decimal(10) ** Decimal(int(log(interval, 10))) if s >= 1 else Decimal(10) ** (Decimal(int(log(interval, 10))) - Decimal(1))
    _s, _e = s / mag, e / mag
    if isinstance((_e - _s) / count, int):
        return float(s), float(e), int(count), float(interval/count)
    count = Decimal(4)
    if isinstance((_e - _s) / count, int):
        return float(s), float(e), int(count), float(interval/count)
    count = Decimal(6)
    if isinstance((_e - _s) / count, int):
        return float(s), float(e), int(count), float(interval/count)
    count = Decimal(3)
    if isinstance((_e - _s) / count, int):
        return float(s), float(e), int(count), float(interval/count)
    count = Decimal(5)
    _e = Decimal(int(abs(_e)) + ceil((abs(_e) - int(abs(_e))) * 10) / 10) * [-1, 1][_e>=0] * mag
    _s = Decimal(int(abs(_s)) + ceil((abs(_s) - int(abs(_s))) * 10) / 10) * [-1, 1][_s>=0] * mag
    interval = (Decimal(str(_e)) - Decimal(str(_s)))
    count = int((e-s) * count / interval)
    return float(_s), float(_e), int(count), float(interval / Decimal(5))


class MyEncoder(json.JSONEncoder):
    from collections import namedtuple
    def default(self, obj):
        if isinstance(obj, complex):
            return "complex number"
        if isinstance(obj, (samples.Sample, samples.Info, samples.Plot, samples.Table,
            samples.Plot.Text, samples.Plot.Axis, samples.Plot.Label, samples.Plot.Set,
            samples.Plot.BasicAttr
        )):
            return obj.__dict__
        return super(MyEncoder, self).default(obj)

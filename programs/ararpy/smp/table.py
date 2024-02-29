#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - table
# ==========================================
#
#
#
"""
from .. import calc
from . import (sample as samples, basic)

Sample = samples.Sample
Table = samples.Table


# Table functions
def update_table_data(smp: Sample, only_table: str = None):
    """
    Update table data
    Parameters
    ----------
    smp
    only_table

    Returns
    -------

    """
    for key, comp in basic.get_components(smp).items():
        if not isinstance(comp, Table):
            continue
        if only_table is not None and key != only_table:
            continue
        if key == '1':
            data = calc.arr.merge(
                smp.SequenceName, smp.SequenceValue, *smp.SampleIntercept)
        elif key == '2':
            data = calc.arr.merge(
                smp.SequenceName, smp.SequenceValue, *smp.BlankIntercept)
        elif key == '3':
            data = calc.arr.merge(
                smp.SequenceName, smp.SequenceValue, *smp.CorrectedValues)
        elif key == '4':
            data = calc.arr.merge(
                smp.SequenceName, smp.SequenceValue, *smp.DegasValues)
        elif key == '5':
            data = calc.arr.merge(
                smp.SequenceName, smp.SequenceValue, *smp.PublishValues)
        elif key == '6':
            data = calc.arr.merge(
                smp.SequenceName, smp.SequenceValue, *smp.ApparentAgeValues)
        elif key == '7':
            data = calc.arr.merge(
                smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.IsochronValues)
        elif key == '8':
            data = calc.arr.merge(
                smp.SequenceName, smp.SequenceValue, *smp.TotalParam)
        else:
            data = [['']]
        # calc.arr.replace(data, pd.isnull, None)
        setattr(comp, 'data', calc.arr.transpose(data))


def update_handsontable(smp: Sample, data: list, id: str):
    """
    Parameters
    ----------
    smp : sample instance
    data : list
    id : str, table id

    Returns
    -------

    """

    def _normalize_data(a, cols, start_col=0):
        if len(a) >= cols:
            return a[start_col:cols]
        else:
            return a[start_col:] + [[''] * len(a[0])] * (cols - len(a))

    def _strToBool(cols):
        bools_dict = {
            'true': True, 'false': False, '1': True, '0': False, 'none': False,
        }
        return [bools_dict.get(str(col).lower(), False) for col in cols]
    try:
        smp.SequenceName = data[0]
    except IndexError:
        pass
    try:
        smp.SequenceValue = data[1]
    except IndexError:
        pass
    if id == '1':  # 样品值
        data = _normalize_data(data, 12, 2)
        smp.SampleIntercept = data
    elif id == '2':  # 本底值
        data = _normalize_data(data, 12, 2)
        smp.BlankIntercept = data
    elif id == '3':  # 校正值
        data = _normalize_data(data, 12, 2)
        smp.CorrectedValues = data
    elif id == '4':  #
        data = _normalize_data(data, 34, 2)
        smp.DegasValues = data
    elif id == '5':  # 发行表
        data = _normalize_data(data, 13, 2)
        smp.PublishValues = data
    elif id == '6':  # 年龄谱
        data = _normalize_data(data, 10, 2)
        smp.ApparentAgeValues = data
    elif id == '7':  # 等时线
        smp.IsochronMark = data[2]
        data = _normalize_data(data, 42, 3)
        smp.IsochronValues = data
        smp.SelectedSequence1 = [
            i for i in range(len(smp.IsochronMark)) if str(smp.IsochronMark[i]) == "1"]
        smp.SelectedSequence2 = [
            i for i in range(len(smp.IsochronMark)) if str(smp.IsochronMark[i]) == "2"]
        smp.UnselectedSequence = [
            i for i in range(len(smp.IsochronMark)) if
            i not in smp.SelectedSequence1 + smp.SelectedSequence2]
    elif id == '8':  # 总参数
        data = _normalize_data(data, 125, 2)
        data[103: 115] = [_strToBool(i) for i in data[103: 115]]
        smp.TotalParam = data
    else:
        raise ValueError(f"{id = }, The table id is not supported.")
    update_table_data(smp, only_table=id)  # Update data of tables after changes of a table



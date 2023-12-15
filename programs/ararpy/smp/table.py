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
# === Internal imports ===
# from programs.ararpy import calc
from . import *
# from programs.ararpy.smp import basic

# === External imports ===
# from programs import samples
#
#
# Sample = samples.Sample
# Info = samples.Info
# Table = samples.Table
# Plot = samples.Plot
# Set = samples.Plot.Set


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
        # setattr(comp, 'data', data)


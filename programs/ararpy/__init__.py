#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# webarar - __init__.py
# ==========================================
#
# ArArPy
#
"""


from . import calc, smp, files

york2 = calc.regression.york2
wtd_3D_regression = calc.regression.wtd_3D_regression

recalculate = smp.calculation.recalculate

name = "ararpy"

Sample = smp.samples.Sample
Info = smp.samples.Info
Table = smp.samples.Table
Plot = smp.samples.Plot
Set = smp.samples.Plot.Set
Label = smp.samples.Plot.Label
Axis = smp.samples.Plot.Axis
Text = smp.samples.Plot.Text
Basic = smp.samples.Basic

VERSION = smp.samples.VERSION

""" define functions and attributions for Sample class """
Sample.name = lambda _smp: _smp.Info.sample.name
Sample.doi = lambda _smp: _smp.Doi
Sample.sample = lambda _smp: _smp.Info.sample
Sample.researcher = lambda _smp: _smp.Info.researcher
Sample.laboratory = lambda _smp: _smp.Info.laboratory

Sample.results = lambda _smp: Basic(
    isochron=Basic(**dict((key, Basic(
        **dict(({2: 'unselected', 0: 'set1', 1: 'set2'}[_key], Basic(**_value))
               for (_key, _value) in value.items())))
                          for (key, value) in _smp.Info.results.isochron.items())),
    age_plateau=Basic(
        **dict(({2: 'unselected', 0: 'set1', 1: 'set2'}[key], Basic(**value))
               for (key, value) in _smp.Info.results.age_plateau.items()))
)
Sample.sequence = lambda _smp: Basic(
    size=len(_smp.SequenceName), name=_smp.SequenceName,
    value=_smp.SequenceValue, unit=_smp.SequenceUnit,
)
Sample.iso_mark = lambda _smp: Basic(
    size=len(_smp.IsochronMark),
    set1=Basic(
        size=sum([1 if i == 1 else 0 for i in _smp.IsochronMark]),
        index=[index for index, _ in enumerate(_smp.IsochronMark) if _ == 1],
    ),
    set2=Basic(
        size=sum([1 if i == 2 else 0 for i in _smp.IsochronMark]),
        index=[index for index, _ in enumerate(_smp.IsochronMark) if _ == 2],
    ),
    unselected=Basic(
        size=sum([0 if i == 2 or i == 1 else 1 for i in _smp.IsochronMark]),
        index=[index for index, _ in enumerate(_smp.IsochronMark) if _ != 1 and _ != 2],
    ),
    value=_smp.IsochronMark,
)

Sample.initial = smp.initial.initial
Sample.set_selection = lambda _smp, _index, _mark: smp.plots.set_selection(_smp, _index, _mark)
Sample.update_table = lambda _smp, _data, _id: smp.table.update_handsontable(_smp, _data, _id)

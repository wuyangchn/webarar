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
import os

import pandas as pd
from . import calc, smp, files

""" classes """
Sample = smp.samples.Sample
Info = smp.samples.Info
Table = smp.samples.Table
Plot = smp.samples.Plot
Set = smp.samples.Plot.Set
Label = smp.samples.Plot.Label
Axis = smp.samples.Plot.Axis
Text = smp.samples.Plot.Text


class ArArBasic:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class ArArData(ArArBasic):
    def __init__(self, **kwargs):
        self.data: list = []
        self.header: list = []
        super().__init__(**kwargs)
        if not isinstance(self.data, list):
            raise TypeError(f"Data must be a list.")
        if len(self.header) != len(self.data):
            self.header = [*self.header, *list(range(len(self.header), len(self.data)))][:len(self.data)]

    def to_df(self) -> pd.DataFrame: return pd.DataFrame(self.data, index=self.header).transpose()
    def to_list(self) -> list: return self.data


""" information for ararpy """
name = 'ararpy'
version = '0.0.1.a3'
__version__ = version
full_version = version
last_update = '2023-12-17'

""" functions and attributions for ararpy """
from_arr = files.arr_file.to_sample
from_age = files.calc_file.to_sample
from_full = files.calc_file.full_to_sample
from_empty = files.new_file.to_sample

""" define functions and attributions for Sample class """
Sample.name = lambda _smp: _smp.Info.sample.name
Sample.doi = lambda _smp: _smp.Doi
Sample.sample = lambda _smp: _smp.Info.sample
Sample.researcher = lambda _smp: _smp.Info.researcher
Sample.laboratory = lambda _smp: _smp.Info.laboratory

Sample.results = lambda _smp: ArArBasic(
    isochron=ArArBasic(**dict(
        (
            {
                'figure_2': 'normal', 'figure_3': 'inverse', 'figure_4': 'cl_1',
                'figure_5': 'cl_2', 'figure_6': 'cl_3', 'figure_7': 'three_d'
            }[key],
            ArArBasic(
                **dict(
                    (
                        {2: 'unselected', 0: 'set1', 1: 'set2'}[_key],
                        ArArBasic(**_value)
                    ) for (_key, _value) in value.items()
                )
            )
        ) for (key, value) in _smp.Info.results.isochron.items())),
    age_plateau=ArArBasic(
        **dict(({2: 'unselected', 0: 'set1', 1: 'set2'}[key], ArArBasic(**value))
               for (key, value) in _smp.Info.results.age_plateau.items()))
)
Sample.sequence = lambda _smp: ArArBasic(
    size=len(_smp.SequenceName), name=_smp.SequenceName,
    value=_smp.SequenceValue, unit=_smp.SequenceUnit,
    mark=ArArBasic(
        size=len(_smp.IsochronMark),
        set1=ArArBasic(
            size=sum([1 if i == 1 else 0 for i in _smp.IsochronMark]),
            index=[index for index, _ in enumerate(_smp.IsochronMark) if _ == 1],
        ),
        set2=ArArBasic(
            size=sum([1 if i == 2 else 0 for i in _smp.IsochronMark]),
            index=[index for index, _ in enumerate(_smp.IsochronMark) if _ == 2],
        ),
        unselected=ArArBasic(
            size=sum([0 if i == 2 or i == 1 else 1 for i in _smp.IsochronMark]),
            index=[index for index, _ in enumerate(_smp.IsochronMark) if _ != 1 and _ != 2],
        ),
        value=_smp.IsochronMark,
    )
)

Sample.initial = smp.initial.initial
Sample.set_selection = lambda _smp, _index, _mark: smp.plots.set_selection(_smp, _index, _mark)
Sample.update_table = lambda _smp, _data, _id: smp.table.update_handsontable(_smp, _data, _id)

Sample.unknown = lambda _smp: ArArData(
    name='unknown', data=_smp.SampleIntercept
)
Sample.blank = lambda _smp: ArArData(
    name='blank', data=_smp.BlankIntercept
)
Sample.parameters = lambda _smp: ArArData(
    name='parameters', data=_smp.TotalParam
)
Sample.corrected = lambda _smp: ArArData(
    name='parameters', data=_smp.CorrectedValues
)
Sample.degas = lambda _smp: ArArData(
    name='parameters', data=_smp.DegasValues
)
Sample.isochron = lambda _smp: ArArData(
    name='isochron', data=_smp.IsochronValues
)
Sample.apparent_ages = lambda _smp: ArArData(
    name='apparent_ages', data=_smp.ApparentAgeValues
)
Sample.publish = lambda _smp: ArArData(
    name='publish', data=_smp.PublishValues
)

Sample.corr_blank = smp.corr.corr_blank
Sample.corr_massdiscr = smp.corr.corr_massdiscr
Sample.corr_decay = smp.corr.corr_decay
Sample.corr_ca = smp.corr.calc_degas_ca
Sample.corr_k = smp.corr.calc_degas_k
Sample.corr_cl = smp.corr.calc_degas_cl
Sample.corr_atm = smp.corr.calc_degas_atm
Sample.corr_r = smp.corr.calc_degas_r
Sample.calc_ratio = smp.corr.calc_ratio

Sample.recalculate = lambda _smp, **kwargs: smp.calculation.recalculate(_smp, **kwargs)

Sample.show_data = lambda _smp: \
    f"Sample Name: \n\t{_smp.name()}\n" \
    f"Doi: \n\t{_smp.doi()}\n" \
    f"Corrected Values: \n\t{_smp.corrected().to_df()}\n" \
    f"Parameters: \n\t{_smp.parameters().to_df()}\n" \
    f"Isochron Values: \n\t{_smp.isochron().to_df()}\n" \
    f"Apparent Ages: \n\t{_smp.apparent_ages().to_df()}\n" \
    f"Publish Table: \n\t{_smp.publish().to_df()}\n"

__tab = "\t"
Sample.help = f"" \
              f"builtin methods:\n " \
              f"{__tab.join([func for func in dir(Sample) if callable(getattr(Sample, func)) and func.startswith('__')])}\n" \
              f"dunder-excluded methods:\n " \
              f"{__tab.join([func for func in dir(Sample) if callable(getattr(Sample, func)) and not func.startswith('__')])}\n"


def test():
    example_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'examples')
    print(f"Running: ararpy.test()")
    print(f"============= Open an example .arr file =============")
    file_path = os.path.join(example_dir, r'22WHA0433.arr')
    print(f"{file_path = }")
    print(f"sample = from_arr(file_path=file_path)")
    sample = from_arr(file_path=file_path)
    print(f"{sample.name() = }")
    print(f"{sample.help = }")
    print(f"sample.parameters() = {sample.parameters()}")
    print(f"sample.parameters().to_df() = \n{sample.parameters().to_df()}")

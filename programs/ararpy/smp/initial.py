#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - initial
# ==========================================
#
#
#
"""

import uuid
import pandas as pd
import numpy as np
import copy

from . import (sample as samples, basic)

Sample = samples.Sample
Info = samples.Info
Table = samples.Table
Plot = samples.Plot

plateau_res_keys = [
    'F', 'sF', 'Num', 'MSWD', 'Chisq', 'Pvalue', 'age', 's1', 's2', 's3', 'Ar39',
    'rs',  # 'rs' means relative error of the total sum
]
PLATEAU_RES = dict(zip(plateau_res_keys, [np.nan] * len(plateau_res_keys)))
iso_res_keys = [
    'k', 'sk', 'm1', 'sm1',
    'MSWD', 'abs_conv', 'iter', 'mag', 'R2', 'Chisq', 'Pvalue',
    'rs',  # 'rs' means relative error of the total sum
    'age', 's1', 's2', 's3',
    'conv', 'initial', 'sinitial', 'F', 'sF',
]
ISO_RES = dict(zip(
    iso_res_keys, [np.nan] * len(iso_res_keys))
)


# create sample instance
def create_sample_from_df(content: pd.DataFrame, smp_info: dict):
    """

    Parameters
    ----------
    content : [
            sample_values, blank_values, corrected_values, degas_values, publish_values,
            apparent_age_values, isochron_values, total_param, sample_info, isochron_mark,
            sequence_name, sequence_value
        ]
    smp_info : dict

    Returns
    -------
    Sample instance
    """
    content_dict = content.to_dict('list')
    res = dict(zip([key[0] for key in content_dict.keys()], [[]] * len(content_dict)))
    for key, val in content_dict.items():
        res[key[0]] = res[key[0]] + [val]

    return create_sample_from_dict(content=res, smp_info=smp_info)


def create_sample_from_dict(content: dict, smp_info: dict):
    """
    content:
        {
            'smp': [], 'blk': [], 'cor': [], 'deg': [], 'pub': [],
            'age': [], 'iso': [], 'pam': [], 'mak': [], 'seq': [],
            'seq': []
        }
    return sample instance
    """
    # Create sample file
    smp = Sample()
    # Initializing
    initial(smp)
    smp.SampleIntercept = content['smp']
    smp.BlankIntercept = content['blk']
    smp.CorrectedValues = content['cor']
    smp.DegasValues = content['deg']
    smp.PublishValues = content['pub']
    smp.ApparentAgeValues = content['age']
    smp.IsochronValues = content['iso']
    smp.TotalParam = content['pam']
    smp.IsochronMark = content['mak'][0]
    smp.SequenceName = content['seq'][0]
    smp.SequenceValue = content['seq'][1]

    basic.update_plot_from_dict(smp.Info, smp_info)

    smp.SelectedSequence1 = [index for index, item in enumerate(smp.IsochronMark) if item == 1]
    smp.SelectedSequence2 = [index for index, item in enumerate(smp.IsochronMark) if item == 2]
    smp.UnselectedSequence = [index for index, item in enumerate(smp.IsochronMark) if item not in [1, 2]]

    return smp


def initial(smp: Sample):
    # 已更新 2023/7/4
    smp.TotalParam = [[]] * 123
    smp.BlankIntercept = [[]] * 10
    smp.SampleIntercept = [[]] * 10
    smp.PublishValues = [[]] * 11
    smp.DecayCorrected = [[]] * 10
    smp.CorrectedValues = [[]] * 10
    smp.DegasValues = [[]] * 32
    smp.ApparentAgeValues = [[]] * 8
    smp.IsochronValues = [[]] * 47

    # Doi
    if not hasattr(smp, 'Doi') or getattr(smp, 'Doi') is None:
        setattr(smp, 'Doi', str(uuid.uuid4().hex))

    # Info
    setattr(smp, 'Info', Info(
        id='0', name='info', attr_name='Info',
        sample=Info(
            name='SAMPLE NAME', material='MATERIAL', location='LOCATION'
        ),
        researcher=Info(
            name='RESEARCHER', addr='ADDRESS', email='EMAIL'
        ),
        laboratory=Info(
            name='LABORATORY', addr='ADDRESS', email='EMAIL', info='INFORMATION', analyst='ANALYST'
        ),
        results=Info(
            name='RESULTS', plateau_F=[], plateau_age=[], total_F=[], total_age=[],
            isochron_F=[], isochron_age=[], J=[],
            # set1=result_set_1, set2=result_set_2,
            isochron={
                'figure_2': {
                    0: copy.deepcopy(ISO_RES), 1: copy.deepcopy(ISO_RES), 2: copy.deepcopy(ISO_RES)},
                'figure_3': {
                    0: copy.deepcopy(ISO_RES), 1: copy.deepcopy(ISO_RES), 2: copy.deepcopy(ISO_RES)},
                'figure_4': {
                    0: copy.deepcopy(ISO_RES), 1: copy.deepcopy(ISO_RES), 2: copy.deepcopy(ISO_RES)},
                'figure_5': {
                    0: copy.deepcopy(ISO_RES), 1: copy.deepcopy(ISO_RES), 2: copy.deepcopy(ISO_RES)},
                'figure_6': {
                    0: copy.deepcopy(ISO_RES), 1: copy.deepcopy(ISO_RES), 2: copy.deepcopy(ISO_RES)},
                'figure_7': {
                    0: copy.deepcopy(ISO_RES), 1: copy.deepcopy(ISO_RES), 2: copy.deepcopy(ISO_RES)},
            },
            age_plateau={
                0: copy.deepcopy(PLATEAU_RES), 1: copy.deepcopy(PLATEAU_RES), 2: copy.deepcopy(PLATEAU_RES)},
            age_spectra={},
        ),
        reference=Info(
            name='REFERENCE', journal='JOURNAL', doi='DOI'
        ),
    ))

    # Plots and Tables
    setattr(smp, 'UnknownTable', Table(
        id='1', name='Unknown', header=samples.SAMPLE_INTERCEPT_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 20))
    ))
    setattr(smp, 'BlankTable', Table(
        id='2', name='Blank', header=samples.BLANK_INTERCEPT_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 20))
    ))
    setattr(smp, 'CorrectedTable', Table(
        id='3', name='Corrected', header=samples.CORRECTED_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 35))
    ))
    setattr(smp, 'DegasPatternTable', Table(
        id='4', name='Degas Pattern', header=samples.DEGAS_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 35))
    ))
    setattr(smp, 'PublishTable', Table(
        id='5', name='Publish', header=samples.PUBLISH_TABLE_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 20))
    ))
    setattr(smp, 'AgeSpectraTable', Table(
        id='6', name='Age Spectra', header=samples.SPECTRUM_TABLE_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 26))
    ))
    setattr(smp, 'IsochronsTable', Table(
        id='7', name='Isochrons', header=samples.ISOCHRON_TABLE_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 42))
    ))
    setattr(smp, 'TotalParamsTable', Table(
        id='8', name='Total Params', header=samples.TOTAL_PARAMS_HEADERS,
        textindexs=[0, 29, 30, 32, 33, 60, 99, 102, *list(range(103, 115))],
        # numericindexs=list(range(1, 120)),
        numericindexs=[1],
    ))

    initial_plot_styles(smp)

    return smp


def initial_plot_styles(sample: Sample, except_attrs=None):
    """
    Initialize plot components styles based on Default Styles. Except attrs is a list containing attrs
    that are not expected to be initialized.
    Judgment order:
        1. The attr name is in except attrs and the sample has this attr: skip
        2. The value is not a dict instance: setattr()
        3. The sample has attr and it is a Set/Label/Text/Axis instance: iteration
    """

    if except_attrs is None:
        except_attrs = []

    def set_attr(obj, name, value):
        if name in except_attrs and hasattr(obj, name):
            pass
        elif not isinstance(value, dict):
            setattr(obj, name, value)
        else:
            if not (hasattr(obj, name) and isinstance(getattr(obj, name), Plot.BasicAttr)):
                setattr(obj, name, getattr(Plot, value['type'].capitalize())())
            for k, v in value.items():
                set_attr(getattr(obj, name), k, v)

    default_styles = copy.deepcopy(samples.DEFAULT_PLOT_STYLES)
    for figure_index, figure_attr in default_styles.items():
        plot = getattr(sample, figure_attr['attr_name'], Plot())
        for key, attr in figure_attr.items():
            set_attr(plot, key, attr)


def re_set_smp(sample: Sample):
    std = initial(Sample())
    basic.get_merged_smp(sample, std)
    return sample

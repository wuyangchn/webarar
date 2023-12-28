#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : sample.py
# @Author : Yang Wu
# @Date   : 2021/12/19
# @Email  : wuy@cug.edu.cn

"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - sample
# ==========================================
#
#
#

Create a sample instance.

"""
from typing import List, Tuple, Dict, Optional, Union
from types import MethodType

NEW_SAMPLE_INTERCEPT_HEADERS = [
    'Sequence', '', '\u00B3\u2076Ar', '1\u03C3', '\u00B3\u2077Ar', '1\u03C3',
    '\u00B3\u2078Ar', '1\u03C3', '\u00B3\u2079Ar', '1\u03C3', '\u2074\u2070Ar', '1\u03C3'
]
NEW_BLANK_INTERCEPT_HEADERS = [
    'Sequence', '', '\u00B3\u2076Ar', '1\u03C3', '\u00B3\u2077Ar', '1\u03C3',
    '\u00B3\u2078Ar', '1\u03C3', '\u00B3\u2079Ar', '1\u03C3', '\u2074\u2070Ar', '1\u03C3'
]
NEW_PARAMS_HEADERS = []

SAMPLE_INTERCEPT_HEADERS = [
    'Sequence', '', '\u00B3\u2076Ar', '1\u03C3', '\u00B3\u2077Ar', '1\u03C3',
    '\u00B3\u2078Ar', '1\u03C3', '\u00B3\u2079Ar', '1\u03C3', '\u2074\u2070Ar', '1\u03C3'
]
BLANK_INTERCEPT_HEADERS = [
    'Sequence', '', '\u00B3\u2076Ar', '1\u03C3', '\u00B3\u2077Ar', '1\u03C3',
    '\u00B3\u2078Ar', '1\u03C3', '\u00B3\u2079Ar', '1\u03C3', '\u2074\u2070Ar', '1\u03C3'
]

CORRECTED_HEADERS = [
    'Sequence', '', '\u00B3\u2076Ar', '1\u03C3', '\u00B3\u2077Ar', '1\u03C3',
    '\u00B3\u2078Ar', '1\u03C3', '\u00B3\u2079Ar', '1\u03C3', '\u2074\u2070Ar', '1\u03C3'
]

DEGAS_HEADERS = [
    'Sequence', '',  # 0-1
    '\u00B3\u2076Ar[a]', '1\u03C3', '\u00B3\u2076Ar[c]', '1\u03C3',  # 2-5
    '\u00B3\u2076Ar[Ca]', '1\u03C3', '\u00B3\u2076Ar[Cl]', '1\u03C3',  # 6-9
    '\u00B3\u2077Ar[Ca]', '1\u03C3', '\u00B3\u2078Ar[Cl]', '1\u03C3',  # 10-13
    '\u00B3\u2078Ar[a]', '1\u03C3', '\u00B3\u2078Ar[c]', '1\u03C3',  # 14-17
    '\u00B3\u2078Ar[K]', '1\u03C3', '\u00B3\u2078Ar[Ca]', '1\u03C3',  # 18-21
    '\u00B3\u2079Ar[K]', '1\u03C3', '\u00B3\u2079Ar[Ca]', '1\u03C3',  # 22-25
    '\u2074\u2070Ar[r]', '1\u03C3', '\u2074\u2070Ar[a]', '1\u03C3',  # 26-29
    '\u2074\u2070Ar[c]', '1\u03C3', '\u2074\u2070Ar[K]', '1\u03C3'  # 29-32
]

PUBLISH_TABLE_HEADERS = [
    'Sequence', '', '\u00B3\u2076Ar[a]', '\u00B3\u2077Ar[Ca]', '\u00B3\u2078Ar[Cl]',
    '\u00B3\u2079Ar[K]', '\u2074\u2070Ar[r]', 'Apparent Age', '1\u03C3', '\u2074\u2070Arr%',
    '\u00B3\u2079ArK%', 'Ca/K', '1\u03C3'
]
SPECTRUM_TABLE_HEADERS = [
    'Sequence', '', '\u2074\u2070Ar/\u00B3\u2079Ar', '1\u03C3', 'Apparent Age',
    '1\u03C3', '1\u03C3', '1\u03C3', '\u2074\u2070Ar[r]%', '\u00B3\u2079Ar[K]%'
]
ISOCHRON_TABLE_HEADERS = [
    'Sequence', '', 'Mark',  # 0-2
    '\u00B3\u2079Ar[K]/\u00B3\u2076Ar[a]', '1\u03C3',  # 3-4
    '\u2074\u2070Ar[r+a]/\u00B3\u2076Ar[a]', '1\u03C3', 'ri', '',  # 5-8
    '\u00B3\u2079Ar[K]/\u2074\u2070Ar[r+a]', '1\u03C3',  # 9-10
    '\u00B3\u2076Ar[a]/\u2074\u2070Ar[r+a]', '1\u03C3', 'ri', '',  # 11-14
    '\u00B3\u2079Ar[K]/\u00B3\u2078Ar[Cl]', '1\u03C3',  # 15-16
    '\u2074\u2070Ar[r+Cl]/\u00B3\u2078Ar[Cl]', '1\u03C3', 'ri', '',  # 17-20
    '\u00B3\u2079Ar[K]/\u2074\u2070Ar[r+Cl]', '1\u03C3',  # 21-22
    '\u00B3\u2078Ar[Cl]/\u2074\u2070Ar[r+Cl]', '1\u03C3', 'ri', '',  # 23-26
    '\u00B3\u2078Ar[Cl]/\u00B3\u2079Ar[K]', '1\u03C3',  # 27-28
    '\u2074\u2070Ar[r+Cl]/\u00B3\u2079Ar[K]', '1\u03C3', 'ri', '',  # 29-32
    '\u00B3\u2076Ar[a+Cl]/\u2074\u2070Ar[r+a]', '1\u03C3',  # 33-34
    '\u00B3\u2078Ar[a+Cl]/\u2074\u2070Ar[r+a]', '1\u03C3',  # 35-36
    '\u00B3\u2079Ar[K]/\u2074\u2070Ar[r+a]', '1\u03C3',  # 37-38
    'r1', 'r2', 'r3',  # 39-41
]
TOTAL_PARAMS_HEADERS = [
    'Sequence', '',  # 0-1
    '(\u2074\u2070Ar/\u00B3\u2076Ar)t', '%1\u03C3',
    '(\u2074\u2070Ar/\u00B3\u2076Ar)c', '%1\u03C3',  # 2-5
    '(\u00B3\u2078Ar/\u00B3\u2076Ar)t', '%1\u03C3',
    '(\u00B3\u2078Ar/\u00B3\u2076Ar)c', '%1\u03C3',  # 6-9
    '(\u00B3\u2079Ar/\u00B3\u2077Ar)Ca', '%1\u03C3',
    '(\u00B3\u2078Ar/\u00B3\u2077Ar)Ca', '%1\u03C3',
    '(\u00B3\u2076Ar/\u00B3\u2077Ar)Ca', '%1\u03C3',  # 10-15
    '(\u2074\u2070Ar/\u00B3\u2079Ar)K', '%1\u03C3',
    '(\u00B3\u2078Ar/\u00B3\u2079Ar)K', '%1\u03C3',  # 16-19
    '(\u00B3\u2076Ar/\u00B3\u2078Ar)Cl', '%1\u03C3',  # 20-21
    'K/Ca', '%1\u03C3', 'K/Cl', '%1\u03C3', 'Ca/Cl', '%1\u03C3',  # 22-27
    'Cycle Number', 'Irradiation Cycles',  # 28-29
    'Irradiation', 'duration', 'Irradiation Time', 'Experiment Time',  # 30-33
    'Storage Years', '',  # 34-35
    'Decay Constant \u2074\u2070K', '%1\u03C3',  # 36-37
    'Decay Constant \u2074\u2070K(EC)', '%1\u03C3',  # 38-39
    'Decay Constant \u2074\u2070K(\u03B2<sup>-</sup>)', '%1\u03C3',  # 40-41
    'Decay Constant \u2074\u2070K(\u03B2<sup>+</sup>)', '%1\u03C3',  # 42-43
    'Decay Constant \u00B3\u2079Ar', '%1\u03C3',  # 44-45
    'Decay Constant \u00B3\u2077Ar', '%1\u03C3',  # 46-47
    'Decay Constant \u00B3\u2076Cl', '%1\u03C3',  # 48-49
    'Decay Activity \u2074\u2070K', '%1\u03C3',  # 50-51
    'Decay Activity \u2074\u2070K(EC)', '%1\u03C3',  # 52-53
    'Decay Activity \u2074\u2070K(\u03B2<sup>-</sup>)', '%1\u03C3',  # 54-55
    'Decay Activity \u2074\u2070K(\u03B2<sup>+</sup>)', '%1\u03C3',  # 56-57
    '\u00B3\u2076Cl/\u00B3\u2078Cl Productivity', '%1\u03C3',  # 58-59
    'Std Name', 'Std Age', '1\u03C3', '\u2074\u2070Ar%', '1\u03C3', 'K%', '1\u03C3',
    '\u2074\u2070Ar<sup>*</sup>/K', '1\u03C3',  # 60-68
    'J', '%1\u03C3', 'MDF', '%1\u03C3',  # 69-72
    'Mass \u00B3\u2076Ar', '%1\u03C3', 'Mass \u00B3\u2077Ar', '%1\u03C3',
    'Mass \u00B3\u2078Ar', '%1\u03C3', 'Mass \u00B3\u2079Ar', '%1\u03C3',
    'Mass \u2074\u2070', '%1\u03C3', 'K Mass', '%1\u03C3',  # 73-84
    'No', '%1\u03C3', 'Year', '%1\u03C3', '\u2074\u2070K/K', '%1\u03C3',
    '\u00B3\u2075/\u00B3\u2077Cl', '%1\u03C3', 'HCl/Cl', '%1\u03C3',  # 85-94
    '\u2074\u2070Ar/\u00B3\u2076Ar air', '%1\u03C3',
    '\u00B3\u2078Ar/\u00B3\u2076Ar air', '%1\u03C3',  # 95-98
    'Isochron Fitting', 'Convergence', 'Iteration', 'Discrimination',  # 99-102
    'Not Zero', 'Corr Blank', 'Corr Discr', 'Corr \u00B3\u2077Ar Decay',
    'Corr \u00B3\u2079Ar Decay',  # 103-107
    'Ca Degassing', 'K Degassing', 'Cl Degassing', 'Trap Degassing',  # 108-111
    'Using Min Equation',
    # 'Recalibration', 'Using Std Age', 'Use Std Ratio',  # 112-115  to be completed
    '', '', '',  # 112-115
    'Auto Plateau Method',  # 116 the index includes sequence name and unit
    'Initial Ratio Model',  # 117
    'Set1 initial Ratio',  # 118
    '1\u03C3',  # 119
    'Set2 initial Ratio',  # 120
    '1\u03C3',  # 121
    'Isotopic Errors',  # 122
    'Parameter Errors',  # 123
    'Plot Errors',  # 124
]

DEFAULT_PLOT_STYLES = {
    'figure_1': {
        'id': 'figure_1', 'name': 'Age Spectra', 'type': 'spectra', 'attr_name': 'AgeSpectraPlot',
        'rightside_text': [],
        'title': {'id': 'title', 'show': True, 'text': 'Age Spectra', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text', 'font_weight': 'bolder',
                  'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': 'Cumulative {sup|39}Ar Released (%)', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': 'Apparent Age (Ma)', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'set1': {'id': 'Points Set 1', 'type': 'set', },
        'set2': {'id': 'Points Set 2', 'type': 'set', },
        'set3': {'id': 'Points Set 3', 'type': 'set', },
        'set4': {'id': 'Points Set 4', 'type': 'set', },
        'set5': {'id': 'Points Set 5', 'type': 'set', },
        'line1': {
            'id': 'Spectra Line 1', 'color': '#333333', 'line_type': 'solid',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line2': {
            'id': 'Spectra Line 2', 'color': '#333333', 'line_type': 'solid',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line3': {
            'id': 'Set1 Line 1', 'color': '#FF0000', 'line_type': 'solid',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line4': {
            'id': 'Set1 Line 2', 'color': '#FF0000', 'line_type': 'solid',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line5': {
            'id': 'Set2 Line 1', 'color': '#00B0F0', 'line_type': 'solid',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line6': {
            'id': 'Set2 Line 2', 'color': '#00B0F0', 'line_type': 'solid',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line7': {
            'id': 'Set4 Line 1', 'color': '#FF0000', 'line_type': 'dashed',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line8': {
            'id': 'Set4 Line 2', 'color': '#FF0000', 'line_type': 'dashed',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line9': {
            'id': 'Set5 Line 1', 'color': '#00B0F0', 'line_type': 'dashed',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'line10': {
            'id': 'Set5 Line 2', 'color': '#00B0F0', 'line_type': 'dashed',
            'line_width': 2, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                      'color': '#252525'}
        },
        'text1': {
            'id': 'Text for Set 1', 'show': True, 'font_size': 16, 'color': '#FF0000', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'text2': {
            'id': 'Text for Set 2', 'show': True, 'font_size': 16, 'color': '#00B0F0', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                  'color': '#252525'}
    },
    'figure_2': {
        'id': 'figure_2', 'name': 'Normal Isochron', 'type': 'isochron', 'attr_name': 'NorIsochronPlot',
        'rightside_text': [],
        'ellipse': {
            'id': 'ellipse', 'color': 'none', 'border_color': '#333333', 'border_type': 'solid',
            'show': False, 'fill': False,
            'border_width': 1, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
        },
        'title': {'id': 'title', 'show': True, 'text': '', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text',
                  'font_weight': 'bolder', 'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': '{sup|39}Ar{sub|K} / {sup|36}Ar{sub|a}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': '{sup|40}Ar{sup|*} / {sup|36}Ar{sub|a}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'set1': {
            'id': 'Points Set 1', 'color': '#FF0000', 'border_color': '#FF0000', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set2': {
            'id': 'Points Set 2', 'color': '#00B0F0', 'border_color': '#00B0F0', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set3': {
            'id': 'Unselected Points', 'color': '#FFFFFF', 'border_color': '#222222', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'line1': {
            'id': 'Line for Set 1', 'type': 'set', 'color': '#FF0000', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'line2': {
            'id': 'Line for Set 2', 'type': 'set', 'color': '#00B0F0', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'errline': {
            'id': 'Error Lines', 'type': 'set', 'color': '#333333', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label'}, 'show': True
        },
        'text1': {
            'id': 'Text for Set 1', 'show': True, 'font_size': 16, 'color': '#FF0000', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'text2': {
            'id': 'Text for Set 2', 'show': True, 'font_size': 16, 'color': '#00B0F0', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                  'color': '#252525'}
    },
    'figure_3': {
        'id': 'figure_3', 'name': 'Inverse Isochron', 'type': 'isochron', 'attr_name': 'InvIsochronPlot',
        'rightside_text': [],
        'title': {'id': 'title', 'show': True, 'text': '', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text',
                  'font_weight': 'bolder', 'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': '{sup|39}Ar{sub|K} / {sup|40}Ar{sup|*}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': '{sup|36}Ar{sub|a} / {sup|40}Ar{sup|*}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'ellipse': {
            'id': 'ellipse', 'color': 'none', 'border_color': '#333333', 'border_type': 'solid',
            'show': False, 'fill': False,
            'border_width': 1, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
        },
        'set1': {
            'id': 'Points Set 1', 'color': '#FF0000', 'border_color': '#FF0000', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set2': {
            'id': 'Points Set 2', 'color': '#00B0F0', 'border_color': '#00B0F0', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set3': {
            'id': 'Unselected Points', 'color': '#FFFFFF', 'border_color': '#222222', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'line1': {
            'id': 'Line for Set 1', 'type': 'set', 'color': '#FF0000', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label', }
        },
        'line2': {
            'id': 'Line for Set 2', 'type': 'set', 'color': '#00B0F0', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label', }
        },
        'errline': {
            'id': 'Error Lines', 'type': 'set', 'color': '#333333', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label'}, 'show': True
        },
        'text1': {
            'id': 'Text for Set 1', 'show': True, 'font_size': 16, 'color': '#FF0000', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'text2': {
            'id': 'Text for Set 2', 'show': True, 'font_size': 16, 'color': '#00B0F0', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                  'color': '#252525'}
    },
    'figure_4': {
        'id': 'figure_4', 'name': 'K-Cl-Ar 1', 'type': 'isochron', 'attr_name': 'KClAr1IsochronPlot',
        'rightside_text': [],
        'title': {'id': 'title', 'show': True, 'text': '', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text',
                  'font_weight': 'bolder', 'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': '{sup|39}Ar{sub|K} / {sup|38}Ar{sub|Cl}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': '{sup|40}Ar{sup|*} / {sup|38}Ar{sub|Cl}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'ellipse': {
            'id': 'ellipse', 'color': 'none', 'border_color': '#333333', 'border_type': 'solid',
            'show': False, 'fill': False,
            'border_width': 1, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
        },
        'set1': {
            'id': 'Points Set 1', 'color': '#FF0000', 'border_color': '#FF0000', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set2': {
            'id': 'Points Set 2', 'color': '#00B0F0', 'border_color': '#00B0F0', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set3': {
            'id': 'Unselected Points', 'color': '#FFFFFF', 'border_color': '#222222', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'line1': {
            'id': 'Line for Set 1', 'type': 'set', 'color': '#FF0000', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'line2': {
            'id': 'Line for Set 2', 'type': 'set', 'color': '#00B0F0', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'errline': {
            'id': 'Error Lines', 'type': 'set', 'color': '#333333', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label'}, 'show': True
        },
        'text1': {
            'id': 'Text for Set 1', 'show': True, 'font_size': 16, 'color': '#FF0000', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'text2': {
            'id': 'Text for Set 2', 'show': True, 'font_size': 16, 'color': '#00B0F0', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                  'color': '#252525'}
    },
    'figure_5': {
        'id': 'figure_5', 'name': 'K-Cl-Ar 2', 'type': 'isochron', 'attr_name': 'KClAr2IsochronPlot',
        'rightside_text': [],
        'title': {'id': 'title', 'show': True, 'text': '', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text',
                  'font_weight': 'bolder', 'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': '{sup|39}Ar{sub|K} / {sup|40}Ar{sup|*}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': '{sup|38}Ar{sub|Cl} / {sup|40}Ar{sup|*}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'ellipse': {
            'id': 'ellipse', 'color': 'none', 'border_color': '#333333', 'border_type': 'solid',
            'show': False, 'fill': False,
            'border_width': 1, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
        },
        'set1': {
            'id': 'Points Set 1', 'color': '#FF0000', 'border_color': '#FF0000', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set2': {
            'id': 'Points Set 2', 'color': '#00B0F0', 'border_color': '#00B0F0', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set3': {
            'id': 'Unselected Points', 'color': '#FFFFFF', 'border_color': '#222222', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'line1': {
            'id': 'Line for Set 1', 'type': 'set', 'color': '#FF0000', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'line2': {
            'id': 'Line for Set 2', 'type': 'set', 'color': '#00B0F0', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'errline': {
            'id': 'Error Lines', 'type': 'set', 'color': '#333333', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label'}, 'show': True
        },
        'text1': {
            'id': 'Text for Set 1', 'show': True, 'font_size': 16, 'color': '#FF0000', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'text2': {
            'id': 'Text for Set 2', 'show': True, 'font_size': 16, 'color': '#00B0F0', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                  'color': '#252525'}
    },
    'figure_6': {
        'id': 'figure_6', 'name': 'K-Cl-Ar 3', 'type': 'isochron', 'attr_name': 'KClAr3IsochronPlot',
        'rightside_text': [],
        'title': {'id': 'title', 'show': True, 'text': '', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text',
                  'font_weight': 'bolder', 'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': '{sup|38}Ar{sub|Cl} / {sup|39}Ar{sub|K}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': '{sup|40}Ar{sup|*} / {sup|39}Ar{sub|K}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'ellipse': {
            'id': 'ellipse', 'color': 'none', 'border_color': '#333333', 'border_type': 'solid',
            'show': False, 'fill': False,
            'border_width': 1, 'opacity': 1, 'symbol_size': 0, 'symbol': 'none', 'type': 'set',
        },
        'set1': {
            'id': 'Points Set 1', 'color': '#FF0000', 'border_color': '#FF0000', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set2': {
            'id': 'Points Set 2', 'color': '#00B0F0', 'border_color': '#00B0F0', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set3': {
            'id': 'Unselected Points', 'color': '#FFFFFF', 'border_color': '#222222', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'line1': {
            'id': 'Line for Set 1', 'type': 'set', 'color': '#FF0000', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label'}
        },
        'line2': {
            'id': 'Line for Set 2', 'type': 'set', 'color': '#00B0F0', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label'}
        },
        'errline': {
            'id': 'Error Lines', 'type': 'set', 'color': '#333333', 'line_type': 'solid', 'line_width': 2,
            'label': {'show': False, 'type': 'label'}, 'show': True
        },
        'text1': {
            'id': 'Text for Set 1', 'show': True, 'font_size': 16, 'color': '#FF0000', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'text2': {
            'id': 'Text for Set 2', 'show': True, 'font_size': 16, 'color': '#00B0F0', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                  'color': '#252525'}
    },
    'figure_7': {
        'id': 'figure_7', 'name': '3D Isochron', 'type': 'isochron', 'attr_name': 'ThreeDIsochronPlot',
        'rightside_text': [],
        'title': {'id': 'title', 'show': True, 'text': '', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text',
                  'font_weight': 'bolder', 'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': '{sup|36}Ar{sub|a+Cl} / {sup|40}Ar{sub|a+r}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'zaxis': {
            'title': {'text': '{sup|39}Ar{sub|K} / {sup|40}Ar{sub|a+r}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': '{sup|38}Ar{sub|a+Cl} / {sup|40}Ar{sub|a+r}', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'set1': {
            'id': 'Points Set 1', 'color': '#FF0000', 'border_color': '#FF0000', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set2': {
            'id': 'Points Set 2', 'color': '#00B0F0', 'border_color': '#00B0F0', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'set3': {
            'id': 'Unselected Points', 'color': '#FFFFFF', 'border_color': '#222222', 'border_width': 2, 'type': 'set',
            'border_type': 'solid', 'opacity': 0.8, 'symbol_size': 10, 'symbol': 'circle',
            'label': {'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top', 'type': 'label'}
        },
        'text1': {
            'id': 'Text for Set 1', 'show': True, 'font_size': 16, 'color': '#FF0000', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'text2': {
            'id': 'Text for Set 2', 'show': True, 'font_size': 16, 'color': '#00B0F0', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif',
        },
        'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                  'color': '#252525'}
    },
    'figure_8': {
        'id': 'figure_8', 'name': 'Degas Pattern', 'type': 'plot', 'attr_name': 'DegasPatternPlot',
        'rightside_text': [],
        'title': {'id': 'title', 'show': True, 'text': '', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text',
                  'font_weight': 'bolder', 'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': 'Step', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': 'Argon isotopes (%)', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                  'color': '#252525'}
    },
    'figure_9': {
        'id': 'figure_9', 'name': 'Age Distribution', 'type': 'plot', 'attr_name': 'AgeDistributionPlot',
        'rightside_text': [],
        'title': {'id': 'title', 'show': True, 'text': '', 'position': 'center',
                  'font_size': 18, 'color': '#333333', 'opacity': 1, 'type': 'text',
                  'font_weight': 'bolder', 'font_family': 'Microsoft Sans Serif', },
        'xaxis': {
            'title': {'text': '{sup|40}Ar / {sup|39}Ar Age', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'yaxis': {
            'title': {'text': 'Count', 'type': 'text', }, 'type': 'axis',
            'min': 0, 'max': 100, 'show_splitline': False, 'ticks_inside': False, 'split_number': 5, 'interval': 10,
        },
        'set1': {
            'id': 'Histogram', 'color': '#FFFFFF', 'border_color': '#333333', 'border_width': 1,
            'border_type': 'dashed', 'opacity': 0.5, 'symbol_size': 10, 'type': 'set', 'index': 0,
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0],
                      'position': 'top', 'color': '#252525'}
        },
        'set2': {
            'id': 'KDE', 'color': '#FF0000', 'line_width': 2, 'line_type': 'solid', 'symbol': 'None', 'symbol_size': 0,
            'opacity': 1, 'type': 'set', 'index': 9, 'band_extend': False, 'band_maximize': False, 'band_points': 200,
            'auto_width': 'Scott',
            'label': {'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0],
                      'position': 'top', 'color': '#252525'}
        },
        'set3': {
            'id': 'Age Bar', 'color': '#252525', 'border_color': '#252525', 'border_width': 1, 'border_type': 'solid',
            'opacity': 1, 'symbol_size': 10, 'type': 'set', 'index': 5, 'vertical_align': 'spread', 'bar_height': 5,
            'bar_interval': 5,
            'label': {
                'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
                'color': '#252525',
            }
        },
        'text1': {
            'id': 'Text for Set 1', 'show': True, 'font_size': 16, 'color': '#FF0000', 'opacity': 1, 'type': 'text',
            'font_weight': 'bold', 'font_family': 'Microsoft Sans Serif', 'pos': [1500, 10],
        },
        'label': {
            'id': '', 'type': 'label', 'show': False, 'distance': 5, 'offset': [10, 0], 'position': 'top',
            'color': '#252525',
        }
    },
}

VERSION = '20231208'


class Sample:

    def __init__(self, **kwargs):
        self.Doi = ""
        self.help = ""
        self.RawData = RawData()
        self.Info = Info()

        self.SequenceName = []
        self.SequenceValue = []
        self.SequenceUnit = []

        self.NewIntercept = []
        self.NewBlank = []
        self.NewParam = []

        self.SampleIntercept = []
        self.BlankIntercept = []
        self.AnalysisDateTime = []

        self.BlankCorrected = []
        self.MassDiscrCorrected = []
        self.DecayCorrected = []
        self.InterferenceCorrected = []
        self.CorrectedValues = []
        self.DegasValues = []

        self.ApparentAgeValues = []
        self.IsochronValues = []
        self.TotalParam = []

        self.PublishValues = []

        self.SelectedSequence1 = []
        self.SelectedSequence2 = []
        self.UnselectedSequence = []
        self.IsochronMark = []

        # Tables and Plots
        self.UnknownTable = Table()
        self.BlankTable = Table()
        self.CorrectedTable = Table()
        self.DegasPatternTable = Table()
        self.PublishTable = Table()
        self.AgeSpectraTable = Table()
        self.IsochronsTable = Table()
        self.TotalParamsTable = Table()
        self.AgeSpectraPlot = Plot()
        self.NorIsochronPlot = Plot()
        self.InvIsochronPlot = Plot()
        self.KClAr1IsochronPlot = Plot()
        self.KClAr2IsochronPlot = Plot()
        self.KClAr3IsochronPlot = Plot()
        self.ThreeDIsochronPlot = Plot()
        self.CorrelationPlot = Plot()
        self.DegasPatternPlot = Plot()
        self.AgeDistributionPlot = Plot()

        # self.Components = {}

        # self.__version = '20230521'
        # self.__version = '20230709'  # add labels to isochron plots
        # self.__version = '20230724'  # change header
        # self.__version = '20230730'  # delete calcparams attribute
        # self.__version = '20230827'  # using merge smp to update arr version
        self.__version = '20231116'  # change smp parameters

    @property
    def version(self):
        return self.__version

    def name(self): ...

    def doi(self): ...

    def sample(self): ...

    def researcher(self): ...

    def laboratory(self): ...

    def results(self): ...

    def sequence(self): ...

    def recalculate(self, *args): ...

    def plot_age_plateau(self): ...

    def plot_isochron(self): ...

    def plot_normal(self): ...

    def plot_inverse(self): ...

    def plot_cl_1(self): ...

    def plot_cl_2(self): ...

    def plot_cl_3(self): ...

    def plot_3D(self): ...

    def initial(self): ...

    def set_selection(self): ...

    def update_table(self): ...

    def unknown(self): ...

    def blank(self): ...

    def parameters(self): ...

    def corrected(self): ...

    def degas(self): ...

    def isochron(self): ...

    def apparent_ages(self): ...

    def publish(self): ...

    def corr_blank(self): ...

    def corr_massdiscr(self): ...

    def corr_decay(self): ...

    def corr_ca(self): ...

    def corr_k(self): ...

    def corr_cl(self): ...

    def corr_atm(self): ...

    def corr_r(self): ...

    def calc_ratio(self): ...

    def show_data(self): ...

    def set_params(self, params: Union[List, str], flag: Optional[str] = None): ...

    def set_info(self, info: dict): ...


class Table:
    def __init__(self, id='', name='Table', colcount=None, rowcount=None, header=None,
                 data=None, coltypes=None, textindexs=None, numericindexs=None, **kwargs):
        if header is None:
            header = ['']
        if data is None:
            data = [['']]
        if colcount is None:
            colcount = len(header)
        if rowcount is None:
            rowcount = len(data[0])
        if coltypes is None:
            coltypes = [{'type': 'numeric'}] * colcount
        self.id = id
        self.name = name
        self.colcount = colcount
        self.rowcount = rowcount
        self.header = header
        self.data = data
        self.coltypes = coltypes
        self.numericindexs = numericindexs
        self.textindexs = textindexs
        if textindexs is not None and numericindexs is not None:
            for i in textindexs:
                if i < self.colcount:
                    self.coltypes[i].update({'type': 'text'})
            for i in numericindexs:
                if i < self.colcount:
                    self.coltypes[i].update({'type': 'numeric'})
        for k, v in kwargs.items():
            setattr(self, k, v)


class Plot:
    def __init__(self, id='', type='', name='', data=None, info=None, **kwargs):
        if data is None:
            data = []
        self.id = id
        self.data = data
        self.info = info
        self.type = type
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

    class BasicAttr:
        def __init__(self, enabled=True, id='', type='', info=None, ):
            self.enabled = enabled
            self.id = id
            self.type = type
            self.info = info

        def show(self):
            self.enabled = True
            return self

        def hidden(self):
            self.enabled = False
            return self

    class Axis(BasicAttr):
        def __init__(self, id='', title=None, min=0, max=100, show_splitline=False,
                     **kwargs):
            super().__init__(id=id, type='Axis')
            self.title = title
            self.min = min
            self.max = max
            self.show_splitline = show_splitline
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Text(BasicAttr):
        def __init__(self, id='', text='', show=True, color=None, font_size=8,
                     font_family=None, font_weight=None,  # bold, normal
                     pos=None, **kwargs):
            super().__init__(id=id, type='Text')
            if pos is None:
                pos = [0, 0]
            self.text = text
            self.show = show
            self.color = color
            self.font_family = font_family
            self.font_size = font_size
            self.font_weight = font_weight
            self.pos = pos
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Label(BasicAttr):
        def __init__(self, id='', show=False, color=None, position=None, distance=None,
                     offset=None, **kwargs):
            super().__init__(id=id, type='Label')
            if offset is None:
                offset = [10, 0]
            self.show = show
            self.color = color
            self.position = position
            self.offset = offset
            self.distance = distance
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Set(BasicAttr):
        def __init__(self, id='', label=None, info=None, color=None, border_color=None,
                     border_width=None, line_width=None, line_type=None, opacity=None,
                     index=None, data=None, symbol_size=None, **kwargs):
            super().__init__(id=id, type='Set', info=info)
            if data is None:
                data = []
            self.label = label
            self.color = color
            self.border_color = border_color
            self.border_width = border_width
            self.line_width = line_width
            self.line_type = line_type
            self.opacity = opacity
            self.index = index
            self.data = data
            self.symbol_size = symbol_size
            for k, v in kwargs.items():
                setattr(self, k, v)


class Info:
    def __init__(self, id='', name='', type='Info', **kwargs):
        self.id = id
        self.name = name
        self.type = type
        for k, v in kwargs.items():
            setattr(self, k, v)


class Sequence:
    def __init__(self, index=None, data=None, flag=None, name=None, datetime=None,
                 type_str=None, results=None, coefficients=None, fitting_method=None,
                 is_estimated=False, **kwargs):
        self.index = index
        if name is None:
            name = ""
        if ' ' in name:
            name = name.replace(" ", '')
        self.name = name
        self.datetime = datetime
        self.data = data
        # flag is to check if the data point is selected
        if flag is None and data is not None:
            flag = [[j if i == 0 else True for i, j in enumerate(_m)] for _m in data]
        self.flag = flag
        self.type_str = type_str
        if results is None:
            results = []
        if fitting_method is None:
            fitting_method = []
        if coefficients is None:
            coefficients = []
        self.results = results
        self.coefficients = coefficients
        self.fitting_method = fitting_method
        self.is_estimated = is_estimated

        for k, v in kwargs.items():
            if hasattr(self, k) and type(getattr(self, k)) is MethodType:
                continue
            setattr(self, k, v)

        self.__as_type(self.type_str)

    def as_type(self, type_str):
        if str(type_str).lower() in ["blk", "b", "blank"]:
            self.type_str = "blank"
        if str(type_str).lower() in ["a", "air"]:
            self.type_str = "air"
        if self.type_str not in ["blank", "air"]:
            self.type_str = "unknown"

    __as_type = as_type

    def is_blank(self):
        return self.type_str == "blank"

    def is_unknown(self):
        return self.type_str != "blank" and self.type_str != "air"

    def is_air(self):
        return self.type_str == "air"

    def as_blank(self):
        return self.as_type("blank")

    def as_unknown(self):
        return self.as_type("unknown")

    def as_air(self):
        return self.as_type("air")

    def get_data_df(self):
        ...

    def get_flag_df(self):
        ...


class RawData:
    def __init__(self, id='', name='', type='raw', data=None, sequence_num=0,
                 isotopic_num=10, source=None, sequence=None, **kwargs):
        """
        Parameters
        ----------
        id
        name : file name
        type : raw
        data :
            list or data frame. [[x_ar36, y_ar36, x_ar37, y_ar37, ...], [ ... ]
        kwargs
        """

        self.id = id
        self.name = name
        self.type = type
        self.source = source
        self.isotopic_num = isotopic_num
        self.sequence_num = sequence_num
        self.interpolated_blank = None
        if data is not None:
            self.sequence: List[Sequence] = [
                Sequence(index=index, name=f"{self.name}-{index}", data=item[1:],
                         datetime=self.__get_experiment_time(item[0][1]),
                         type_str=item[0][2], fitting_method=[0] * 5)
                for index, item in enumerate(data)]
        else:
            self.sequence: List[Sequence] = []
        if sequence is not None:
            self.sequence = sequence
        for k, v in kwargs.items():
            if hasattr(self, k) and type(getattr(self, k)) is MethodType:
                continue

    def __get_experiment_time(self, time_str):
        k1 = time_str.split(' ')
        [month, day, year] = k1[0].split('/')
        [hour, min, second] = k1[2].split(':')
        if 'pm' in time_str.lower() and int(hour) < 12:
            hour = int(hour) + 12
        if 'am' in time_str.lower() and int(hour) >= 12:
            hour = int(hour) - 12
        return f'{year}-{month}-{day}T{hour}:{min}:{second}'

    def set_flag(self, sequence_index: int, isotopic_index: int, data: List[List[float]]):
        ...

    def get_flag(self, sequence_index: Optional[int], isotopic_index: Optional[int]) -> List[List[float]]:
        ...

    def get_result(self, sequence_index: Optional[int], isotopic_index: Optional[int],
                   method_index: Optional[List[List[Union[int, str]]]]) -> List[List[float]]:
        ...

    def do_regression(self, sequence_index: Optional[List], isotopic_index: Optional[List]):
        ...

    def get_data_df(self):
        ...

    def get_sequence(self, index: Optional[Union[list, int, str, bool]], flag: Optional[str],
                     unique: Optional[bool] = True) -> Union[Sequence, List]:
        ...

    def get_unknown(self) -> Union[Sequence, List]:
        ...

    def get_blank(self) -> Union[Sequence, List]:
        ...

    def get_air(self) -> Union[Sequence, List]:
        ...

    def to_sample(self, mapping: Optional[List[dict]]) -> Sample:
        ...

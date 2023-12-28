#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ==========================================
# Copyright 2023 Yang
# webarar - export
# ==========================================
#
#
#

from re import findall
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.chartsheet import Chartsheet
import os
import sys
import pickle
import traceback

from ..calc import arr, isochron
from . import basic, sample, consts

Sample = sample.Sample
Plot = sample.Plot

try:
    from webarar.settings import SETTINGS_ROOT
except ModuleNotFoundError:
    SETTINGS_ROOT = ""


def to_excel(file_path: str):
    excel = WritingWorkbook(filepath=file_path)
    excel.get_xls()


class ExcelTemplate:
    def __init__(self, **kwargs):
        self.name = ""
        self.worksheets = {}
        self.save_path = ''
        for key, value in kwargs.items():
            setattr(self, key, value)

    def sheetnames(self):
        return self.worksheets.keys()

    def sheet(self):
        # sheet name, sheet property name, (col, row, name, arr cls property name), (), ...
        return self.worksheets.items()

    def save(self):
        with open(self.save_path, 'wb') as f:
            f.write(pickle.dumps(self))


class WritingWorkbook:
    def __init__(self, **kwargs):
        self.style = None
        self.filepath = None  #
        self.template = None
        self.template_filepath = None  #
        self.sample = None  #

        self.chartarea_color = '#FFFFFF'  # white = '#FFFFFF'
        self.plotarea_color = '#FFFFFF'  # yellow = '#FFE4B5'
        self.border_color = '#000000'  # black = '#000000'
        self.font_color = '#000000'  # black = '#000000'
        self.color_map = ['#d61a1a', '#0268bd', '#f3f0eb', '#ffffff']
        self.plot_border_width = 1.25
        self.font_name = 'Microsoft Sans Serif'
        self.title_font_size = 16
        self.axis_font_size = 14
        self.axis_font_bold = False
        self.axis_num_font_size = 10
        self.line_width = 1.25

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.template_filepath is not None:
            self.read_template()
        if self.style is None:
            self.style = {
                'font_size': 10, 'font_name': 'Microsoft Sans Serif', 'bold': False,
                'bg_color': '#FFFFFF',  # back ground
                'font_color': '#000000', 'align': 'left',
                'top': 1, 'left': 1, 'right': 1, 'bottom': 1  # border width
            }

    def read_template(self):
        # print(self.template_filepath)
        self.template = CustomUnpickler(open(self.template_filepath, 'rb')).load()

    def get_xls(self):
        # TypeError: NAN/INF not supported in write_number() without 'nan_inf_to_errors' Workbook() option
        xls = Workbook(self.filepath, {"nan_inf_to_errors": True})
        style = xls.add_format(self.style)

        sht_reference = xls.add_worksheet("Reference")  # Data used to plot
        sht_reference.hide_gridlines(2)  # 0 = show grids, 1 = hide print grid, else = hide print and screen grids
        start_row = 3
        reference_header = [
            "x1", "y1", "y2", "x2", "y1", "y2", "x3", "y1", "y2", "x[bar]", "y[bar]", None, None, None,  # age spectra
            "x[set1]", "y[set1]", "x[set2]", "y[set2]", "x[unselected]", "y[unselected]",
            "point1[set1]", "point2[set1]", "point1[set2]", "point2[set2]",
            "x[set1]", "y[set1]", "x[set2]", "y[set2]", "x[unselected]", "y[unselected]",
            "point1[set1]", "point2[set1]", "point1[set2]", "point2[set2]",
            "x[set1]", "y[set1]", "x[set2]", "y[set2]", "x[unselected]", "y[unselected]",
            "point1[set1]", "point2[set1]", "point1[set2]", "point2[set2]",
            "x[set1]", "y[set1]", "x[set2]", "y[set2]", "x[unselected]", "y[unselected]",
            "point1[set1]", "point2[set1]", "point1[set2]", "point2[set2]",
            "x[set1]", "y[set1]", "x[set2]", "y[set2]", "x[unselected]", "y[unselected]",
            "point1[set1]", "point2[set1]", "point1[set2]", "point2[set2]",
        ]
        # writing header
        sht_reference.write_row(row=start_row - 3, col=0, data=reference_header, cell_format=style)
        # Data for age spectra
        spectra_data = arr.transpose(self.sample.AgeSpectraPlot.data)
        spectra_set1_data = arr.transpose(self.sample.AgeSpectraPlot.set1.data) or [[]] * 3
        spectra_set2_data = arr.transpose(self.sample.AgeSpectraPlot.set2.data) or [[]] * 3
        sht_reference.write_column(f"A{start_row}", spectra_data[0], style)
        sht_reference.write_column(f"B{start_row}", spectra_data[1], style)
        sht_reference.write_column(f"C{start_row}", spectra_data[2], style)
        sht_reference.write_column(f"D{start_row}", spectra_set1_data[0], style)
        sht_reference.write_column(f"E{start_row}", spectra_set1_data[1], style)
        sht_reference.write_column(f"F{start_row}", spectra_set1_data[2], style)
        sht_reference.write_column(f"G{start_row}", spectra_set2_data[0], style)
        sht_reference.write_column(f"H{start_row}", spectra_set2_data[1], style)
        sht_reference.write_column(f"I{start_row}", spectra_set2_data[2], style)
        sht_reference.write_column(f"J{start_row}", [], style)
        sht_reference.write_column(f"K{start_row}", [], style)
        # Data for normal isochron
        set_data = [set1_data, set2_data, set3_data] = isochron.get_set_data(
            self.sample.NorIsochronPlot.data, self.sample.SelectedSequence1, self.sample.SelectedSequence2,
            self.sample.UnselectedSequence)
        sht_reference.write_column(f"O{start_row}", set1_data[0], style)
        sht_reference.write_column(f"P{start_row}", set1_data[2], style)
        sht_reference.write_column(f"Q{start_row}", set2_data[0], style)
        sht_reference.write_column(f"R{start_row}", set2_data[2], style)
        sht_reference.write_column(f"S{start_row}", set3_data[0], style)
        sht_reference.write_column(f"T{start_row}", set3_data[2], style)
        sht_reference.write_column(f"U{start_row}", self.sample.NorIsochronPlot.line1.data[0], style)
        sht_reference.write_column(f"V{start_row}", self.sample.NorIsochronPlot.line1.data[1], style)
        sht_reference.write_column(f"W{start_row}", self.sample.NorIsochronPlot.line2.data[0], style)
        sht_reference.write_column(f"X{start_row}", self.sample.NorIsochronPlot.line2.data[1], style)
        # Data for inverse isochron
        set_data = [set1_data, set2_data, set3_data] = isochron.get_set_data(
            self.sample.InvIsochronPlot.data, self.sample.SelectedSequence1, self.sample.SelectedSequence2,
            self.sample.UnselectedSequence)
        sht_reference.write_column(f"Y{start_row}", set1_data[0], style)
        sht_reference.write_column(f"Z{start_row}", set1_data[2], style)
        sht_reference.write_column(f"AA{start_row}", set2_data[0], style)
        sht_reference.write_column(f"AB{start_row}", set2_data[2], style)
        sht_reference.write_column(f"AC{start_row}", set3_data[0], style)
        sht_reference.write_column(f"AD{start_row}", set3_data[2], style)
        sht_reference.write_column(f"AE{start_row}", self.sample.InvIsochronPlot.line1.data[0], style)
        sht_reference.write_column(f"AF{start_row}", self.sample.InvIsochronPlot.line1.data[1], style)
        sht_reference.write_column(f"AG{start_row}", self.sample.InvIsochronPlot.line2.data[0], style)
        sht_reference.write_column(f"AH{start_row}", self.sample.InvIsochronPlot.line2.data[1], style)
        # Data for Cl 1 isochron
        set_data = [set1_data, set2_data, set3_data] = isochron.get_set_data(
            self.sample.KClAr1IsochronPlot.data, self.sample.SelectedSequence1, self.sample.SelectedSequence2,
            self.sample.UnselectedSequence)
        sht_reference.write_column(f"AI{start_row}", set1_data[0], style)
        sht_reference.write_column(f"AJ{start_row}", set1_data[2], style)
        sht_reference.write_column(f"AK{start_row}", set2_data[0], style)
        sht_reference.write_column(f"AL{start_row}", set2_data[2], style)
        sht_reference.write_column(f"AM{start_row}", set3_data[0], style)
        sht_reference.write_column(f"AN{start_row}", set3_data[2], style)
        sht_reference.write_column(f"AO{start_row}", self.sample.KClAr1IsochronPlot.line1.data[0], style)
        sht_reference.write_column(f"AP{start_row}", self.sample.KClAr1IsochronPlot.line1.data[1], style)
        sht_reference.write_column(f"AQ{start_row}", self.sample.KClAr1IsochronPlot.line2.data[0], style)
        sht_reference.write_column(f"AR{start_row}", self.sample.KClAr1IsochronPlot.line2.data[1], style)
        # Data for Cl 2 isochron
        set_data = [set1_data, set2_data, set3_data] = isochron.get_set_data(
            self.sample.KClAr2IsochronPlot.data, self.sample.SelectedSequence1, self.sample.SelectedSequence2,
            self.sample.UnselectedSequence)
        sht_reference.write_column(f"AS{start_row}", set1_data[0], style)
        sht_reference.write_column(f"AT{start_row}", set1_data[2], style)
        sht_reference.write_column(f"AU{start_row}", set2_data[0], style)
        sht_reference.write_column(f"AV{start_row}", set2_data[2], style)
        sht_reference.write_column(f"AW{start_row}", set3_data[0], style)
        sht_reference.write_column(f"AX{start_row}", set3_data[2], style)
        sht_reference.write_column(f"AY{start_row}", self.sample.KClAr2IsochronPlot.line1.data[0], style)
        sht_reference.write_column(f"AZ{start_row}", self.sample.KClAr2IsochronPlot.line1.data[1], style)
        sht_reference.write_column(f"BA{start_row}", self.sample.KClAr2IsochronPlot.line2.data[0], style)
        sht_reference.write_column(f"BB{start_row}", self.sample.KClAr2IsochronPlot.line2.data[1], style)
        # Data for Cl 3 isochron
        set_data = [set1_data, set2_data, set3_data] = isochron.get_set_data(
            self.sample.KClAr3IsochronPlot.data, self.sample.SelectedSequence1, self.sample.SelectedSequence2,
            self.sample.UnselectedSequence)
        sht_reference.write_column(f"BC{start_row}", set1_data[0], style)
        sht_reference.write_column(f"BD{start_row}", set1_data[2], style)
        sht_reference.write_column(f"BE{start_row}", set2_data[0], style)
        sht_reference.write_column(f"BF{start_row}", set2_data[2], style)
        sht_reference.write_column(f"BG{start_row}", set3_data[0], style)
        sht_reference.write_column(f"BH{start_row}", set3_data[2], style)
        sht_reference.write_column(f"BI{start_row}", self.sample.KClAr3IsochronPlot.line1.data[0], style)
        sht_reference.write_column(f"BJ{start_row}", self.sample.KClAr3IsochronPlot.line1.data[1], style)
        sht_reference.write_column(f"BK{start_row}", self.sample.KClAr3IsochronPlot.line2.data[0], style)
        sht_reference.write_column(f"BL{start_row}", self.sample.KClAr3IsochronPlot.line2.data[1], style)
        # Data for degas pattern
        degas_data = self.sample.DegasPatternPlot.data
        sht_reference.write_column(f"BM{start_row}", degas_data[0], style)
        sht_reference.write_column(f"BN{start_row}", degas_data[1], style)
        sht_reference.write_column(f"BO{start_row}", degas_data[2], style)
        sht_reference.write_column(f"BP{start_row}", degas_data[3], style)
        sht_reference.write_column(f"BQ{start_row}", degas_data[4], style)
        sht_reference.write_column(f"BR{start_row}", degas_data[5], style)
        sht_reference.write_column(f"BS{start_row}", degas_data[6], style)
        sht_reference.write_column(f"BT{start_row}", degas_data[7], style)
        sht_reference.write_column(f"BU{start_row}", degas_data[8], style)
        sht_reference.write_column(f"BV{start_row}", degas_data[9], style)
        sht_reference.write_column(f"BW{start_row}", [i+1 for i in range(len(self.sample.SequenceName))], style)

        sht_result = xls.add_worksheet('Results')
        title_style = xls.add_format({
            'font_size': 10, 'font_name': 'Microsoft Sans Serif', 'bold': True,
            'bg_color': '#ccffff', 'font_color': '#0000ff', 'align': 'vcenter',
            'top': 2, 'bottom': 2  # border width
        })
        title_style_2 = xls.add_format({
            'font_size': 10, 'font_name': 'Microsoft Sans Serif', 'bold': True,
            'font_color': '#000000', 'align': 'vcenter', 'top': 0, 'left': 0, 'bottom': 0, 'right': 0  # border width
        })
        data_style = xls.add_format({
            'font_size': 10, 'font_name': 'Microsoft Sans Serif', 'bold': False,
            'font_color': '#000000', 'align': 'vcenter',
            'top': 0, 'left': 0, 'bottom': 0, 'right': 0  # border width
        })
        data_style.set_align('left')
        data_style.set_text_wrap()
        sht_result.set_column(0, 21, width=8.5)  # column width
        sht_result.set_column(10, 11, width=3)  # column width
        sht_result.merge_range(0, 0, 1, 9, 'Sample Information', title_style)
        title_list = [
            [7, 0, 8, 0, 'Result'], [7, 1, 8, 1, ''], [7, 2, 8, 2, '40(r)/39(k)'], [7, 3, 8, 3, '1σ'],
            [7, 4, 8, 4, 'Age'], [7, 5, 8, 5, '1σ'],
            [7, 6, 8, 6, 'MSWD'], [7, 7, 8, 7, '39Ar(K)'], [7, 8, 8, 8, 'Ca/K'], [7, 9, 8, 9, '1σ'],
            [7, 12, 8, 12, 'Result'], [7, 13, 8, 13, ''], [7, 14, 8, 14, '40(r)/39(k)'], [7, 15, 8, 15, '1σ'],
            [7, 16, 8, 16, 'Age'], [7, 17, 8, 17, '1σ'],
            [7, 18, 8, 18, 'MSWD'], [7, 19, 8, 19, '39Ar(K)'], [7, 20, 8, 20, 'Ca/K'], [7, 21, 8, 21, '1σ'],
        ]
        data_list = [
            [3, 0, 3, 2, f"Sample = {self.sample.Info.sample.name}"],
            [3, 3, 3, 5, f"Material = {self.sample.Info.sample.material}"],
            [3, 6, 3, 8, f"Irradiation = {self.sample.TotalParam[28][0]}"],
            [4, 0, 4, 2, f"Analyst = {self.sample.Info.laboratory.analyst}"],
            [4, 3, 4, 5, f"Researcher = {self.sample.Info.researcher.name}"],
            [4, 6, 4, 8,
             f"J = {self.sample.TotalParam[67][0]} ± {round(self.sample.TotalParam[68][0] * self.sample.TotalParam[67][0] / 100, len(str(self.sample.TotalParam[67][0])))}"],
        ]
        for each in title_list:
            sht_result.merge_range(*each, title_style)
        for each in data_list:
            sht_result.merge_range(*each, data_style)

        def _write_results(sht: Worksheet, start_row: int, start_col: int, title: str, data: list):
            if len(data) < 11:
                return
            sht.merge_range(start_row, start_col, start_row + 1, start_col + 1, title, title_style_2)
            sht.merge_range(start_row, start_col + 2, start_row + 1, start_col + 2, data[0], data_style)
            sht.write_column(start_row, start_col + 3, data[1:3], data_style)
            sht.merge_range(start_row, start_col + 4, start_row + 1, start_col + 4, data[3], data_style)
            sht.write_column(start_row, start_col + 5, data[4:6], data_style)
            sht.merge_range(start_row, start_col + 6, start_row + 1, start_col + 6, data[6], data_style)
            sht.write_column(start_row, start_col + 7, data[7:9], data_style)
            sht.merge_range(start_row, start_col + 8, start_row + 1, start_col + 8, data[9], data_style)
            sht.write_column(start_row, start_col + 9, data[9:11], data_style)

        try:
            _write_results(sht_result, 10, 0, 'Total Age', [
                *self.sample.AgeSpectraPlot.info[0:2], '', self.sample.AgeSpectraPlot.info[4],
                self.sample.AgeSpectraPlot.info[6], '',
                '', 1, len(self.sample.SequenceName), '', '', ''])
            _write_results(sht_result, 10, 12, 'Total Age', [
                *self.sample.AgeSpectraPlot.info[0:2], '', self.sample.AgeSpectraPlot.info[4],
                self.sample.AgeSpectraPlot.info[6], '',
                '', 1, len(self.sample.SequenceName), '', '', ''])
        except TypeError:
            pass
        try:
            _write_results(sht_result, 17, 0, 'Set 1 Age Plateau', [
                *self.sample.AgeSpectraPlot.set1.info[0:2], '',
                self.sample.AgeSpectraPlot.set1.info[4], self.sample.AgeSpectraPlot.set1.info[6], '',
                self.sample.AgeSpectraPlot.set1.info[3], '', self.sample.AgeSpectraPlot.set1.info[2],
                '', '', ''
            ])
        except (IndexError, TypeError):
            pass
        try:
            _write_results(sht_result, 17, 12, 'Set 2 Age Plateau', [
                *self.sample.AgeSpectraPlot.set2.info[0:2], '',
                self.sample.AgeSpectraPlot.set2.info[4], self.sample.AgeSpectraPlot.set2.info[6], '',
                self.sample.AgeSpectraPlot.set2.info[2], '', self.sample.AgeSpectraPlot.set2.info[3],
                '', '', ''
            ])
        except (IndexError, TypeError):
            pass
        for row_index, figure in enumerate(['figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6']):
            for col_index, set in enumerate(['set1', 'set2']):
                try:
                    _isochron_results = getattr(basic.get_component_byid(self.sample, figure), set)
                    _name = \
                    ['Normal Ioschron', 'Inverse Isochron', 'K-Cl-Ar Plot 1', 'K-Cl-Ar Plot 2', 'K-Cl-Ar Plot 3'][
                        row_index]
                    _write_results(sht_result, 24 + row_index * 7, 0 + col_index * 12,
                                   f'{["Set 1", "Set 2"][col_index]} {_name}', [
                                       *_isochron_results.info[2], '',
                                       _isochron_results.info[3][0], _isochron_results.info[3][2], '',
                                       _isochron_results.info[0][4], '',
                                       len([self.sample.SelectedSequence1, self.sample.SelectedSequence2][col_index]),
                                       '', '', ''
                                   ])
                except (IndexError, TypeError):
                    continue

        for sht_name, [prop_name, sht_type, row, col, _, smp_attr_name, header_name] in self.template.sheet():
            if sht_type == "table":
                data = arr.transpose(getattr(self.sample, smp_attr_name, None).data)
                sht = xls.add_worksheet(sht_name)
                sht.hide_gridlines(2)  # 0 = show grids, 1 = hide print grid, else = hide print and screen grids
                sht.hide()  # default hidden table sheet
                sht.set_column(0, len(data), width=12)  # column width
                header = getattr(samples, header_name)
                sht.write_row(row=row - 1, col=col, data=header, cell_format=style)
                for each_col in data:
                    res = sht.write_column(row=row, col=col, data=each_col, cell_format=style)
                    if res:
                        xls.close()
                        return None
                    col += 1
            elif sht_type == "chart":
                sht = xls.add_chartsheet(sht_name)
                sht.set_paper(1)  # US letter = 1, A4 = 9, letter is more rectangular
                num_unselected = len(self.sample.UnselectedSequence)
                num_set1 = len(self.sample.SelectedSequence1)
                num_set2 = len(self.sample.SelectedSequence2)
                if "spectra" in prop_name.lower():
                    figure = self.sample.AgeSpectraPlot
                    data_area = [
                        # Spectra lines
                        f"A{start_row}:A{len(spectra_data[0]) + start_row - 1}",
                        f"B{start_row}:B{len(spectra_data[0]) + start_row - 1}",
                        f"C{start_row}:C{len(spectra_data[0]) + start_row - 1}",
                        # set 1
                        f"D{start_row}:D{len(spectra_data[0]) + start_row - 1}",
                        f"E{start_row}:E{len(spectra_data[0]) + start_row - 1}",
                        f"F{start_row}:F{len(spectra_data[0]) + start_row - 1}",
                        # set 2
                        f"G{start_row}:G{len(spectra_data[0]) + start_row - 1}",
                        f"H{start_row}:H{len(spectra_data[0]) + start_row - 1}",
                        f"I{start_row}:I{len(spectra_data[0]) + start_row - 1}",
                    ]
                    axis_range = [figure.xaxis.min, figure.xaxis.max, figure.yaxis.min, figure.yaxis.max]
                    self.get_chart_age_spectra(xls, sht, data_area, axis_range)
                elif "normal_isochron" in prop_name.lower():
                    data_area = [
                        f"O{start_row}:O{num_set1 + start_row - 1}", f"P{start_row}:P{num_set1 + start_row - 1}",
                        f"Q{start_row}:Q{num_set2 + start_row - 1}", f"R{start_row}:R{num_set2 + start_row - 1}",
                        f"S{start_row}:S{num_unselected + start_row - 1}",
                        f"T{start_row}:T{num_unselected + start_row - 1}",
                        f"U{start_row}:V{start_row}", f"U{start_row + 1}:V{start_row + 1}",
                        f"W{start_row}:X{start_row}", f"W{start_row + 1}:X{start_row + 1}",
                    ]
                    axis_range = [
                        basic.get_component_byid(self.sample, 'figure_2').xaxis.min,
                        basic.get_component_byid(self.sample, 'figure_2').xaxis.max,
                        basic.get_component_byid(self.sample, 'figure_2').yaxis.min,
                        basic.get_component_byid(self.sample, 'figure_2').yaxis.max,
                    ]
                    self.get_chart_isochron(
                        xls, sht, data_area, axis_range, title_name="Normal Isochron",
                        x_axis_name=f"{consts.sup_39}Ar / {consts.sup_36}Ar",
                        y_axis_name=f"{consts.sup_40}Ar / {consts.sup_36}Ar")
                elif "inverse_isochron" in prop_name.lower():
                    data_area = [
                        f"Y{start_row}:Y{num_set1 + start_row - 1}", f"Z{start_row}:Z{num_set1 + start_row - 1}",
                        f"AA{start_row}:AA{num_set2 + start_row - 1}", f"AB{start_row}:AB{num_set2 + start_row - 1}",
                        f"AC{start_row}:AC{num_unselected + start_row - 1}",
                        f"AD{start_row}:AD{num_unselected + start_row - 1}",
                        f"AE{start_row}:AF{start_row}", f"AE{start_row + 1}:AF{start_row + 1}",
                        f"AG{start_row}:AH{start_row}", f"AG{start_row + 1}:AH{start_row + 1}",
                    ]
                    axis_range = [
                        basic.get_component_byid(self.sample, 'figure_3').xaxis.min,
                        basic.get_component_byid(self.sample, 'figure_3').xaxis.max,
                        basic.get_component_byid(self.sample, 'figure_3').yaxis.min,
                        basic.get_component_byid(self.sample, 'figure_3').yaxis.max,
                    ]
                    self.get_chart_isochron(
                        xls, sht, data_area, axis_range, title_name="Inverse Isochron",
                        x_axis_name=f"{consts.sup_39}Ar / {consts.sup_40}Ar",
                        y_axis_name=f"{consts.sup_36}Ar / {consts.sup_40}Ar")
                elif "k-cl-ar_1_isochron" in prop_name.lower():
                    data_area = [
                        f"AI{start_row}:AI{num_set1 + start_row - 1}", f"AJ{start_row}:AJ{num_set1 + start_row - 1}",
                        f"AK{start_row}:AK{num_set2 + start_row - 1}", f"AL{start_row}:AL{num_set2 + start_row - 1}",
                        f"AM{start_row}:AM{num_unselected + start_row - 1}",
                        f"AN{start_row}:AN{num_unselected + start_row - 1}",
                        f"AO{start_row}:AP{start_row}", f"AO{start_row + 1}:AP{start_row + 1}",
                        f"AQ{start_row}:AR{start_row}", f"AQ{start_row + 1}:AR{start_row + 1}",
                    ]
                    axis_range = [
                        basic.get_component_byid(self.sample, 'figure_4').xaxis.min,
                        basic.get_component_byid(self.sample, 'figure_4').xaxis.max,
                        basic.get_component_byid(self.sample, 'figure_4').yaxis.min,
                        basic.get_component_byid(self.sample, 'figure_4').yaxis.max,
                    ]
                    self.get_chart_isochron(
                        xls, sht, data_area, axis_range, title_name="K-Cl-Ar 1 Isochron",
                        x_axis_name=f"{consts.sup_39}Ar / {consts.sup_38}Ar",
                        y_axis_name=f"{consts.sup_40}Ar / {consts.sup_38}Ar")
                elif "k-cl-ar_2_isochron" in prop_name.lower():
                    data_area = [
                        f"AS{start_row}:AS{num_set1 + start_row - 1}", f"AT{start_row}:AT{num_set1 + start_row - 1}",
                        f"AU{start_row}:AU{num_set2 + start_row - 1}", f"AV{start_row}:AV{num_set2 + start_row - 1}",
                        f"AW{start_row}:AW{num_unselected + start_row - 1}",
                        f"AX{start_row}:AX{num_unselected + start_row - 1}",
                        f"AY{start_row}:AZ{start_row}", f"AY{start_row + 1}:AZ{start_row + 1}",
                        f"BA{start_row}:BB{start_row}", f"BA{start_row + 1}:BB{start_row + 1}",
                    ]
                    axis_range = [
                        basic.get_component_byid(self.sample, 'figure_5').xaxis.min,
                        basic.get_component_byid(self.sample, 'figure_5').xaxis.max,
                        basic.get_component_byid(self.sample, 'figure_5').yaxis.min,
                        basic.get_component_byid(self.sample, 'figure_5').yaxis.max,
                    ]
                    self.get_chart_isochron(
                        xls, sht, data_area, axis_range, title_name="K-Cl-Ar 2 Isochron",
                        x_axis_name=f"{consts.sup_39}Ar / {consts.sup_40}Ar",
                        y_axis_name=f"{consts.sup_38}Ar / {consts.sup_40}Ar")
                elif "k-cl-ar_3_isochron" in prop_name.lower():
                    data_area = [
                        f"BC{start_row}:BC{num_set1 + start_row - 1}", f"BD{start_row}:BD{num_set1 + start_row - 1}",
                        f"BE{start_row}:BE{num_set2 + start_row - 1}", f"BF{start_row}:BF{num_set2 + start_row - 1}",
                        f"BG{start_row}:BG{num_unselected + start_row - 1}",
                        f"BH{start_row}:BH{num_unselected + start_row - 1}",
                        f"BI{start_row}:BJ{start_row}", f"BI{start_row + 1}:BJ{start_row + 1}",
                        f"BK{start_row}:BL{start_row}", f"BK{start_row + 1}:BL{start_row + 1}",
                    ]
                    axis_range = [
                        basic.get_component_byid(self.sample, 'figure_6').xaxis.min,
                        basic.get_component_byid(self.sample, 'figure_6').xaxis.max,
                        basic.get_component_byid(self.sample, 'figure_6').yaxis.min,
                        basic.get_component_byid(self.sample, 'figure_6').yaxis.max,
                    ]
                    self.get_chart_isochron(
                        xls, sht, data_area, axis_range, title_name="K-Cl-Ar 3 Isochron",
                        x_axis_name=f"{consts.sup_38}Ar / {consts.sup_39}Ar",
                        y_axis_name=f"{consts.sup_40}Ar / {consts.sup_39}Ar")
                elif "degas_pattern" in prop_name.lower():
                    data_area = [
                        f"BM{start_row}:BM{len(degas_data[0]) + start_row - 1}",
                        f"BN{start_row}:BN{len(degas_data[1]) + start_row - 1}",
                        f"BO{start_row}:BO{len(degas_data[2]) + start_row - 1}",
                        f"BP{start_row}:BP{len(degas_data[3]) + start_row - 1}",
                        f"BQ{start_row}:BQ{len(degas_data[4]) + start_row - 1}",
                        f"BR{start_row}:BR{len(degas_data[5]) + start_row - 1}",
                        f"BS{start_row}:BS{len(degas_data[6]) + start_row - 1}",
                        f"BT{start_row}:BT{len(degas_data[7]) + start_row - 1}",
                        f"BU{start_row}:BU{len(degas_data[8]) + start_row - 1}",
                        f"BV{start_row}:BV{len(degas_data[9]) + start_row - 1}",
                        f"BW{start_row}:BW{len(degas_data[9]) + start_row - 1}",
                    ]
                    axis_range = [
                        basic.get_component_byid(self.sample, 'figure_8').xaxis.min,
                        basic.get_component_byid(self.sample, 'figure_8').xaxis.max,
                        basic.get_component_byid(self.sample, 'figure_8').yaxis.min,
                        basic.get_component_byid(self.sample, 'figure_8').yaxis.max,
                    ]
                    self.get_chart_degas_pattern(
                        xls, sht, data_area, axis_range,
                        title_name="Degas Pattern", x_axis_name=f"Sequence",
                        y_axis_name=f"Argon Isotopes (%)")
            else:
                xls.close()
                return None
        xls.get_worksheet_by_name("Reference").hide()
        xls.get_worksheet_by_name("Isochrons").hidden = 0  # unhiden isochrons worksheet
        xls.get_worksheet_by_name("Publish").activate()
        xls.close()
        print('导出完毕，文件路径:%s' % self.filepath)
        return True

    def create_initial_chart(self, xls: Workbook, chart_type: str = 'scatter'):
        # chartarea
        chartarea_dict = {'border': {'none': True}, 'fill': {'color': self.chartarea_color}}
        # plotarea
        plotarea_dict = {
            'border': {'color': self.border_color, 'width': self.plot_border_width},
            'fill': {'color': self.plotarea_color}
        }
        # title, No title
        title_dict = {'none': True, 'name': '',
                      'name_font': {'name': self.font_name, 'size': self.title_font_size, 'color': self.font_color}}
        # axis
        axis_dict = {
            'name': 'Axis Name',  # axis name
            'name_font': {'name': self.font_name, 'size': self.axis_font_size, 'bold': self.axis_font_bold,
                          'color': self.font_color},
            # Setting number font
            'num_font': {'name': self.font_name, 'size': self.axis_num_font_size, 'color': self.font_color,
                         'italic': False},
            'major_gridlines': {'visible': False, 'line': {'width': 1.25, 'dash_type': 'dash'}},
            # Setting line (ticks) properties of chart axes
            'line': {'width': self.plot_border_width, 'color': self.border_color},
            'crossing': 'min',
        }
        # Not display legend
        legend_dict = {'none': True}

        chart = xls.add_chart({'type': chart_type})
        chart.set_chartarea(chartarea_dict)
        chart.set_plotarea(plotarea_dict)
        chart.set_title(title_dict)
        chart.set_x_axis(axis_dict)
        chart.set_y_axis(axis_dict)
        chart.set_legend(legend_dict)

        return chart

    def get_chart_age_spectra(self, xls: Workbook, sht: Chartsheet, data_area: list, axis_range: list):
        # ==============SpectraDiagram===============
        [xMin, xMax, yMin, yMax] = axis_range
        # Initializing a chart
        chart = self.create_initial_chart(xls, 'scatter')
        # Set data
        series = [
            {
                'name': 'Line 1-1',
                'categories': f'Reference!{data_area[0]}',
                'values': f'Reference!{data_area[1]}',
                'line': {'color': self.border_color, 'width': self.line_width},
                'marker': {'type': 'none'},
            },
            {
                'name': 'Line 1-2',
                'categories': f'Reference!{data_area[0]}',
                'values': f'Reference!{data_area[2]}',
                'line': {'color': self.border_color, 'width': self.line_width},
                'marker': {'type': 'none'},
            },
            {
                'name': 'Line 2-1',
                'categories': f'Reference!{data_area[3]}',
                'values': f'Reference!{data_area[4]}',
                'line': {'color': self.color_map[0], 'width': self.line_width},
                'marker': {'type': 'none'},
            },
            {
                'name': 'Line 2-2',
                'categories': f'Reference!{data_area[3]}',
                'values': f'Reference!{data_area[5]}',
                'line': {'color': self.color_map[0], 'width': self.line_width},
                'marker': {'type': 'none'},
            },
            {
                'name': 'Line 3-1',
                'categories': f'Reference!{data_area[6]}',
                'values': f'Reference!{data_area[7]}',
                'line': {'color': self.color_map[1], 'width': self.line_width},
                'marker': {'type': 'none'},
            },
            {
                'name': 'Line 3-2',
                'categories': f'Reference!{data_area[6]}',
                'values': f'Reference!{data_area[8]}',
                'line': {'color': self.color_map[1], 'width': self.line_width},
                'marker': {'type': 'none'},
            },
        ]
        for each in series:
            chart.add_series(each)
        # Title
        # chart.title_name = 'Age Spectra'
        # Axis title
        chart.x_axis.update({'name': f'Cumulative {consts.sup_39}Ar released (%)', 'min': xMin, 'max': xMax})
        chart.y_axis.update({'name': 'Apparent age (Ma)', 'min': yMin, 'max': yMax})
        sht.set_chart(chart)

    def get_chart_isochron(self, xls: Workbook, sht: Chartsheet, data_areas, axis_range,
                           title_name="", x_axis_name="", y_axis_name=""):
        # Initializing a chart
        isochron = self.create_initial_chart(xls, 'scatter')
        series = [
            {
                'name': 'Set 1 Selected Points',
                'categories': f'Reference!{data_areas[0]}',
                'values': f'Reference!{data_areas[1]}',
                'line': {'none': True},
                'marker': {
                    'type': 'square', 'size': 6,
                    'border': {'color': self.border_color},
                    'fill': {'color': self.color_map[0]}}
            },
            {
                'name': 'Set 2 Selected Points',
                'categories': f'Reference!{data_areas[2]}',
                'values': f'Reference!{data_areas[3]}',
                'line': {'none': True},
                'marker': {'type': 'square', 'size': 6,
                           'border': {'color': self.border_color},
                           'fill': {'color': self.color_map[1]}}
            },
            {
                'name': 'Unselected Points',
                'categories': f'Reference!{data_areas[4]}',
                'values': f'Reference!{data_areas[5]}',
                'line': {'none': True},
                'marker': {'type': 'square', 'size': 6,
                           'border': {'color': self.border_color},
                           'fill': {'color': self.color_map[2]}}
            },
            {
                'name': 'Line Set 1',
                'categories': f'Reference!{data_areas[6]}',
                'values': f'Reference!{data_areas[7]}',
                'line': {'color': self.color_map[0], 'width': self.line_width},
                'marker': {'type': 'none'}
            },
            {
                'name': 'Line Set 2',
                'categories': f'Reference!{data_areas[8]}',
                'values': f'Reference!{data_areas[9]}',
                'line': {'color': self.color_map[1], 'width': self.line_width},
                'marker': {'type': 'none'}
            }
        ]
        # isochron.title_name = title_name
        for each in series:
            isochron.add_series(each)
        isochron.x_axis.update({'name': x_axis_name, 'min': axis_range[0], 'max': axis_range[1]})
        isochron.y_axis.update({'name': y_axis_name, 'min': axis_range[2], 'max': axis_range[3]})
        sht.set_chart(isochron)

    def get_chart_degas_pattern(self, xls: Workbook, sht: Chartsheet, data_areas, axis_range,
                                title_name="", x_axis_name="", y_axis_name=""):
        # unicode for supscript numbers
        # series name
        series_name = [
            f'{consts.sup_36}Ara', f'{consts.sup_37}ArCa', f'{consts.sup_38}ArCl',
            f'{consts.sup_39}ArK', f'{consts.sup_40}Arr', f'{consts.sup_36}Ar',
            f'{consts.sup_37}Ar', f'{consts.sup_38}Ar', f'{consts.sup_39}Ar', f'{consts.sup_40}Ar',
        ]
        # Initializing a chart
        chart = self.create_initial_chart(xls, 'scatter')
        series = []
        for i in range(len(data_areas) - 1):
            series.append({
                'name': series_name[i],
                'categories': f'Reference!{data_areas[10]}',
                'values': f'Reference!{data_areas[i]}',
                'line': {'color': self.border_color, 'width': self.line_width},
                'marker': {
                    'type': 'square', 'size': 6,
                    'border': {'color': self.border_color},
                    # 'fill': {'color': self.color_map[0]},
                }
            })
        # chart.title_name = title_name
        for each in series:
            chart.add_series(each)
        # chart.x_axis.update({'name': x_axis_name, 'min': axis_range[0], 'max': axis_range[1]})
        # chart.y_axis.update({'name': y_axis_name, 'min': axis_range[2], 'max': axis_range[3]})

        chart.set_legend({'none': False, 'position': 'top'})

        sht.set_chart(chart)


class CreateOriginGraph:
    def __init__(self, **kwargs):
        self.name = "Origin"
        self.sample = Sample()
        self.export_filepath = ""
        self.spectra_data = [[]] * 3
        self.set1_spectra_data = [[]] * 3
        self.set2_spectra_data = [[]] * 3
        self.isochron_data = [[]] * 36
        self.isochron_lines_data = [[]] * 20
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_graphs(self):
        import originpro as op
        import OriginExt
        def origin_shutdown_exception_hook(exctype, value, traceback):
            """Ensures Origin gets shut down if an uncaught exception"""
            op.exit()
            sys.__excepthook__(exctype, value, traceback)

        if op and op.oext:
            sys.excepthook = origin_shutdown_exception_hook

        # Set Origin instance visibility.
        # Important for only external Python.
        # Should not be used with embedded Python.
        if op.oext:
            op.set_show(True)

        # Spectra lines
        linePoints = self.spectra_data if self.spectra_data != [] else [[]] * 3
        linePoints += self.set1_spectra_data if self.set1_spectra_data != [] else [[]] * 3
        linePoints += self.set2_spectra_data if self.set2_spectra_data != [] else [[]] * 3
        age_spectra_wks = op.new_sheet(lname='Age data')
        age_spectra_wks.from_list(0, linePoints[0], lname="X values")
        age_spectra_wks.from_list(1, linePoints[1], lname="Y1 values")
        age_spectra_wks.from_list(2, linePoints[2], lname="Y2 values")
        age_spectra_wks.from_list(3, linePoints[3], lname="Set 1 X values")
        age_spectra_wks.from_list(4, linePoints[4], lname="Set 1 Y1 values")
        age_spectra_wks.from_list(5, linePoints[5], lname="Set 1 Y2 values")
        age_spectra_wks.from_list(6, linePoints[6], lname="Set 2 X values")
        age_spectra_wks.from_list(7, linePoints[7], lname="Set 2 Y1 values")
        age_spectra_wks.from_list(8, linePoints[8], lname="Set 2 Y2 values")
        # Isochron scatter plots
        isochron_wb = op.new_book('w', lname='Isochron data')
        isochron_set1_ws = isochron_wb.add_sheet(name='Isochron Set 1', active=False)
        isochron_set2_ws = isochron_wb.add_sheet(name='Isochron Set 2', active=False)
        isochron_set3_ws = isochron_wb.add_sheet(name='Isochron Unselected', active=False)
        isochron_lines_ws = isochron_wb.add_sheet(name='Isochron Lines', active=False)

        for index, item in enumerate(self.isochron_lines_data):
            isochron_lines_ws.from_list(index, item, lname='')
        for index, each_col in enumerate(arr.transpose(
                [arr.transpose(self.isochron_data)[i] for i in self.sample.SelectedSequence1])):
            isochron_set1_ws.from_list(index, each_col)  # Normal, invers, K-Cl-Ar 1, K-Cl-Ar 2, K-Cl-Ar 3, 3D
        for index, each_col in enumerate(arr.transpose(
                [arr.transpose(self.isochron_data)[i] for i in self.sample.SelectedSequence2])):
            isochron_set2_ws.from_list(index, each_col)  # Normal, invers, K-Cl-Ar 1, K-Cl-Ar 2, K-Cl-Ar 3, 3D
        for index, each_col in enumerate(arr.transpose(
                [arr.transpose(self.isochron_data)[i] for i in self.sample.UnselectedSequence])):
            isochron_set3_ws.from_list(index, each_col)  # Normal, invers, K-Cl-Ar 1, K-Cl-Ar 2, K-Cl-Ar 3, 3D

        # Age spectra plot
        graph = self.sample.AgeSpectraPlot
        gr = op.new_graph(lname='Age Spectra',
                          template=os.path.join(SETTINGS_ROOT, 'OriginExportTemplate.otpu'))
        gl_1 = gr[0]
        pl_1 = gl_1.add_plot(age_spectra_wks, coly='B', colx='A', type='l')  # 'l'(Line Plot)
        pl_2 = gl_1.add_plot(age_spectra_wks, coly='C', colx='A', type='l')  # 'l'(Line Plot)
        pl_3 = gl_1.add_plot(age_spectra_wks, coly='E', colx='D', type='l')  # set 1
        pl_4 = gl_1.add_plot(age_spectra_wks, coly='F', colx='D', type='l')  # set 1
        pl_5 = gl_1.add_plot(age_spectra_wks, coly='H', colx='G', type='l')  # set 2
        pl_6 = gl_1.add_plot(age_spectra_wks, coly='I', colx='G', type='l')  # set 2
        pl_1.color = pl_2.color = graph.line1.color
        pl_3.color = pl_4.color = graph.line3.color
        pl_5.color = pl_6.color = graph.line5.color
        gl_1.axis('y').title = 'Apparent age (Ma)'
        gl_1.axis('x').title = 'Cumulative \+(39)Ar released (%)'
        gl_1.axis('y').set_limits(float(graph.yaxis.min), float(graph.yaxis.max))
        gl_1.axis('x').set_limits(0, 100, 20)
        # Normal Isochron plots
        graph = self.sample.NorIsochronPlot
        gr = op.new_graph(lname='Normal Isochron',
                          template=os.path.join(SETTINGS_ROOT, 'OriginExportTemplate.otpu'))
        gl_1 = gr[0]
        pl_1 = gl_1.add_plot(isochron_set1_ws, colx='A', coly='C', type='s')  # 's'(Scatter Plot)
        pl_2 = gl_1.add_plot(isochron_set2_ws, colx='A', coly='C', type='s')  # 's'(Scatter Plot)
        pl_3 = gl_1.add_plot(isochron_set3_ws, colx='A', coly='C', type='s')  # 's'(Scatter Plot)
        for plt in gl_1.plot_list():
            plt.color = [graph.set1.color, graph.set2.color, '#333333'][plt.index()]
            plt.symbol_kind = 2
            plt.symbol_interior = 1
            plt.symbol_size = 3
        pl_1 = gl_1.add_plot(isochron_lines_ws, coly='B', colx='A', type='l')  # 'l'(Line Plot)
        pl_2 = gl_1.add_plot(isochron_lines_ws, coly='D', colx='C', type='l')  # 'l'(Line Plot)
        pl_1.color = graph.line1.color
        pl_2.color = graph.line2.color
        gl_1.axis('x').title = '\+(39)Ar / \+(36)Ar'
        gl_1.axis('y').title = '\+(40)Ar / \+(36)Ar'
        gl_1.axis('x').set_limits(float(graph.xaxis.min), float(graph.xaxis.max))
        gl_1.axis('y').set_limits(float(graph.yaxis.min), float(graph.yaxis.max))
        # print(pl_1.layer.GetNumProp(f"{gl_1.axis('x')}.inc"))
        # pl_1.layer.SetNumProp(pl_1._format_property('symbol.size'), 10)
        # print(pl_1.layer.GetNumProp(pl_1._format_property('symbol.size')))
        # Inverse Isochron plots
        graph = self.sample.InvIsochronPlot
        gr = op.new_graph(lname='Inverse Isochron',
                          template=os.path.join(SETTINGS_ROOT, 'OriginExportTemplate.otpu'))
        gl_1 = gr[0]
        pl_1 = gl_1.add_plot(isochron_set1_ws, colx='G', coly='I', type='s')  # 's'(Scatter Plot)
        pl_2 = gl_1.add_plot(isochron_set2_ws, colx='G', coly='I', type='s')  # 's'(Scatter Plot)
        pl_3 = gl_1.add_plot(isochron_set3_ws, colx='G', coly='I', type='s')  # 's'(Scatter Plot)
        for plt in gl_1.plot_list():
            plt.color = [graph.set1.color, graph.set2.color, '#333333'][plt.index()]
            plt.symbol_kind = 2
            plt.symbol_interior = 1
            plt.symbol_size = 3
        pl_1 = gl_1.add_plot(isochron_lines_ws, coly='F', colx='E', type='l')  # 'l'(Line Plot)
        pl_2 = gl_1.add_plot(isochron_lines_ws, coly='H', colx='G', type='l')  # 'l'(Line Plot)
        pl_1.color = graph.line1.color
        pl_2.color = graph.line2.color
        gl_1.axis('x').title = '\+(39)Ar / \+(40)Ar'
        gl_1.axis('y').title = '\+(36)Ar / \+(40)Ar'
        gl_1.axis('x').set_limits(float(graph.xaxis.min), float(graph.xaxis.max))
        gl_1.axis('y').set_limits(float(graph.yaxis.min), float(graph.yaxis.max))
        # Cl correlation 1
        graph = self.sample.KClAr1IsochronPlot
        gr = op.new_graph(lname='Cl correlation 1',
                          template=os.path.join(SETTINGS_ROOT, 'OriginExportTemplate.otpu'))
        gl_1 = gr[0]
        pl_1 = gl_1.add_plot(isochron_set1_ws, colx='M', coly='O', type='s')  # 's'(Scatter Plot)
        pl_2 = gl_1.add_plot(isochron_set2_ws, colx='M', coly='O', type='s')  # 's'(Scatter Plot)
        pl_3 = gl_1.add_plot(isochron_set3_ws, colx='M', coly='O', type='s')  # 's'(Scatter Plot)
        for plt in gl_1.plot_list():
            plt.color = [graph.set1.color, graph.set2.color, '#333333'][plt.index()]
            plt.symbol_kind = 2
            plt.symbol_interior = 1
            plt.symbol_size = 3
        pl_1 = gl_1.add_plot(isochron_lines_ws, coly='J', colx='I', type='l')  # 'l'(Line Plot)
        pl_2 = gl_1.add_plot(isochron_lines_ws, coly='L', colx='K', type='l')  # 'l'(Line Plot)
        pl_1.color = graph.line1.color
        pl_2.color = graph.line2.color
        gl_1.axis('x').title = '\+(39)Ar / \+(38)Ar'
        gl_1.axis('y').title = '\+(40)Ar / \+(38)Ar'
        gl_1.axis('x').set_limits(float(graph.xaxis.min), float(graph.xaxis.max))
        gl_1.axis('y').set_limits(float(graph.yaxis.min), float(graph.yaxis.max))
        # Cl correlation 2
        graph = self.sample.KClAr2IsochronPlot
        gr = op.new_graph(lname='Cl correlation 2',
                          template=os.path.join(SETTINGS_ROOT, 'OriginExportTemplate.otpu'))
        gl_1 = gr[0]
        pl_1 = gl_1.add_plot(isochron_set1_ws, colx='S', coly='U', type='s')  # 's'(Scatter Plot)
        pl_2 = gl_1.add_plot(isochron_set2_ws, colx='S', coly='U', type='s')  # 's'(Scatter Plot)
        pl_3 = gl_1.add_plot(isochron_set3_ws, colx='S', coly='U', type='s')  # 's'(Scatter Plot)
        for plt in gl_1.plot_list():
            plt.color = [graph.set1.color, graph.set2.color, '#333333'][plt.index()]
            plt.symbol_kind = 2
            plt.symbol_interior = 1
            plt.symbol_size = 3
        pl_1 = gl_1.add_plot(isochron_lines_ws, coly='N', colx='M', type='l')  # 'l'(Line Plot)
        pl_2 = gl_1.add_plot(isochron_lines_ws, coly='P', colx='O', type='l')  # 'l'(Line Plot)
        pl_1.color = graph.line1.color
        pl_2.color = graph.line2.color
        gl_1.axis('x').title = '\+(39)Ar / \+(40)Ar'
        gl_1.axis('y').title = '\+(38)Ar / \+(40)Ar'
        gl_1.axis('x').set_limits(float(graph.xaxis.min), float(graph.xaxis.max))
        gl_1.axis('y').set_limits(float(graph.yaxis.min), float(graph.yaxis.max))
        # Cl correlation 3
        graph = self.sample.KClAr3IsochronPlot
        gr = op.new_graph(lname='Cl correlation 3',
                          template=os.path.join(SETTINGS_ROOT, 'OriginExportTemplate.otpu'))
        gl_1 = gr[0]
        pl_1 = gl_1.add_plot(isochron_set1_ws, colx='Y', coly='AA', type='s')  # 's'(Scatter Plot)
        pl_2 = gl_1.add_plot(isochron_set2_ws, colx='Y', coly='AA', type='s')  # 's'(Scatter Plot)
        pl_3 = gl_1.add_plot(isochron_set3_ws, colx='Y', coly='AA', type='s')  # 's'(Scatter Plot)
        for plt in gl_1.plot_list():
            plt.color = [graph.set1.color, graph.set2.color, '#333333'][plt.index()]
            plt.symbol_kind = 2
            plt.symbol_interior = 1
            plt.symbol_size = 3
        pl_1 = gl_1.add_plot(isochron_lines_ws, coly='R', colx='Q', type='l')  # 'l'(Line Plot)
        pl_2 = gl_1.add_plot(isochron_lines_ws, coly='T', colx='S', type='l')  # 'l'(Line Plot)
        pl_1.color = graph.line1.color
        pl_2.color = graph.line2.color
        gl_1.axis('x').title = '\+(38)Ar / \+(39)Ar'
        gl_1.axis('y').title = '\+(40)Ar / \+(39)Ar'
        gl_1.axis('x').set_limits(float(graph.xaxis.min), float(graph.xaxis.max))
        gl_1.axis('y').set_limits(float(graph.yaxis.min), float(graph.yaxis.max))

        # Save the opju to your UFF.
        op.save(self.export_filepath)

        # Exit running instance of Origin.
        # Required for external Python but don't use with embedded Python.
        if op.oext:
            op.exit()
        return 0


class CreatePDF:
    def __init__(self, **kwargs):
        self.name = "PDF"
        self.sample = Sample()
        self.figure = Plot()
        self.export_filepath = ""
        self.page_size = [595, 842]
        self.data_bytes = b""
        self.component = []
        self.text = []
        self.frame = []
        self.axis_area = [138, 400, 360, 270]  # x0, y0, w, h
        with open(os.path.join(SETTINGS_ROOT, 'PDF_Template.txt'), 'rb') as f:
            self.data_str: str = f.read().decode('utf-8')
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _xmin(self):
        return float(self.figure.xaxis.min)

    def _xmax(self):
        return float(self.figure.xaxis.max)

    def _ymin(self):
        return float(self.figure.yaxis.min)

    def _ymax(self):
        return float(self.figure.yaxis.max)

    def _get_transfer_pos(self, x, y):
        x0, y0, w, h = self.axis_area
        x = (x - self._xmin()) / (self._xmax() - self._xmin()) * w + x0
        y = (y - self._ymin()) / (self._ymax() - self._ymin()) * h + y0
        return [x, y]

    def _get_isochron_line(self, point1, point2, color='1 0 0', width=1):
        line_str = ''
        if not len(point1) == len(point2) == 2:
            return line_str
        x0, y0, w, h = self.axis_area

        def _get_line_points(k, m):
            if k == 0:
                return [
                    [x0, m], [x0 + w, m]
                ]
            return [
                [x0, x0 * k + m], [x0 + w, (x0 + w) * k + m],
                [(y0 - m) / k, y0], [(y0 + h - m) / k, y0 + h]
            ]

        point_1 = self._get_transfer_pos(*point1)
        point_2 = self._get_transfer_pos(*point2)
        k = (point_2[1] - point_1[1]) / (point_2[0] - point_1[0])
        m = point_2[1] - point_2[0] * k
        line = []
        for point in _get_line_points(k, m):
            if self.is_in_area(*point):
                line.append(point)
        if len(line) == 2:
            line_str = f'{width} w\r{color} RG\r{line[0][0]} {line[0][1]} m {line[1][0]} {line[1][1]} l S\r'
        return line_str

    def _get_spectra_line(self, data, width=1, color='1 0 0'):
        """
        data = [[x1, x2, ..., xn], [y1, y2, ..., yn]]
        """
        x0, y0, w, h = self.axis_area
        num = 0
        line_str = ''
        if not data:
            return line_str
        data = arr.transpose(data)
        for index, point in enumerate(data):
            point = self._get_transfer_pos(*point)
            if not self.is_in_area(*point):
                if index == 0 and self.is_in_area(*self._get_transfer_pos(*data[index + 1])):
                    point[0] = x0
                elif index == (len(data) - 1) and self.is_in_area(*self._get_transfer_pos(*data[index - 1])):
                    point[0] = x0 + w
                elif 0 < index < (len(data) - 1) and (
                        self.is_in_area(*self._get_transfer_pos(*data[index + 1])) or self.is_in_area(
                    *self._get_transfer_pos(*data[index - 1]))):
                    if x0 < point[0] < (x0 + w):
                        point[1] = [y0, y0 + h][point[1] >= y0 + h]
                    else:
                        point[0] = [x0, x0 + w][point[0] >= x0 + w]
                else:
                    continue
            line_str = line_str + f'{point[0]} {point[1]} {"m " if num == 0 else "l "}'
            num += 1
        line_str = f'{width} w\r{color} RG\r' + line_str + 'S\r'
        return line_str

    def is_in_area(self, x, y):
        x0, y0, w, h = self.axis_area
        if x == -999:
            x = x0
        if y == -999:
            y = y0
        return x0 <= x <= x0 + w and y0 <= y <= y0 + h

    def set_axis_frame(self):
        from decimal import Decimal
        frame = ''
        x0, y0, w, h = self.axis_area
        frame += f'1 w\r0 0 0 RG\r{x0} {y0} {w} {h} re S\r'  # % 四个参数：最小x，最小y，宽度和高度

        xmin, xmax = float(self.figure.xaxis.min), float(self.figure.xaxis.max)
        nx, dx = int(self.figure.xaxis.split_number), float(self.figure.xaxis.interval)
        ymin, ymax = float(self.figure.yaxis.min), float(self.figure.yaxis.max)
        ny, dy = int(self.figure.yaxis.split_number), float(self.figure.yaxis.interval)

        for i in range(ny + 1):
            yi = y0 + i * h * dy / (ymax - ymin)
            if self.is_in_area(-999, yi):
                frame += f'{x0} {yi} m {x0 - 4} {yi} l S\r'
                frame += f'BT\r1 0 0 1 {x0 - 4 - 32} {yi - 4} Tm\r/F1 12 Tf\r0 0 0 rg\r({Decimal(str(ymin)) + i * Decimal(str(dy))}) Tj\rET\r'
        for i in range(nx + 1):
            xi = x0 + i * w * dx / (xmax - xmin)
            if self.is_in_area(xi, -999):
                frame += f'{xi} {y0} m {xi} {y0 - 4} l S\r'
                frame += f'BT\r1 0 0 1 {xi - 12} {y0 - 16} Tm\r/F1 12 Tf\r0 0 0 rg\r({Decimal(str(xmin)) + i * Decimal(str(dx))}) Tj\rET\r'
        self.frame.append(frame)
        return frame

    def set_main_content(self):
        content = ''
        if self.figure.type == 'isochron':
            scatter_w, scatter_h = 5, 5
            if not arr.is_empty(self.figure.line1.info):
                content += self._get_isochron_line(*self.figure.line1.data, width=1, color='1 0 0')
            if not arr.is_empty(self.figure.line2.info):
                content += self._get_isochron_line(*self.figure.line2.data, width=1, color='0 0 1')
            for point in arr.transpose(self.figure.data):
                x, y = self._get_transfer_pos(point[0], point[2])
                if self.is_in_area(x, y):
                    if int(point[5]) - 1 in self.sample.SelectedSequence1:
                        color = '0 0 0 RG\r1 0 0 rg\r'
                    elif int(point[5]) - 1 in self.sample.SelectedSequence2:
                        color = '0 0 0 RG\r0 0 1 rg\r'
                    else:
                        color = '0 0 0 RG\r1 1 1 rg\r'
                    content = content + color + \
                              f'{x - scatter_w / 2} {y - scatter_h / 2} {scatter_w} {scatter_h} re b\r'
        elif self.figure.type == 'spectra':
            for index, data in enumerate([self.figure.data, self.figure.set1.data, self.figure.set2.data]):
                color = ['0 0 0', '1 0 0', '0 0 1'][index]
                data = arr.transpose(data)
                content = content + self._get_spectra_line(data[:2], color=color) + \
                          self._get_spectra_line([data[0], data[2]], color=color)
        self.component.append(content)
        return content

    def set_text(self):
        text = ''
        x0, y0, w, h = self.axis_area
        # Figure Title
        text += f'BT\r1 0 0 1 {x0 + 10} {y0 - 20 + h} Tm\n/F1 12 Tf\r({self.sample.Info.sample.name}) Tj\rET\r'
        if self.figure.type == 'isochron':
            xaxis_title_number = ''.join(list(filter(str.isdigit, self.figure.xaxis.title.text)))
            yaxis_title_number = ''.join(list(filter(str.isdigit, self.figure.yaxis.title.text)))
            # X axis title
            x_title_length = 5 * 12  # length * font point size
            text += '\n'.join([
                'BT', f'1 0 0 1 {x0 + w / 2 - x_title_length / 2} {y0 - 30} Tm',
                # % 使用Tm将文本位置设置为（35,530）前四个参数是cosx, sinx, -sinx, cosx表示逆时针旋转弧度
                '/F1 8 Tf', '5 Ts', f'({xaxis_title_number[:2]}) Tj', '/F1 12 Tf', '0 Ts', '(Ar / ) Tj',
                '/F1 8 Tf', '5 Ts', f'({xaxis_title_number[2:4]}) Tj', '/F1 12 Tf', '0 Ts', '(Ar) Tj', 'ET',
            ])
            # Y axis title
            y_title_length = 5 * 12  # length * font point size
            text += '\n'.join([
                'BT', f'0 1 -1 0 {x0 - 40} {y0 + h / 2 - y_title_length / 2} Tm',
                # % 使用Tm将文本位置设置为（35,530）前四个参数是cosx, sinx, -sinx, cosx表示逆时针旋转弧度
                '/F1 8 Tf', '5 Ts', f'({yaxis_title_number[:2]}) Tj', '/F1 12 Tf', '0 Ts', '(Ar / ) Tj',
                '/F1 8 Tf', '5 Ts', f'({yaxis_title_number[2:4]}) Tj', '/F1 12 Tf', '0 Ts', '(Ar) Tj', 'ET',
            ])

        elif self.figure.type == 'spectra':
            # X axis title
            x_title_length = 13 * 12  # length * font point size
            text += '\n'.join([
                'BT', f'1 0 0 1 {x0 + w / 2 - x_title_length / 2} {y0 - 30} Tm',
                '/F1 12 Tf', '0 Ts', '(Cumulative ) Tj', '/F1 8 Tf', '5 Ts', f'(39) Tj',
                '/F1 12 Tf', '0 Ts', '(Ar Released (%)) Tj', 'ET',
            ])
            # Y axis title
            y_title_length = 9 * 12  # length * font point size
            text += '\n'.join([
                'BT', f'0 1 -1 0 {x0 - 40} {y0 + h / 2 - y_title_length / 2} Tm',
                '/F1 12 Tf', '0 Ts', f'(Apparent Age (Ma)) Tj', 'ET',
            ])
            # Text 1
            info = self.figure.set1.info
            if len(info) == 8 and self.figure.text1.text != '':
                sum39 = findall('∑{sup|39}Ar = (.*)', self.figure.text1.text)[1]
                text += '\n'.join([
                    'BT', f'1 0 0 1 {x0 + w / 4} {y0 + h / 2} Tm',
                    '/F1 12 Tf', '0 Ts', f'(t) Tj', '/F1 8 Tf', '-2 Ts', f'(p) Tj',
                    '/F1 12 Tf', '0 Ts',
                    f'( = {info[4]:.2f} <261> {info[6]:.2f} Ma, MSMD = {info[3]:.2f}, ∑) Tj',
                    '/F1 8 Tf', '5 Ts', f'(39) Tj',
                    '/F1 12 Tf', '0 Ts',
                    f'(Ar = {sum39}) Tj',
                    'ET',
                ])
            # Text 2
            text2 = findall('∑{sup|39}Ar = (.*)', self.figure.text2.text)[1]

        self.text.append(text)
        return text

    def set_split_line(self):
        others = []
        for i in range(200):
            if i * 50 >= self.page_size[0]:
                break
            others.append(f'[2] 0 d\n{i * 50} 0 m {i * 50} {self.page_size[1]} l S')
        for i in range(200):
            if i * 50 >= self.page_size[1]:
                break
            others.append(f'[2] 0 d\n0 {i * 50} m {self.page_size[0]} {i * 50} l S')
        self.data_str = self.data_str.replace(
            '% <flag: others>\r',
            '% <flag: others>\r' + '0.75 G\n' + '\n'.join(others),
        )

    def set_info(self):
        from datetime import datetime, timezone, timedelta
        date = str(datetime.now(tz=timezone(offset=timedelta(hours=8))))
        date = findall('(.*)-(.*)-(.*) (.*):(.*):(.*)\.(.*)', date)[0]
        date = ''.join(date[0:6])
        date = 'D:' + date + "+08'00'"
        self.data_str = self.data_str.replace(
            '% <flag: info CreationDate>',
            f"{date}",
        )
        self.data_str = self.data_str.replace(
            '% <flag: info ModDate>',
            f"{date}",
        )

        self.data_str = self.data_str.replace(
            '% <flag: info Title>',
            f'{self.sample.Info.sample.name} - {self.figure.name}'
        )
        self.data_str = self.data_str.replace(
            '% <flag: page title>\r',
            '% <flag: page title>\r' +
            f'(<This is a demo of the exported PDF.>) Tj T*\n'
            f'(<The PDFs can be freely edited in Adobe Illustrator.>) Tj\n'
        )

    def set_replace(self):
        self.data_str = self.data_str.replace(
            '% <main contents>\r',
            '% <main contents>\r' + '\r\n'.join(self.component)
        )
        self.data_str = self.data_str.replace(
            '% <frames>\r',
            '% <frames>\r' + '\r\n'.join(self.frame)
        )
        self.data_str = self.data_str.replace(
            '% <texts>\r',
            '% <texts>\r' + '\r\n'.join(self.text)
        )

    def get_pdf(self):
        self.do_function(
            self.set_main_content,
            self.set_axis_frame,
            self.set_text,
            self.set_info,
            self.set_replace,
            # self.set_split_line,
            self.toBetys,
            self.save,
        )

    def get_contents(self):
        self.do_function(
            self.set_main_content,
            self.set_axis_frame,
            self.set_text,
        )
        return {
            'component': self.component,
            'frame': self.frame,
            'text': self.text,
        }

    def toBetys(self):
        self.data_bytes = self.data_str.encode('utf-8')
        return self.data_bytes

    def save(self):
        with open(self.export_filepath, 'wb') as f:
            f.write(self.data_bytes)

    def do_function(self, *handlers):
        for handler in handlers:
            try:
                handler()
            except Exception:
                print(traceback.format_exc())
                continue


class CustomUnpickler(pickle.Unpickler):
    """https://blog.csdn.net/weixin_43236007/article/details/109506191"""

    def find_class(self, module, name):
        try:
            return super().find_class(__name__, name)
        except AttributeError:
            return super().find_class(module, name)
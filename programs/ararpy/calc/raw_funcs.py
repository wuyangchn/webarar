#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - calc - raw_funcs
# ==========================================
#
#
#
"""
import traceback
import numpy as np
from .arr import transpose, is_twoD
from . import regression


"""get regression results for raw data points"""


def get_raw_data_regression_results(points_data, unselected: list = None):
    """
    Parameters
    ----------
    points_data : two dimensional list. like [[x1, y1], [x2, y2], ..., [xn, yn]]
    unselected :

    Returns
    -------

    """
    if unselected is None:
        unselected = []
    linesData, linesResults = [], []
    x, y = transpose(points_data)
    un_x = transpose(unselected)[0] if is_twoD(unselected) else []
    reg_handler = [
        regression.linest, regression.quadratic, regression.exponential,
        regression.power, regression.average]
    size = 50
    lines_x = [(max(x + un_x) - 0) / size * i for i in range(size + 1)]
    for i in range(len(reg_handler)):
        try:
            res = reg_handler[i](a0=y, a1=x)
            line_data = transpose([lines_x, res[7](lines_x)])
            line_results = res[0:4]
            if np.isin(np.inf, line_data) or np.isin(np.nan, line_data):
                raise ZeroDivisionError(f"Infinite value or nan value.")
            if abs(res[0] - min(y)) > 5 * (max(y) - min(y)):
                raise ValueError
        except RuntimeError:
            line_data, line_results = [], ['RuntimeError', np.nan, np.nan, np.nan]
        except np.linalg.LinAlgError:
            line_data, line_results = [], ['MatrixError', np.nan, np.nan, np.nan]
        except TypeError or IndexError:
            line_data, line_results = [], ['NotEnoughPoints', np.nan, np.nan, np.nan]
        except ZeroDivisionError:
            line_data, line_results = [], [np.inf, np.nan, np.nan, np.nan]
        except ValueError:
            line_data, line_results = [], ['BadFitting', np.nan, np.nan, np.nan]
        except:
            line_data, line_results = [], [np.nan, np.nan, np.nan, np.nan]
        linesData.append(line_data)
        linesResults.append(line_results)
    return linesData, linesResults

#
# def get_lines_data(sequenceData, only_isotope=None):
#     def _get_scatter_x(a: list, nope=50):
#         interval = (max(a) - 0) / nope
#         return [interval * (i + 1) for i in range(nope)]
#
#     linesData, linesResults = [], []
#     for i in range(5):
#         try:
#             if isinstance(only_isotope, int) and i != only_isotope:
#                 raise IndexError
#             _ = transpose(sequenceData[i])
#             x, y = _[0], _[1]
#             try:
#                 line_res = regression.linest(a0=y, a1=x)
#             except:
#                 line_res = ['BadFitting', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
#             try:
#                 quad_res = regression.quadratic(a0=y, a1=x)
#             except:
#                 quad_res = ['BadFitting', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
#             try:
#                 exp_res = regression.exponential(a0=y, a1=x)
#             except:
#                 exp_res = ['BadFitting', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
#             try:
#                 pow_res = regression.power(a0=y, a1=x)
#             except:
#                 pow_res = ['BadFitting', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
#             else:
#                 if abs(pow_res[0]) > 10 * max(y):
#                     pow_res = ['BadFitting', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
#                 elif pow_res[0] < 0:
#                     pow_res = ['Negative', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
#             try:
#                 ave_res = regression.average(a0=y)
#             except:
#                 ave_res = ['BadFitting', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
#
#             lines_x = [_x for _x in [0] + _get_scatter_x(x)]
#             linesData.append([])
#             for index, res in enumerate([line_res, quad_res, exp_res, pow_res, ave_res]):
#                 try:
#                     linesData[i].append(transpose([lines_x, res[7](lines_x)]))
#                 except Exception as e:
#                     linesData[i].append([])
#             linesResults.append([line_res[0:4], quad_res[0:4], exp_res[0:4], pow_res[0:4], ave_res[0:4]])
#         except IndexError or ValueError:
#             linesData.append([[], [], [], [], []])
#             linesResults.append([[], [], [], [], []])
#
#     return linesData, linesResults

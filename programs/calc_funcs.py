#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : FuncsCalc.py
# @Author : Yang Wu
# @Date   : 2021/12/20
# @Email  : wuy@cug.edu.cn

"""
Functions involved in entire calculations of Ar-Ar dating.
Important Constants:

    Isotopic Mass:
    M41 = 40.9645008
    M40 = 39.962383123
    M39 = 38.964313
    M38 = 37.9627322
    M37 = 36.9667759
    M36 = 35.96754628
    M35 = 34.9752567

    M40 = 39.962384                                 # Nuclides and Isotopes, Chart of nuclides, 14th edition
    M38 = 37.962732                                 # Nuclides and Isotopes, Chart of nuclides, 14th edition
    M36 = 35.967546                                 # Nuclides and Isotopes, Chart of nuclides, 14th edition

    M40 = 39.962383123                              # Nuclides and Isotopes, Chart of nuclides, 16th edition, 2002
    M38 = 37.962732                                 # Nuclides and Isotopes, Chart of nuclides, 16th edition, 2002
    M36 = 35.9675463                                # Nuclides and Isotopes, Chart of nuclides, 16th edition, 2002

    Atom Percent Abundance:
    Ar40_AA = 99.6003                               # Nuclides and Isotopes, Chart of nuclides, 16th edition, 2002
    Ar38_AA = 0.0632                                # Nuclides and Isotopes, Chart of nuclides, 16th edition, 2002
    Ar36_AA = 0.3365                                # Nuclides and Isotopes, Chart of nuclides, 16th edition, 2002

    Atmospheric Isotope Proportion:
    (40Ar/36Ar)a = 295.5                            # Nier, 1950; Steiger and Jäger, 1977
    (38Ar/36Ar)a = 0.1869                           # Nier, 1950; Steiger and Jäger, 1977

    Artificially Radioactive:
    Ar35: Half_Life = 1.77 s                        # Nuclides and Isotopes, Chart of nuclides, 16th edition, 2002
          Modes_of_Decay_1 = positron
          Energy_of_Radiation_1 = 4.943 MeV
          Modes_of_Decay_2 = gamma ray
          Energy_of_Radiation_2 = 1219.2 keV
    Ar37: Half_Life = 35.0 d
    Ar39: Half_Life = 269 a
"""
import traceback

import decimal
from math import exp, log, cos, acos, ceil, sqrt, atan, sin, gamma
from typing import List, Any
from scipy.optimize import fsolve
from scipy.stats import distributions
import numpy as np

math_e = 2.718281828459045
math_pi = 3.141592653589793


def is_number(*args):
    for i in args:
        if not isinstance(i, (float, int)):
            return False
    return True


def is_not_zero(*args):
    for i in args:
        if i == 0:
            return False
    return True


def get_axis_scale(data: list, count=6, increment=None, extra_count=0, min_interval=1):
    """
    parameters: data is necessary, default count of sticks is 6 if increment is not defined,
    extra count is used to extend space
    return: min, max, count, increment
    """
    if len(data) == 0:
        return 0, 1, 5, 0.2  # Default return
    _max = max(data)
    _min = min(data)
    interval = (_max - _min) / count
    if interval == 0:
        interval = 10
    mag = 10 ** int(log(interval, 10)) if interval >= 1 else 10 ** (int(log(interval, 10)) - 1)
    if not increment:
        increment = decimal.Decimal(
            str(decimal.Decimal(int(interval / mag // min_interval) + min_interval) * decimal.Decimal(str(mag))))
    else:
        increment = decimal.Decimal(increment)
    start = decimal.Decimal(0)
    if _min < 0:
        start = -increment
        while start > _min:
            start -= increment
    else:
        while start + increment < _min:
            start += increment
    count = 0
    while count * increment + start < _max:
        count += 1
    end = decimal.Decimal(str(count + extra_count)) * decimal.Decimal(str(increment)) + start
    start -= decimal.Decimal(extra_count) * decimal.Decimal(str(increment))
    start = 0 if start < 0 <= _min else start
    count = (end - start) / increment
    return float(start), float(end), int(count), float(increment)


def get_isochron(x: list, sx: list, y: list, sy: list, z: list, sz: list):
    _n = min([len(x), len(sx), len(y), len(sy), len(z), len(sz)])
    # x / z
    k0 = [x[i] / z[i] if z[i] != 0 and is_number(x[i], z[i]) else 0 for i in range(_n)]
    k1 = [error_div((x[i], sx[i]), (z[i], sz[i])) if z[i] != 0 and is_number(x[i], sx[i], z[i], sz[i]) else 0 for i in
          range(_n)]
    # y / z
    k2 = [y[i] / z[i] if z[i] != 0 and is_number(y[i], z[i]) else 0 for i in range(_n)]
    k3 = [error_div((y[i], sy[i]), (z[i], sz[i])) if z[i] != 0 and is_number(y[i], sy[i], z[i], sz[i]) else 0 for i in
          range(_n)]
    pho = [
        error_cor(sx[i] / x[i], sy[i] / y[i], sz[i] / z[i]) if is_not_zero(x[i], y[i], z[i]) and is_number(x[i], y[i],
                                                                                                           z[i], sx[i],
                                                                                                           sy[i],
                                                                                                           sz[i]) else 0
        for i in range(_n)]
    return [k0, k1, k2, k3, pho]


def get_3D_isochron(x1: list, sx1: list, x2: list, sx2: list, x3: list, sx3: list, z: list, sz: list):
    _n = min([len(x1), len(sx1), len(x2), len(sx2), len(x3), len(sx3), len(z), len(sz)])
    # x1 / z
    k0 = [x1[i] / z[i] if z[i] != 0 and is_number(x1[i], z[i]) else 0 for i in range(_n)]
    k1 = [error_div((x1[i], sx1[i]), (z[i], sz[i])) if z[i] != 0 and is_number(x1[i], sx1[i], z[i], sz[i]) else 0 for i
          in range(_n)]
    # x2 / z
    k2 = [x2[i] / z[i] if z[i] != 0 and is_number(x2[i], z[i]) else 0 for i in range(_n)]
    k3 = [error_div((x2[i], sx2[i]), (z[i], sz[i])) if z[i] != 0 and is_number(x2[i], sx2[i], z[i], sz[i]) else 0 for i
          in range(_n)]
    # x3 / z
    k4 = [x3[i] / z[i] if z[i] != 0 and is_number(x3[i], z[i]) else 0 for i in range(_n)]
    k5 = [error_div((x3[i], sx3[i]), (z[i], sz[i])) if z[i] != 0 and is_number(x3[i], sx3[i], z[i], sz[i]) else 0 for i
          in range(_n)]
    # r1 between x and y
    r1 = [
        error_cor(sx1[i] / x1[i], sx2[i] / x2[i], sz[i] / z[i])
        if is_not_zero(x1[i], x2[i], z[i]) and is_number(x1[i], x2[i], z[i], sx1[i], sx2[i], sz[i])
        else 0 for i in range(_n)]
    # r2 between x and z
    r2 = [
        error_cor(sx1[i] / x1[i], sx3[i] / x3[i], sz[i] / z[i])
        if is_not_zero(x1[i], x3[i], z[i]) and is_number(x1[i], x3[i], z[i], sx1[i], sx3[i], sz[i])
        else 0 for i in range(_n)]
    # r3 between y and z
    r3 = [
        error_cor(sx2[i] / x2[i], sx3[i] / x3[i], sz[i] / z[i])
        if is_not_zero(x2[i], x3[i], z[i]) and is_number(x2[i], x3[i], z[i], sx2[i], sx3[i], sz[i])
        else 0 for i in range(_n)]
    return [k0, k1, k2, k3, k4, k5, r1, r2, r3]


def get_histogram_data(x: list, s: float = None, r: str = 'sturges', w: float = None, c: int = None):
    """
    Parameters:
        x: input data to yield bins
        s: starting point
        r: rules, string
        w: bin width or interval, float for specific number
        c: bin count
        default method to get bin width and count is Rice rule
    returns: counts: [number of points in each bin], bins: [half bins], s, r, w, c, e, res: [values in each bin]
    """
    if len(x) == 0 or max(x) == min(x):
        return None
    else:
        x = [round(xi, 2) for xi in x]
    if isinstance(r, str) and r.lower().find('square-root') != -1:
        # Square-root choice, used by Excel's Analysis Toolpak histograms and many other
        c = ceil(len(x) ** (1. / 2.))
    if isinstance(r, str) and r.lower().find('sturges') != -1:
        # Sturges' formula, Ceiling(log2n)
        c = ceil(log(len(x), 2)) + 1
    if isinstance(r, str) and r.lower().find('rice') != -1:
        # Rice Rule
        c = ceil(2 * len(x) ** (1. / 3.))
    if isinstance(r, str) and r.lower().find('scott') != -1:
        # Scott's normal reference rule, optimal for random samples of normally distributed data
        w = ceil(3.49 * (sum([float(i - sum(x) / len(x)) ** 2 for i in x]) / len(x)) ** (1. / 2.) / len(x) ** (1. / 3.))
        d = 0.5 * 10 ** (int(log(w, 10)) - 1)
    if w is None and c is None:
        return get_histogram_data(x=x, s=s, w=w, c=c, r='sturges')

    if s is None and isinstance(c, int):
        d = 0.5 * 10 ** int(log(abs(max(x) - min(x)) / c, 10))
    if s is None:
        d = d if min(x) - d >= 0 else min(x)
        s = round(min(x) - d, 2)
        e = round(max(x) + d, 2)
    else:
        e = round(max(x) + min(x) - s, 2)
    if isinstance(c, int) and not isinstance(w, (int, float)):
        w = round(abs(e - s) / c, 2)
    bins = [s + i * w for i in range(10000) if s + (i - 1) * w <= max(x)]
    bins = list(set(bins))
    bins.sort()
    c = len(bins) - 1
    counts = [0] * c
    res = [[]] * c
    half_bins = [round((bins[i] + bins[i + 1]) / 2, 2) for i in range(c)]
    bin_ranges = [[]] * c
    for i in range(c):
        bin_ranges[i] = [round(bins[i], 2), round(bins[i + 1], 2)]
        for xi in x:
            if bins[i] <= xi < bins[i + 1] or bins[i] <= xi <= bins[i + 1] and i == c - 1:
                counts[i] += 1
                res[i].append(xi)

    return counts, half_bins, bin_ranges, s, r, w, c, bins[-1], res


def get_kde(x: list, h: (float, int) = None, a: str = None, k: str = 'normal', s: (float, int) = None,
            e: (float, int) = None, n: int = 200):
    """
    Parameters:
        x: input data
        h: bandwidth
        a: auto width rule
        k: kernel function name, default is normal, standard normal density function
        s: KDE curve starting point
        e: KDE curve ending point
        n: points number of KDE line
    Returns:
        None
    """
    x = [round(xi, 2) for xi in x]
    x.sort()

    def get_uniform_x(_x: list, _s=s, _e=e, _np=n):
        _s = min(_x) if _s is None else _s
        _e = max(_x) if _e is None else _e
        _line_x = []
        _step = abs(_e - _s) / _np
        _line_x = [_s + i * _step for i in range(_np)] + [_e]
        _line_x.sort()
        return _line_x

    def h_scott(_x, _se):  # Scott, 1992
        return 1.06 * _se * len(_x) ** (-1. / 5.)

    def h_silverman(_x, _se):  # Silverman, 1986
        return 0.9 * min(_se, (_x[int(3 / 4 * len(_x))] - _x[int(1 / 4 * len(_x))]) / 1.34) * len(_x) ** (-1. / 5.)

    # Normal function
    def k_normal(_xi, _u=0, _se=1, _h=h):
        return 1 / (_se * sqrt(2 * math_pi)) * (exp(-1. / 2. * ((_xi - _u) / (_h * _se)) ** 2))

    def k_epanechnikov(_xi, _u=0, _h=h):
        _xi = (_xi - _u) / _h
        return 3 / 4 * (1 - _xi ** 2) if abs(_xi) <= 1 else 0

    def k_uniform(_xi, _u=0, _h=h):
        _xi = (_xi - _u) / _h
        return 1 / 2 if abs(_xi) <= 1 else 0

    def k_triangular(_xi, _u=0, _h=h):
        _xi = (_xi - _u) / _h
        return 1 - abs(_xi) if abs(_xi) <= 1 else 0

    mean_x = sum(x) / len(x)
    se = sqrt(sum([(xi - mean_x) ** 2 for xi in x]) / (len(x) - 1))

    if (a is None or a == 'none') and (h is None or h <= 0):
        # Default rule for h is Scott's rule
        a = 'Scott'
    if isinstance(a, str):
        if a.lower() == 'scott':
            h = h_scott(x, se)
        elif a.lower() == 'silverman':
            h = h_silverman(x, se)
        else:
            a = 'none'
    else:
        a = 'none'

    # Get points that are evenly distributed over the range (min_x, max_x) to get a KDE curve
    line_x = get_uniform_x(_x=x, _s=s, _e=e)

    if k.lower() == 'normal':
        k_normal_res = [[k_normal(_xi, _u=xi, _h=h) for _xi in line_x] for xi in x]
    elif k.lower() == 'epanechnikov':
        k_normal_res = [[k_epanechnikov(_xi, _u=xi, _h=h) for _xi in line_x] for xi in x]
    elif k.lower() == 'uniform':
        k_normal_res = [[k_uniform(_xi, _u=xi, _h=h) for _xi in line_x] for xi in x]
    elif k.lower() == 'triangular':
        k_normal_res = [[k_triangular(_xi, _u=xi, _h=h) for _xi in line_x] for xi in x]
    else:
        return get_kde(x=x, h=h, a=a, k='normal', s=s, e=e, n=n)

    res = [
        sum([k_normal_res[j][i] for j in range(len(x))]) / (len(x) * h) for i in range(len(line_x))
    ]

    return [[line_x, res], h, k, a]


def get_ellipse(x: float, sx: float, y: float, sy: float, r: float):
    x, sx, y, sy, r = float(x), float(sx), float(y), float(sy), float(r)
    Qxx = sx ** 2
    Qxy = sx * sy * r
    Qyy = sy ** 2
    # Calculate the ellipse's short semi-axial and long semi-axial
    k = pow((Qxx - Qyy) ** 2 + 4 * Qxy ** 2, 0.5)
    Qee = (Qxx + Qyy + k) / 2
    Qff = (Qxx + Qyy - k) / 2
    e = pow(Qee, 0.5)  # long semi-axial
    f = pow(Qff, 0.5)  # short semi-axial
    phi_e = atan((Qee - Qxx) / Qxy) if Qxy != 0 else 0 if Qxx >= Qyy else math_pi / 2  # radian

    # adjust
    plt_sfactor = 1
    if plt_sfactor == 1:
        v = 2.279  # 68% confidence limit, 1 sigma
    elif plt_sfactor == 2:
        v = 5.991  # 95% confidence limit, 2 sigma, Isoplot R always gives ellipse with 95% confidence
    else:
        v = 1
    e = e * pow(v, 0.5)
    f = f * pow(v, 0.5)

    ellipse_points = []
    for i in range(24):
        theta = i * 15 / 180 * math_pi
        ellipse_points.append([
            e * cos(theta) * cos(phi_e) - f * sin(theta) * sin(phi_e) + x,
            e * cos(theta) * sin(phi_e) + f * sin(theta) * cos(phi_e) + y
        ])

    return ellipse_points


'-----------------------'
'--J Value Calculation--'
'-----------------------'


def j_value(age: float, sage: float, r: float, sr: float, f: float, rsf: float):
    """
    :param age: age of the reference standard sample, in Ma
    :param sage: 1 sigma error of age
    :param r: 40/39 ratio of the reference standard standard sample
    :param sr: 1 sigma error of 40/39 ratio
    :param f: decay constant(lambda) of K
    :param rsf: relative error of decay constant
    :return: J value | error
    """
    f = f * 1000000  # exchange to unit of Ma
    rsf = f * rsf / 100  # exchange to absolute error
    k0 = (exp(f * age) - 1) / r
    v1 = rsf ** 2 * (age * exp(f * age) / r) ** 2
    v2 = sage ** 2 * (f * exp(f * age) / r) ** 2
    v3 = sr ** 2 * ((1 - exp(f * age)) / r ** 2) ** 2
    k1 = pow(v1 + v2 + v3, 0.5)
    return k0, k1


'------------------------'
'--Correction Functions--'
'------------------------'


def get_mdf(rm: float, srm: float, m1: float, m2: float, ra: float = 298.56, sra: float = 0):
    """
    :param rm: ratio 40a/36a
    :param srm: error of ratio in one sigma
    :param m1: Ar36 isotopic mass
    :param m2: Ar40 isotopic mass
    :param ra: theoretical 40a/36a
    :param sra: error of theoretical 40a/36a
    :return: linear mdf, error, exp mdf, error, pow mdf, error
    """
    sm1 = 0
    sm2 = 0
    delta_m = m2 - m1
    sdelta_m = error_add(sm2, sm1)
    ratio_m = m2 / m1
    sratio_m = error_div((m2, sm2), (m1, sm1))
    isAapkop = True
    if isAapkop:
        # line
        k1 = (ra / rm + delta_m - 1) / delta_m  # A.A.P.Koppers
        k2 = error_div(((ra / rm + delta_m - 1), error_div((ra, sra), (rm, srm))), (delta_m, sdelta_m))
        # exp
        try:
            k3 = (log(ra / rm) / log(ratio_m)) * (1 / m1) + 1  # A.A.P.Koppers
            v1 = error_log(ra / rm, error_div((ra, sra), (rm, srm)))
            v2 = error_log(ratio_m, sratio_m)
            v3 = error_div((log(ra / rm), v1), (log(ratio_m), v2))
            k4 = error_div((log(ra / rm) / log(ratio_m), v3), (m1, sm1))
        except Exception:
            k3, k4 = "Null", "Null"
        # pow
        try:
            k5 = pow((ra / rm), (1 / delta_m))  # A.A.P.Koppers
            k6 = error_pow((ra / rm, error_div((ra, sra), (rm, srm))),
                           (1 / delta_m, error_div((1, 0), (delta_m, sdelta_m))))
        except Exception:
            k5, k6 = "Null", "Null"
        return k1, k2, k3, k4, k5, k6
    else:
        mdf_line_2 = (rm / ra - 1) / delta_m  # Ryu et al., 2013
        return mdf_line_2, 0, 0, 0, 0, 0


def corr_blank(a0: list, e0: list, a1: list, e1: list):
    """
    :param a0: a list of tested isotope value
    :param e0: 1 sigma error of a0, list type
    :param a1: a list of blank isotope value
    :param e1: 1 sigma error of a1, list type
    :return: list of corrected data | error list
    """
    # Do not force negative value to zero in correcting blank...
    k0 = [a0[i] - a1[i] for i in range(len(a0))]
    k1 = [error_add(e0[i], e1[i]) for i in range(len(k0))]
    return [k0, k1]


def corr_discr(a0: list, e0: list, mdf: list, smdf: list, m: list, m40: list, isRelative=True, method="l"):
    """
    :param a0: a list of tested isotope value
    :param e0: 1 sigma error of a0, list type
    :param mdf: mass discrimination factor(MDF), list
    :param smdf: absolute error of MDF, list
    :param m: mass of isotope being corrected
    :param m40: mass of Ar40, default value is defined above
    :param isRelative: errors of params are in a relative format
    :param method: correction method, "l" or "linear", "e" or "exponential", "p" or "power"
    :return: corrected value | error of corrected value
    linear correction, MDF = [(Ar40/Ar36)true / (Ar40/Ar36)measure] * 1 / MD - 1 / MD + 1
    corr = blank_corrected / [MD * MDF - MD +1]
    """
    r0, r1 = [], []
    if isRelative:
        smdf = [smdf[i] * mdf[i] / 100 for i in range(len(smdf))]
    for i in range(min([len(arg) for arg in [a0, e0, mdf, smdf]])):
        delta_mass = abs(m40[i] - m[i])
        ratio_mass = abs(m40[i] / m[i]) if m[i] != 0 else 1
        if method.lower()[0] == 'l':
            k0 = 1 / (delta_mass * mdf[i] - delta_mass + 1) if (delta_mass * mdf[i] - delta_mass + 1) != 0 else 0
            k1 = error_div((1, 0), (delta_mass * mdf[i] - delta_mass + 1, smdf[i] * delta_mass))
        elif method.lower()[0] == 'e':
            k0 = 1 / (ratio_mass ** (mdf[i] * m40[i] - m[i]))
            k1 = error_div((1, 0), (ratio_mass ** (mdf[i] * m40[i] - m[i]), error_pow((ratio_mass, 0), (
                mdf[i] * m40[i] - m[i], error_mul((mdf[i], smdf[i]), (m40[i], 0))))))
        elif method.lower()[0] == 'p':
            k0 = 1 / (mdf[i] ** delta_mass)
            k1 = error_div((1, 0), (mdf[i] ** delta_mass, error_pow((mdf[i], smdf[i]), (delta_mass, 0))))
        else:
            k0 = 1
            k1 = 0
        r0.append(a0[i] * k0)
        r1.append(error_mul((a0[i], e0[i]), (k0, k1)))
    return [r0, r1]


def corr_decay(a0: list, e0: list, t1: list, t2: list, t3: list, f: list, sf: list, unit: str = 'h', isRelative=True):
    r0, r1 = [], []
    if isRelative:
        sf = [sf[i] * f[i] / 100 for i in range(len(sf))]
    for i in range(len(a0)):
        k = get_decay_factor(t1[i], t2[i], t3[i], f[i], sf[i], unit)
        r0.append(a0[i] * k[0])
        r1.append(error_mul((a0[i], e0[i]), (k[0], k[1])))
    return [r0, r1]


def get_decay_factor(t1: list, t2: list, t3: list, f: float, sf: float, unit: str = 'h'):
    """
    :param t1: [year, month, day, hour, min, (second)], test start time
    :param t2: irradiation end time for all cycles, [[year, month, day, hour, min],...]
    :param t3: irradiation durations for all cycles, list for all irradiation cycles, in hour
    :param f: decay constant of K
    :param sf: absolute error of f
    :param unit: unit of decay constant, input 'h' or 'a'
    :return: correction factor | error of factor | stand duration
    """
    v1 = []
    v2 = []
    e1 = []
    # t_year, t_month, t_day, t_hour, t_min = t1
    t_test_start = get_datetime(*t1)  # the time when analysis began
    t2 = [get_datetime(*i) for i in t2]  # the time when irradiation ended for all cycles, in second
    k2 = [t_test_start - i for i in t2]  # standing time in second between irradiation and analysing

    try:
        if unit == 'h':
            k2 = [float(i) / 3600 for i in k2]  # exchange to unit in hour
            t3 = [float(i) for i in t3]
        elif unit == 'a':
            k2 = [i / (3600 * 24 * 365.242) for i in k2]  # exchange to unit in year
            t3 = [float(i) / (24 * 365) for i in t3]
        for i in range(len(t3)):
            iP = 1  # power
            v1.append(iP * (1 - exp(-f * t3[i])) / (f * exp(f * k2[i])))
            e11 = t3[i] * exp(-f * t3[i]) / (f * exp(f * k2[i]))
            e12 = (exp(-f * t3[i]) - 1) * (1 + f * k2[i]) * exp(f * k2[i]) / (f * exp(f * k2[i])) ** 2
            e1.append(iP * (e11 + e12))
            v2.append(iP * t3[i])
        k0 = sum(v2) / sum(v1)
        k1 = error_div((sum(v2), 0), (sum(v1), pow(sum(e1) ** 2 * sf ** 2, 0.5)))
        # other error calculation equation in CALC
        # It is calculated based on an assumption that only one irradiation exist with total duration of sum of t3,
        # and the end time is the last irradiation finish time
        k1 = pow(((sum(t3) * exp(f * k2[-1]) * (1 - exp(-f * sum(t3))) + f * sum(t3) * k2[-1] * exp(f * k2[-1]) * (
                1 - exp(-f * sum(t3))) - f * sum(t3) * exp(f * k2[-1]) * sum(t3) * exp(-f * sum(t3))) / (
                          1 - exp(-f * sum(t3))) ** 2) ** 2 * sf ** 2, 0.5)
    except Exception as e:
        print(traceback.format_exc())
        return 1, 0
    else:
        return k0, k1


def get_datetime(t_year: int, t_month: int, t_day: int, t_hour: int, t_min: int, t_seconds: int = 0, base=None):
    """
    :param t_year: int
    :param t_month: int
    :param t_day: int
    :param t_hour: int
    :param t_min: int
    :param t_seconds: int, default == 0
    :param base: base time [y, m, d, h, m]
    :return: seconds since 1970-1-1 8:00
    """
    t_year, t_month, t_day, t_hour, t_min, t_seconds = \
        int(t_year), int(t_month), int(t_day), int(t_hour), int(t_min), int(t_seconds)
    if base is None:
        base = [1970, 1, 1, 8, 0]
    base_year, base_mouth, base_day, base_hour, base_min = base
    if t_year % 4 == 0 and t_year % 100 != 0 or t_year % 400 == 0:
        days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    delta_seconds = ((((t_year - base_year) * 365 + ((t_year + 1 - base_year) - (t_year + 1 - base_year) % 4) / 4 +
                       sum(days[base_mouth - 1:t_month - 1]) + t_day - base_day) * 24 + t_hour - base_hour) * 60 +
                     t_min - base_min) * 60 + t_seconds
    return delta_seconds


'-------------------'
'--Age Calculation--'
'-------------------'


def calc_age(a0: float, e0: float, J: float, sJ: float, uf: int = 1, useMinEquation: bool = True,
             useDecayConst: bool = False, recalibrationPrimary: bool = False, usePrimaryAge: bool = False,
             usePrimaryRatio: bool = False, useStandardAge: bool = True, **kwargs):
    """
    :param a0: value of ar40r/ar39k
    :param e0: error of ar40r/ar39k
    :param J: irradiation params
    :param sJ: error of j in 1 sigma
    :param uf: error factor for ar40r/ar39k error, default = 1
    :param useMinEquation:
    :param useDecayConst:
    :param recalibrationPrimary:
    :param usePrimaryAge:
    :param usePrimaryRatio:
    :param useStandardAge:
    :return: age in Ma | analytical error | internal error | full external error
    """
    A = kwargs.pop('A', 31.58)
    sA = kwargs.pop('sA', 0.064)
    Ae = kwargs.pop('Ae', 3.310)  # 40K --> 40Ar
    sAe = kwargs.pop('sAe', 3.310 * 1.209 / 100)
    Ab = kwargs.pop('Ab', 28.270)  # 40K --> 40Ca
    sAb = kwargs.pop('sAb', 28.270 * 0.177 / 100)
    W = kwargs.pop('W', 39.09830)
    sW = kwargs.pop('sW', 39.09830 * 0.000154 / 100)
    Y = kwargs.pop('Y', 31556930)
    sY = kwargs.pop('sY', 0)
    f = kwargs.pop('f', 0.000117)
    sf = kwargs.pop('sf', 0.00000100035)
    No = kwargs.pop('No', 6.0221367E+23)  # avogadro_number
    sNo = kwargs.pop('sNo', 6.0221367E+23 * 0.000059 / 100)
    L = kwargs.pop('L', 5.46E-10)  # decay_constant_of_40K
    sL = kwargs.pop('sL', 5.46E-10 * 0.979 / 100)
    Le = kwargs.pop('Le', 0.000000000058)  # decay_constant_of_40K_EC
    sLe = kwargs.pop('sLe', 0.000000000058 * 1.207 / 100)  # decay_constant_of_40K_EC_error
    Lb = kwargs.pop('Lb', 0.000000000495)  # decay_constant_of_40K_betaN
    sLb = kwargs.pop('sLb', 0.000000000488 * 1.014 / 100)  # decay_constant_of_40K_betaN_error
    t = kwargs.pop('t', 0)  # standard_age
    st = kwargs.pop('st', 0 * 0 / 100)  # standard_age_error
    Ap = kwargs.pop('Ap', 0)  # standard_Ar_conc, p for Primary Standard
    sAp = kwargs.pop('sAp', 0 * 0.001 / 100)
    Kp = kwargs.pop('Kp', 0)  # standard_K_conc
    sKp = kwargs.pop('sKp', 7.597 * 0.03 / 100)
    KK = kwargs.pop('0', 0)  # standard_40K_K
    sKK = kwargs.pop('sKK', 0)

    if not is_number(J, sJ) or L == 0:
        return 0, 0, 0, 0

    e0 = e0 / uf  # change to 1 sigma
    k0, k1, k2, k3 = 0, 0, 0, 0

    if not useMinEquation:
        try:
            L = L * 1000000  # change to Ma
            sL = sL * 1000000  # change to Ma
            k0 = log(1 + J * a0) / L
            v1 = e0 ** 2 * (J / (L * (1 + J * a0))) ** 2
            v2 = sJ ** 2 * (a0 / (L * (1 + J * a0))) ** 2
            v3 = sL ** 2 * (log(1 + J * a0) / (L ** 2)) ** 2
            k1 = pow(v1, 0.5)  # analytical error
            k2 = pow(v1 + v2, 0.5)  # internal error
            k3 = pow(v1 + v2 + v3, 0.5)  # full external error
        except Exception as e:
            print(traceback.format_exc())
        finally:
            return k0, k1, k2, k3
    else:
        useDecayConst = False
        useStandardAge = True
        recalibrationPrimary = True

    if recalibrationPrimary:
        try:
            # recalculation using Min et al.(2000) equation
            # lmd = A * W * Y / (f * No)
            V = f * No / ((Ab + Ae) * W * Y)
            sf = 0  # the error of f was not considered by Koppers
            sV = pow((V / f * sf) ** 2 + (V / No * sNo) ** 2 + (V / (Ab + Ae)) ** 2 * (sAb ** 2 + sAe ** 2) +
                     (V / W * sW) ** 2 + (V / Y * sY) ** 2, 0.5)
            # standard age in year
            t = t * 1000000
            st = st * 1000000
            # back-calculating Ar40/Ar39 ration for the standard
            stdR = (exp(t * L) - 1) / J
            # errors of standard age and decay constants were not applied
            sStdR = pow((stdR / J) ** 2 * sJ ** 2, 0.5)
            # normalize the measured 40Ar/39Ar
            R = a0 / stdR
            sR_1 = error_div((a0, e0), (stdR, sStdR))  # errors of measured 40Ar/39Ar and J value
            sR_2 = error_div((a0, e0), (stdR, 0))  # error of measured 40Ar/39Ar only

            BB = 1
            KK = exp(t / V) - 1  # 40Arr / 40K Use standard age
            XX = BB * KK * R + 1
            k0 = V * log(XX)

            e1 = (log(XX) * V / f - V * BB * KK * R / (f * XX)) ** 2 * sf ** 2  # sFr
            e2 = (log(XX) * V / No) ** 2 * sNo ** 2  # sNo
            e3 = (-1 * log(XX) * V / A + BB * KK * R / (A * XX)) ** 2 * sAb ** 2  # sAb
            e4 = (-1 * log(XX) * V / A - Ab * KK * R / (Ae ** 2 * XX)) ** 2 * sAe ** 2  # sAe
            e5 = (-1 * log(XX) * V / W - V * BB * KK * R / (W * XX)) ** 2 * sW ** 2  # sW
            e6 = (log(XX) * V / Y) ** 2 * sY ** 2  # sY
            e7 = (V * BB * KK / XX) ** 2 * sR_1 ** 2  # sR
            # e8 = (V * BB * KK * R / (Ap * XX)) ** 2 * sAp ** 2  # sAp
            # e9 = (V * BB * KK * R / (Kp * XX)) ** 2 * sKp ** 2  # sKp
            e8, e9 = 0, 0
            if useDecayConst:  # k0 = log(L / Le * KK * R + 1) / L
                e1 = (V * BB * KK * R / (f * XX)) ** 2 * sf ** 2
                e2 = 0
                e3 = (-1 * log(XX) * V / L + BB * KK * R / (L * XX)) ** 2 * sLb ** 2
                e4 = (-1 * log(XX) * V / L - Lb * KK * R / (Le ** 2 * XX)) ** 2 * sLe ** 2
                e5 = (V * BB * KK * R / (W * XX)) ** 2 * sW ** 2
                e6 = 0
            if useStandardAge:
                e1, e9 = 0, 0
            k1 = pow((V * KK * R / (R * XX)) ** 2 * sR_2 ** 2, 0.5)  # analytical error, error of 40Ar/39Ar only
            k2 = pow((V * KK * R / (R * XX)) ** 2 * sR_1 ** 2, 0.5)  # internal error, errors of 40Ar/39Ar and J value
            k3 = pow(e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9, 0.5)  # total external error
            [k0, k1, k2, k3] = [i / 1000000 for i in [k0, k1, k2, k3]]  # change to Ma
            return k0, k1, k2, k3
        except Exception as e:
            print('Error in Using Min equation: {}, lines: {}'.format(e, e.__traceback__.tb_lineno))
            return calc_age(a0, e0, J, sJ, uf=uf, useMinEquation=False)
    return 0, 0, 0, 0


def err_wtd_mean(a0: list, e0: list, sf: int = 1, adjust_error: bool = True):
    """
    :param a0: x
    :param e0: error
    :param sf: sigma number for age error, default = 1
    :param adjust_error: adjust error by multiply Sqrt(MSWD)
    :return: error-weighted mean value | error in 1 sigma | number of data points | MSWD
    """
    e0 = [i / sf for i in e0]  # change error to 1 sigma
    n = len(a0)
    try:
        if n == 0:
            raise ValueError(f'Empty input')
        wt = [1 / i ** 2 if i != 0 else 999 for i in e0]  # error weighting
        k0 = sum([a0[i] * wt[i] for i in range(n)]) / sum(wt)  # error-weighted value
        k3 = sum([(a0[i] - k0) ** 2 * wt[i] for i in range(n)]) / (n - 1)  # MSWD mentioned in Min et al., 2000
        if adjust_error:
            k1 = pow(k3 / sum(wt), 0.5)  # error of mean age using equation mentioned by Min et al. (2000)
        else:
            k1 = pow(1 / sum(wt), 0.5)  # ArArCALC实际是利用加权平均计算总40r/39k，再计算年龄
        k2 = n
        k4 = k3 * (n - 1)
        k5 = distributions.chi2.sf(k4, n - 1)
        # k4, k5 = get_chi_square(a0, [k0] * n)
        # print(f'wtd_mean value: {k0} ± {k1}, dp = {k2}, MSWD = {k3}, Chi-square = {k4}, p-value = {k5}')
        return k0, k1, k2, k3, k4, k5
    except Exception:
        print(traceback.format_exc())
        return None, None, None, None


def wtd_york2_regression(x: list, sx: list, y: list, sy: list, ri: list, sf: int = 1, **kwargs):
    """
    :param x: isochron x-axis
    :param sx: standard error of x
    :param y: isochron y-axis, y = b + m * x
    :param sy: standard error of y
    :param ri: relative coefficient of errors of x and y
    :param sf: factor of error, default = 1, meaning inputted errors are in 1 sigma
    :return: Intercept | Error | slope | Error | MSWD | Convergence | Number of Iterations | error magnification | other
     b, sb, a, sa, mswd, dF, Di, k, r2, chi_square, p_value
    """
    conv_tol = kwargs.pop('convergence', 0.001)
    iter_num = kwargs.pop('iteration', 100)
    n = len(x)
    sx = [sXi / sf for sXi in sx]  # change to 1 sigma
    sy = [sYi / sf for sYi in sy]  # change to 1 sigma
    X, sX, Y, sY, R = list(x), list(sx), list(y), list(sy), list(ri)
    wX = [1 / sXi ** 2 if sXi != 0 else 1 for sXi in sX]  # Weights of X
    wY = [1 / sYi ** 2 if sYi != 0 else 1 for sYi in sY]  # Weights of Y
    Z = lambda m, b: list(map(lambda wXi, wYi, Ri:
                              (wXi * wYi) / (m ** 2 * wYi + wXi - 2 * m * Ri * (wXi * wYi) ** 0.5),
                              wX, wY, R))  # Weights of S
    mX = lambda m, b: sum(list(map(lambda Zi, Xi: Zi * Xi, Z(m, b), X))) / sum(Z(m, b))  # Weighted mean of X
    mY = lambda m, b: sum(list(map(lambda Zi, Yi: Zi * Yi, Z(m, b), Y))) / sum(Z(m, b))  # Weighted mean of Y
    # Equation to minimize
    S = lambda m, b: sum(list(map(lambda Zi, Yi, Xi: Zi * (Yi - m * Xi - b) ** 2, Z(m, b), Y, X)))
    # Slope by OLS is used as the initial values in weights calculation
    temp_lst = intercept_linest(y, x)
    if not temp_lst:
        return False
    b, seb, m, sem = temp_lst[0], temp_lst[1], temp_lst[5][0], temp_lst[6][0]
    b = mY(m, b) - m * mX(m, b)
    last_m = 1e10
    Di = 0  # Iteration number
    mswd, k = 1, 1  # Initial return values
    while abs(m - last_m) >= abs(m * conv_tol / 100):
        last_m = m
        U = list(map(lambda Xi: Xi - mX(m, b), X))
        V = list(map(lambda Yi: Yi - mY(m, b), Y))
        # Expression from York 2004, which differs to York 1969
        Up = list(map(lambda Zi, Vi, Ui, wXi, wYi, Ri:
                      Zi ** 2 * Vi * (Ui / wYi + m * Vi / wXi - Ri * (Vi + m * Ui) / (wXi * wYi) ** 0.5),
                      Z(m, b), V, U, wX, wY, R))
        Lo = list(map(lambda Zi, Vi, Ui, wXi, wYi, Ri:
                      Zi ** 2 * Ui * (Ui / wYi + m * Vi / wXi - Ri * (Vi + m * Ui) / (wXi * wYi) ** 0.5),
                      Z(m, b), V, U, wX, wY, R))
        m = sum(Up) / sum(Lo)  # New slope
        b = mY(m, b) - m * mX(m, b)  # From York 2004, calculate b again after final value of m has been obtained
        sumUUZ = sum(list(map(lambda Ui, Zi: Ui * Ui * Zi, U, Z(m, b))))
        sumXXZ = sum(list(map(lambda Xi, Zi: Xi * Xi * Zi, X, Z(m, b))))
        sem = pow(1 / sumUUZ, 0.5)
        seb = pow(sumXXZ / sum(Z(m, b)), 0.5) * sem
        mswd = S(m, b) / (n - 2)
        # print(f"York 2004 regression, m = {m}, b = {b}, S = {S(m, b)}, Di = {Di}")
        if mswd > 1:
            k = pow(mswd, 0.5)  # k为误差放大系数
        else:
            k = 1

        sem = sem * k
        seb = seb * k

        Di = Di + 1
        if Di >= iter_num:
            break

    # Calculate Y values base on the regression results
    estimate_y = [b + m * _x for _x in x]
    resid = [(estimate_y[i] - y[i]) ** 2 for i in range(len(y))]
    reg = [(i - sum(estimate_y) / len(estimate_y)) ** 2 for i in estimate_y]
    ssresid = sum(resid)  # residual sum of squares / sum squared residual
    ssreg = sum(reg)  # regression sum of square
    sstotal = ssreg + ssresid  # total sum of squares
    r2 = ssreg / sstotal if sstotal != 0 else 1  # r2 = ssreg / sstotal
    chi_square = mswd * (n - 2)
    p_value = distributions.chi2.sf(chi_square, n - 2)

    # average error of S
    err_s = lambda m, b: list(map(lambda Zi, Yi, Xi: (1 / Zi) ** 1./2. / abs(Yi - m * Xi - b), Z(m, b), Y, X))
    avg_err_s = sum(err_s(m, b)) / len(X) * 100

    # print('----------------------------------------------------------------')
    # print('截距>>>' + str(b) + '  ' + '误差>>>' + str(seb))
    # print('斜率>>>' + str(m) + '  ' + '误差>>>' + str(sem))
    # print('Absolute Convergence' + '>>>' + str(abs(m - last_m)))
    # print('Number of Iterations' + '>>>' + str(Di))
    # print('MSWD' + '>>>' + str(mswd))
    # print('Error Magnification>>>' + str(k))
    # print('----------------------------------------------------------------')

    return b, seb, m, sem, mswd, abs(m - last_m), Di, k, r2, chi_square, p_value, avg_err_s


def wtd_3D_regression(x: list, sx: list, y: list, sy: list, z: list, sz: list,
                      r1: list, r2: list, r3: list, sf: int = 1, **kwargs):
    """
    :param x: x-axis
    :param sx: standard error of x
    :param y: y-axis
    :param sy: standard error of y
    :param z: z-axis, z = ax + by + c
    :param sz: standard error of z
    :param r1: relative coefficient of errors of x and y
    :param r2: relative coefficient of errors of x and z
    :param r3: relative coefficient of errors of y and z
    :param sf: factor of error, default = 1, meaning inputted errors are in 1 sigma
    :return: c (interceept), sc, a, sa, b, sb, S, mswd, r2, abs(a - last_a), Di, k  # length == 12
    """
    conv_tol = kwargs.pop('convergence', 0.001)
    iter_num = kwargs.pop('iteration', 100)
    n = len(x)
    sx = [sXi / sf for sXi in sx]  # change to 1 sigma
    sy = [sYi / sf for sYi in sy]  # change to 1 sigma
    sz = [sZi / sf for sZi in sz]  # change to 1 sigma
    if n <= 3:
        return False
    Di = 0

    def getSumProduct(*args, factor=1):
        n = len(args[0])
        for arg in args:
            n = len(arg) if len(arg) < n else n
        res = []
        for i in range(n):
            temp = 1
            for arg in args:
                temp = temp * arg[i]
            res.append(temp * factor)
        return sum(res)

    # wX = list(map(lambda si: 1 / si ** 2, sx))
    # wY = list(map(lambda si: 1 / si ** 2, sy))
    # wZ = list(map(lambda si: 1 / si ** 2, sz))
    # Weights of S
    W = lambda a, b: list(map(lambda sXi, sYi, sZi, r1i, r2i, r3i: 1 / (
            a ** 2 * sXi ** 2 + b ** 2 * sYi ** 2 + sZi ** 2 +
            2 * a * b * r1i * sXi * sYi - 2 * a * r2i * sXi * sZi - 2 * b * r3i * sYi * sZi),
                              sx, sy, sz, r1, r2, r3))
    # Weighted mean values of X, Y, and Z, respectively
    mX = lambda a, b: sum(list(map(lambda Wi, xi: Wi * xi, W(a, b), x))) / sum(W(a, b))
    mY = lambda a, b: sum(list(map(lambda Wi, yi: Wi * yi, W(a, b), y))) / sum(W(a, b))
    mZ = lambda a, b: sum(list(map(lambda Wi, zi: Wi * zi, W(a, b), z))) / sum(W(a, b))
    # Minimizing this equation
    S = lambda a, b, c: sum([W(a, b)[i] * (a * x[i] + b * y[i] + c - z[i]) ** 2 for i in range(n)])
    # Calculate new c based on iterated a and b
    new_c = lambda a, b: mZ(a, b) - a * mX(a, b) - b * mY(a, b)
    # Initial values of a, b, and c from OLS
    linest_res = intercept_linest(z, x, y)
    c, sc, k2, k3, k4, [a, b], [sa, sb] = linest_res[0:7]
    c = new_c(a, b)
    k = 1  # Error magnification factor
    last_a = 1e10
    mswd, f = 1000, 0
    # print(f"初始值：a = {a}, b = {b}, c = {c}")
    # ar38ar36 = 0.1885
    # ar40ar36 = (a + b * ar38ar36) * -1 / c
    # print(f"Ar38/Ar36 = {ar38ar36}, Ar40/Ar36 = {ar40ar36}, S = {S(a, b, c)}")
    while abs(a - last_a) >= abs(a * conv_tol / 100):
        last_a = a
        U = list(map(lambda xi: xi - mX(a, b), x))
        V = list(map(lambda yi: yi - mY(a, b), y))
        G = list(map(lambda zi: zi - mZ(a, b), z))
        # P and Q are Xi - mX and Yi - mY, respectively. These values are obtained by weighted Orthogonal regression
        P = list(map(lambda Wi, Ui, Vi, Gi, sXi, sYi, sZi, r1i, r2i, r3i:
                     Wi * ((a * sXi ** 2 + b * r1i * sXi * sYi - r2i * sXi * sZi) * (Gi - b * Vi) + (
                             a * b * r1i * sXi * sYi + b ** 2 * sYi ** 2 - a * r2i * sXi * sZi - 2 * b * r3i * sYi * sZi + sZi ** 2) * Ui),
                     W(a, b), U, V, G, sx, sy, sz, r1, r2, r3))
        Q = list(map(lambda Wi, Ui, Vi, Gi, sXi, sYi, sZi, r1i, r2i, r3i:
                     Wi * ((b * sYi ** 2 + a * r1i * sXi * sYi - r3i * sYi * sZi) * (Gi - a * Ui) + (
                             a * b * r1i * sXi * sYi + a ** 2 * sXi ** 2 - b * r3i * sYi * sZi - 2 * a * r2i * sXi * sZi + sZi ** 2) * Vi),
                     W(a, b), U, V, G, sx, sy, sz, r1, r2, r3))
        # Up = getSumProduct(W(a, b), U, G) * getSumProduct(W(a, b), V, V) - getSumProduct(W(a, b), U, V) * getSumProduct(W(a, b), V, G)
        # Lo = getSumProduct(W(a, b), U, U) * getSumProduct(W(a, b), V, V) - getSumProduct(W(a, b), U, V) * getSumProduct(W(a, b), V, U)
        a_Up = getSumProduct(W(a, b), P, G) * getSumProduct(W(a, b), Q, V) - getSumProduct(W(a, b), P,
                                                                                           V) * getSumProduct(W(a, b),
                                                                                                              Q, G)
        a_Lo = getSumProduct(W(a, b), P, U) * getSumProduct(W(a, b), Q, V) - getSumProduct(W(a, b), P,
                                                                                           V) * getSumProduct(W(a, b),
                                                                                                              Q, U)
        new_a = a_Up / a_Lo
        # Up = getSumProduct(W(a, b), V, G) * getSumProduct(W(a, b), U, U) - getSumProduct(W(a, b), U, G) * getSumProduct(W(a, b), V, U)
        # Lo = getSumProduct(W(a, b), U, U) * getSumProduct(W(a, b), V, V) - getSumProduct(W(a, b), U, V) * getSumProduct(W(a, b), V, U)
        b_Up = getSumProduct(W(a, b), Q, G) * getSumProduct(W(a, b), P, U) - getSumProduct(W(a, b), P,
                                                                                           G) * getSumProduct(W(a, b),
                                                                                                              Q, U)
        b_Lo = getSumProduct(W(a, b), P, U) * getSumProduct(W(a, b), Q, V) - getSumProduct(W(a, b), P,
                                                                                           V) * getSumProduct(W(a, b),
                                                                                                              Q, U)
        new_b = b_Up / b_Lo

        # Standard errors
        mU = getSumProduct(W(a, b), U) / sum(W(a, b))
        mV = getSumProduct(W(a, b), V) / sum(W(a, b))
        mP = getSumProduct(W(a, b), P) / sum(W(a, b))
        mQ = getSumProduct(W(a, b), Q) / sum(W(a, b))

        D_PU = list(map(lambda Wi, sXi, sYi, sZi, r1i, r2i, r3i:
                        Wi * (
                                a * b * r1i * sXi * sYi + b ** 2 * sYi ** 2 - a * r2i * sXi * sZi - 2 * b * r3i * sYi * sZi + sZi ** 2),
                        W(a, b), sx, sy, sz, r1, r2, r3))
        D_QU = list(map(lambda Wi, sXi, sYi, sZi, r1i, r2i, r3i:
                        -1 * a * Wi * (b * sYi ** 2 + a * r1i * sXi * sYi - r3i * sYi * sZi),
                        W(a, b), sx, sy, sz, r1, r2, r3))
        D_PV = list(map(lambda Wi, sXi, sYi, sZi, r1i, r2i, r3i:
                        -1 * b * Wi * (a * sXi ** 2 + b * r1i * sXi * sYi - r2i * sXi * sZi),
                        W(a, b), sx, sy, sz, r1, r2, r3))
        D_QV = list(map(lambda Wi, sXi, sYi, sZi, r1i, r2i, r3i:
                        Wi * (
                                a * b * r1i * sXi * sYi + a ** 2 * sXi ** 2 - b * r3i * sYi * sZi - 2 * a * r2i * sXi * sZi + sZi ** 2),
                        W(a, b), sx, sy, sz, r1, r2, r3))
        D_PG = list(map(lambda Wi, sXi, sYi, sZi, r1i, r2i, r3i:
                        Wi * (a * sXi ** 2 + b * r1i * sXi * sYi - r2i * sXi * sZi),
                        W(a, b), sx, sy, sz, r1, r2, r3))
        D_QG = list(map(lambda Wi, sXi, sYi, sZi, r1i, r2i, r3i:
                        Wi * (b * sYi ** 2 + a * r1i * sXi * sYi - r3i * sYi * sZi),
                        W(a, b), sx, sy, sz, r1, r2, r3))
        D_UX = D_VY = D_GZ = [1 - Wi / sum(W(a, b)) for Wi in W(a, b)]

        D_Wa = list(map(lambda Wi, sXi, sYi, sZi, r1i, r2i, r3i:
                        -1 * Wi ** 2 * (2 * a * sXi ** 2 + 2 * b * r1i * sXi * sYi - 2 * r2i * sXi * sZi),
                        W(a, b), sx, sy, sz, r1, r2, r3))

        D_Wb = list(map(lambda Wi, sXi, sYi, sZi, r1i, r2i, r3i:
                        -1 * Wi ** 2 * (2 * b * sYi ** 2 + 2 * a * r1i * sXi * sYi - 2 * r3i * sYi * sZi),
                        W(a, b), sx, sy, sz, r1, r2, r3))

        D_aX = list(map(lambda Wi, D_UXi, D_QUi, D_PUi, Pi, Qi, Ui, Vi, Gi:
                        Wi * D_UXi * (a * (
                                getSumProduct(W(a, b), P, U) * Vi * D_QUi + getSumProduct(W(a, b), Q, V) * (
                                Ui * D_PUi + Pi) -
                                getSumProduct(W(a, b), Q, U) * Vi * D_PUi - getSumProduct(W(a, b), P, V) * (
                                        Ui * D_QUi + Qi)) -
                                      (getSumProduct(W(a, b), P, G) * Vi * D_QUi + getSumProduct(W(a, b), Q,
                                                                                                 V) * Gi * D_PUi) +
                                      (getSumProduct(W(a, b), Q, G) * Vi * D_PUi + getSumProduct(W(a, b), P,
                                                                                                 V) * Gi * D_QUi)),
                        W(a, b), D_UX, D_QU, D_PU, P, Q, U, V, G))

        D_aY = list(map(lambda Wi, D_VYi, D_QVi, D_PVi, Pi, Qi, Ui, Vi, Gi:
                        Wi * D_VYi * (a * (
                                getSumProduct(W(a, b), P, U) * (Qi + Vi * D_QVi) + getSumProduct(W(a, b), Q, V) * (
                                Ui * D_PVi) -
                                getSumProduct(W(a, b), Q, U) * (Pi + Vi * D_PVi) - getSumProduct(W(a, b), P, V) * (
                                        Ui * D_QVi)) -
                                      (getSumProduct(W(a, b), P, G) * (Qi + Vi * D_QVi) + getSumProduct(W(a, b), Q,
                                                                                                        V) * Gi * D_PVi) +
                                      (getSumProduct(W(a, b), Q, G) * (Pi + Vi * D_PVi) + getSumProduct(W(a, b), P,
                                                                                                        V) * Gi * D_QVi)),
                        W(a, b), D_VY, D_QV, D_PV, P, Q, U, V, G))

        D_aZ = list(map(lambda Wi, D_GZi, D_QGi, D_PGi, Pi, Qi, Ui, Vi, Gi:
                        Wi * D_GZi * (a * (
                                getSumProduct(W(a, b), P, U) * (Vi * D_QGi) + getSumProduct(W(a, b), Q, V) * (
                                Ui * D_PGi) -
                                getSumProduct(W(a, b), Q, U) * (Vi * D_PGi) - getSumProduct(W(a, b), P, V) * (
                                        Ui * D_QGi)) -
                                      (getSumProduct(W(a, b), P, G) * (Vi * D_QGi) + getSumProduct(W(a, b), Q, V) * (
                                              Pi + Gi * D_PGi)) +
                                      (getSumProduct(W(a, b), Q, G) * (Vi * D_PGi) + getSumProduct(W(a, b), P, V) * (
                                              Qi + Gi * D_QGi))),
                        W(a, b), D_GZ, D_QG, D_PG, P, Q, U, V, G))

        D_WPU_a = list(map(lambda Wi, D_Wai, Pi, Ui: D_Wai * Pi * Ui, W(a, b), D_Wa, P, U))
        D_WQV_a = list(map(lambda Wi, D_Wai, Qi, Vi: D_Wai * Qi * Vi, W(a, b), D_Wa, Q, V))
        D_WQU_a = list(map(lambda Wi, D_Wai, Qi, Ui: D_Wai * Qi * Ui, W(a, b), D_Wa, Q, U))
        D_WPV_a = list(map(lambda Wi, D_Wai, Pi, Vi: D_Wai * Pi * Vi, W(a, b), D_Wa, P, V))
        D_WPG_a = list(map(lambda Wi, D_Wai, Pi, Gi: D_Wai * Pi * Gi, W(a, b), D_Wa, P, G))
        D_WQG_a = list(map(lambda Wi, D_Wai, Qi, Gi: D_Wai * Qi * Gi, W(a, b), D_Wa, Q, G))

        D_aa = a_Lo + a * (
                sum(D_WPU_a) * sum(list(map(lambda Wi, Qi, Vi: Wi * Qi * Vi, W(a, b), Q, V))) +
                sum(D_WQV_a) * sum(list(map(lambda Wi, Pi, Ui: Wi * Pi * Ui, W(a, b), P, U))) -
                sum(D_WQU_a) * sum(list(map(lambda Wi, Pi, Vi: Wi * Pi * Vi, W(a, b), P, V))) -
                sum(D_WPV_a) * sum(list(map(lambda Wi, Qi, Ui: Wi * Qi * Ui, W(a, b), Q, U)))
        ) - (
                       sum(D_WPG_a) * sum(list(map(lambda Wi, Qi, Vi: Wi * Qi * Vi, W(a, b), Q, V))) +
                       sum(D_WQV_a) * sum(list(map(lambda Wi, Pi, Gi: Wi * Pi * Gi, W(a, b), P, G))) -
                       sum(D_WQG_a) * sum(list(map(lambda Wi, Pi, Vi: Wi * Pi * Vi, W(a, b), P, V))) -
                       sum(D_WPV_a) * sum(list(map(lambda Wi, Qi, Gi: Wi * Qi * Gi, W(a, b), Q, G)))
               )

        D_bX = list(map(lambda Wi, D_UXi, D_QUi, D_PUi, Pi, Qi, Ui, Vi, Gi:
                        Wi * D_UXi * (b * (
                                getSumProduct(W(a, b), P, U) * (Vi * D_QUi) + getSumProduct(W(a, b), Q, V) * (
                                Pi + Ui * D_PUi) -
                                getSumProduct(W(a, b), Q, U) * (Vi * D_PUi) - getSumProduct(W(a, b), P, V) * (
                                        Qi + Ui * D_QUi)) -
                                      (getSumProduct(W(a, b), Q, G) * (Pi + Ui * D_PUi) + getSumProduct(W(a, b), P,
                                                                                                        U) * Gi * D_QUi) +
                                      (getSumProduct(W(a, b), P, G) * (Qi + Ui * D_QUi) + getSumProduct(W(a, b), Q,
                                                                                                        U) * Gi * D_PUi)),
                        W(a, b), D_UX, D_QU, D_PU, P, Q, U, V, G))

        D_bY = list(map(lambda Wi, D_VYi, D_QVi, D_PVi, Pi, Qi, Ui, Vi, Gi:
                        Wi * D_VYi * (b * (
                                getSumProduct(W(a, b), P, U) * (Qi + Vi * D_QVi) + getSumProduct(W(a, b), Q, V) * (
                                Ui * D_PVi) -
                                getSumProduct(W(a, b), Q, U) * (Pi + Vi * D_PVi) - getSumProduct(W(a, b), P, V) * (
                                        Ui * D_QVi)) -
                                      (getSumProduct(W(a, b), Q, G) * (Ui * D_PVi) + getSumProduct(W(a, b), P, U) * (
                                              Gi * D_QVi)) +
                                      (getSumProduct(W(a, b), P, G) * (Ui * D_QVi) + getSumProduct(W(a, b), Q, U) * (
                                              Gi * D_PVi))),
                        W(a, b), D_VY, D_QV, D_PV, P, Q, U, V, G))

        D_bZ = list(map(lambda Wi, D_GZi, D_QGi, D_PGi, Pi, Qi, Ui, Vi, Gi:
                        Wi * D_GZi * (b * (
                                getSumProduct(W(a, b), P, U) * (Vi * D_QGi) + getSumProduct(W(a, b), Q, V) * (
                                Ui * D_PGi) -
                                getSumProduct(W(a, b), Q, U) * (Vi * D_PGi) - getSumProduct(W(a, b), P, V) * (
                                        Ui * D_QGi)) -
                                      (getSumProduct(W(a, b), Q, G) * (Ui * D_PGi) + getSumProduct(W(a, b), P, U) * (
                                              Qi + Gi * D_QGi)) +
                                      (getSumProduct(W(a, b), P, G) * (Ui * D_QGi) + getSumProduct(W(a, b), Q, U) * (
                                              Pi + Gi * D_PGi))),
                        W(a, b), D_GZ, D_QG, D_PG, P, Q, U, V, G))

        D_WPU_b = list(map(lambda Wi, D_Wbi, Pi, Ui: D_Wbi * Pi * Ui, W(a, b), D_Wb, P, U))
        D_WQV_b = list(map(lambda Wi, D_Wbi, Qi, Vi: D_Wbi * Qi * Vi, W(a, b), D_Wb, Q, V))
        D_WQU_b = list(map(lambda Wi, D_Wbi, Qi, Ui: D_Wbi * Qi * Ui, W(a, b), D_Wb, Q, U))
        D_WPV_b = list(map(lambda Wi, D_Wbi, Pi, Vi: D_Wbi * Pi * Vi, W(a, b), D_Wb, P, V))
        D_WPG_b = list(map(lambda Wi, D_Wbi, Pi, Gi: D_Wbi * Pi * Gi, W(a, b), D_Wb, P, G))
        D_WQG_b = list(map(lambda Wi, D_Wbi, Qi, Gi: D_Wbi * Qi * Gi, W(a, b), D_Wb, Q, G))

        D_bb = b_Lo + b * (
                sum(D_WPU_b) * sum(list(map(lambda Wi, Qi, Vi: Wi * Qi * Vi, W(a, b), Q, V))) +
                sum(D_WQV_b) * sum(list(map(lambda Wi, Pi, Ui: Wi * Pi * Ui, W(a, b), P, U))) -
                sum(D_WQU_b) * sum(list(map(lambda Wi, Pi, Vi: Wi * Pi * Vi, W(a, b), P, V))) -
                sum(D_WPV_b) * sum(list(map(lambda Wi, Qi, Ui: Wi * Qi * Ui, W(a, b), Q, U)))
        ) - (
                       sum(D_WQG_b) * sum(list(map(lambda Wi, Pi, Ui: Wi * Pi * Ui, W(a, b), P, U))) +
                       sum(D_WPU_b) * sum(list(map(lambda Wi, Qi, Gi: Wi * Qi * Gi, W(a, b), Q, G))) -
                       sum(D_WPG_b) * sum(list(map(lambda Wi, Qi, Ui: Wi * Qi * Ui, W(a, b), Q, U))) -
                       sum(D_WQU_b) * sum(list(map(lambda Wi, Pi, Gi: Wi * Pi * Gi, W(a, b), P, G)))
               )

        Va = sum(list(map(lambda D_Xi, sXi, D_Yi, sYi, D_Zi, sZi, r1i, r2i, r3i:
                          D_Xi ** 2 * sXi ** 2 + D_Yi ** 2 * sYi ** 2 + D_Zi ** 2 * sZi ** 2 +
                          2 * r1i * sXi * sYi * D_Xi * D_Yi + 2 * r2i * sXi * sZi * D_Xi * D_Zi + 2 * r3i * sYi * sZi * D_Yi * D_Zi,
                          D_aX, sx, D_aY, sy, D_aZ, sz, r1, r2, r3)))
        Vb = sum(list(map(lambda D_Xi, sXi, D_Yi, sYi, D_Zi, sZi, r1i, r2i, r3i:
                          D_Xi ** 2 * sXi ** 2 + D_Yi ** 2 * sYi ** 2 + D_Zi ** 2 * sZi ** 2 +
                          2 * r1i * sXi * sYi * D_Xi * D_Yi + 2 * r2i * sXi * sZi * D_Xi * D_Zi + 2 * r3i * sYi * sZi * D_Yi * D_Zi,
                          D_bX, sx, D_bY, sy, D_bZ, sz, r1, r2, r3)))

        D_cX = list(map(lambda Wi, D_aXi, D_bXi:
                        - 1 * a * Wi / sum(W(a, b)) + (-1 * D_aXi) * (2 * mP - 2 * mU + mX(a, b)) + (-1 * D_bXi) * (
                                2 * mQ - 2 * mV + mY(a, b)),
                        W(a, b), D_aX, D_bX))
        D_cY = list(map(lambda Wi, D_aYi, D_bYi:
                        - 1 * b * Wi / sum(W(a, b)) + (-1 * D_aYi) * (2 * mP - 2 * mU + mX(a, b)) + (-1 * D_bYi) * (
                                2 * mQ - 2 * mV + mY(a, b)),
                        W(a, b), D_aY, D_bY))
        D_cZ = list(map(lambda Wi, D_aZi, D_bZi:
                        Wi / sum(W(a, b)) + (-1 * D_aZi) * (2 * mP - 2 * mU) + (-1 * D_bZi) * (2 * mQ - 2 * mV),
                        W(a, b), D_aZ, D_bZ))
        Vc = sum(list(map(lambda D_cXi, D_cYi, D_cZi, sxi, syi, szi, r1i, r2i, r3i:
                          D_cXi ** 2 * sxi ** 2 + D_cYi ** 2 * syi ** 2 + D_cZi ** 2 * szi ** 2 +
                          2 * r1i * sxi * syi * D_cXi * D_cYi + 2 * r2i * sxi * szi * D_cXi * D_cZi + 2 * r3i * syi * szi * D_cYi * D_cZi,
                          D_cX, D_cY, D_cZ, sx, sy, sz, r1, r2, r3)))

        sa = (Va / D_aa) ** 0.5
        sb = (Vb / D_bb) ** 0.5
        sc = Vc ** 0.5

        mswd = S(a, b, c) / (n - 3)
        if mswd > 1:
            k = pow(mswd, 0.5)  # k为误差放大系数
        else:
            k = 1

        sa, sb, sc = sa * k, sb * k, sc * k

        a = new_a
        b = new_b
        c = new_c(new_a, new_b)

        # ar40ar36 = (a + b * ar38ar36) * -1 / c
        # f = 1 / c
        # print(f"new_a = {a}, new_b = {b}, new_c = {c}, S = {S(a, b, c)}, MSWD = {mswd}, Ar38/Ar36 = {ar38ar36}, Ar40/Ar36 = {ar40ar36}")
        #
        # print(f"Iteration info: a = {a:.4f} ± {sa:.4f} | {sa/a * 100:.2f}%, b = {b:.4f} ± {sb:.4f} | {sb/b * 100:.2f}%, c = {c:.4f} ± {sc:.4f} | {sc/c * 100:.2f}% "
        #       f"S = {S(a, b, c)}， Di = {Di}, MSWD = {mswd}")

        Di = Di + 1
        if Di >= iter_num:
            break

    estimate_z = list(map(lambda xi, yi: c + a * xi + b * yi, x, y))
    resid = list(map(lambda zi, Zi: (zi - Zi) ** 2, estimate_z, z))
    reg = [(i - sum(estimate_z) / len(estimate_z)) ** 2 for i in estimate_z]
    ssresid = sum(resid)  # residual sum of squares / sum squared residual
    ssreg = sum(reg)  # regression sum of square
    sstotal = ssreg + ssresid  # total sum of squares
    R = ssreg / sstotal if sstotal != 0 else 1  # r2 = ssreg / sstotal
    chi_square = mswd * (n - 3)
    p_value = distributions.chi2.sf(chi_square, n - 3)

    # relative error of S
    err_s = lambda a, b, c: [(1 / W(a, b)[i]) ** 1./2. / abs(a * x[i] + b * y[i] + c - z[i]) for i in range(n)]
    avg_err_s = sum(err_s(a, b, c)) / len(x) * 100
    print(f"Average relative error of S = {avg_err_s}%")

    # print(f"a = {a}, b = {b}, c = {c}, S = {S(a, b, c)}， Di = {Di}, MSWD = {mswd}, r2 = {R}")

    return c, sc, a, sa, b, sb, S(a, b, c), mswd, R, abs(a - last_a), Di, k, chi_square, p_value, avg_err_s


def error_cor(sX: float, sY: float, sZ: float):
    """
    calculate correlation coefficient of errors.
    :param sX: relative error of X, where X/Z vs. Y/Z
    :param sY: relative error of Y
    :param sZ: relative error of Z
    :return:
    """
    if sZ == 0:
        return 1
    k = pow(1 / ((1 + sX ** 2 / sZ ** 2) * (1 + sY ** 2 / sZ ** 2)), 0.5)
    return k


'---------------------------'
'--Extrapolation Functions--'
'---------------------------'


def intercept_average(a0: list, a1=None):
    """
    :param a0: known_y's
    :param a1:
    :return: intercept | standard error | relative error | r2 | MSWD | other params | errors of other params |
             euqation | m_ssresid
    """
    if a1 is None:
        a1 = []
    k0 = sum(a0) / len(a0)

    # calculate Y values base on the fitted formula
    estimate_y = [k0 for x in a0]
    resid = [(x - k0) ** 2 for x in a0]
    reg = [(i - sum(estimate_y) / len(estimate_y)) ** 2 for i in estimate_y]
    ssresid = sum(resid)  # residual sum of squares / sum squared residual
    ssreg = sum(reg)  # regression sum of square
    sstotal = ssreg + ssresid  # total sum of squares
    df = len(a0) - 1  # df = degree of freedom
    m_ssresid = ssresid / df
    r2 = ssreg / sstotal if sstotal != 0 else 1  # r2 = ssreg / sstotal

    k1 = pow(sum([(i - k0) ** 2 for i in a0]) / df, 0.5)  # standard deviation
    k2 = k1 / k0 * 100 if k0 != 0 else 0  # relative standard error
    k3 = r2  # determination coefficient
    k4 = 'MSWD'
    k5 = []
    k6 = []
    k8 = m_ssresid

    def get_adjusted_y(x: list):
        return [k0] * len(x)

    k7 = get_adjusted_y

    return k0, k1, k2, k3, k4, k5, k6, k7, k8


def intercept_weighted_least_squares(a0: list, a1: list):
    """
    :param a0: known_y's
    :param a1: known_x's
    :return: intercept | standard error | relative error | R2 | [m] | [sem]
    """
    """
    y = m * x + b, 
    """
    linest_res = intercept_linest(a0, a1)
    b0, seb0, rseb0, r2, mswd, [m0], [rem0] = linest_res[0:7]
    y0 = list(map(lambda i: m0 * i + b0, a1))
    resid = list(map(lambda i, j: i - j, y0, a0))
    weight = list(map(lambda i: 1 / i ** 2, resid))  # Use weighting by inverse of the squares of residual

    sum_wi = sum(weight)
    sum_wiyi = sum(list(map(lambda i, j: i * j, weight, a0)))
    sum_wixi = sum(list(map(lambda i, j: i * j, weight, a1)))
    sum_wiyixi = sum(list(map(lambda i, j, g: i * j * g, weight, a0, a1)))
    sum_wixixi = sum(list(map(lambda i, j, g: i * j * g, weight, a1, a1)))

    m = (sum_wiyixi - sum_wixi * sum_wiyi / sum_wi) / (sum_wixixi - sum_wixi * sum_wixi / sum_wi)
    b = (sum_wiyi - m * sum_wixi) / sum_wi
    a0 = list(map(lambda i, j: i * j, weight, a0))
    a1 = list(map(lambda i, j: i * j, weight, a1))
    linest_res = intercept_linest(a0, a1, weight=weight)
    b, seb, rseb, r2, mswd, [m], [sem] = linest_res[0:7]
    return b, seb, rseb, r2, [m], [sem]


def intercept_linest(a0: list, a1: list, *args, weight: list = None, interceptIsZero: bool = False):
    """
    :param a0: known_y's, y = b + m * x
    :param a1: known_x's
    :param args: more known_x's
    :param weight: necessary when weighted least squares fitting
    :param interceptIsZero: set b as zero, y = m * x
    :return: intercept | standard error | relative error | R2 | MSWD | other params: list |
             error of other params: list | equation | m_ssresid (y估计值的标准误差)
    """
    if interceptIsZero:
        if len(a0) != len(a1) or len(args) > 0:
            return False
        try:
            df = len(a0) - 1
            m = sum(list(map(lambda x, y: x * y, a1, a0))) / sum(list(map(lambda x: x ** 2, a1)))
            SSresid = sum(list(map(lambda x, y: y - x * m, a1, a0)))
            sey = pow(SSresid / df, 0.5)
            SSreg = sum(list(map(lambda x: (x * m) ** 2, a1)))
            SStotal = SSreg + SSresid
            R2 = SStotal / SSreg
            sem = pow(SSresid / df * 1 / sum(list(map(lambda x: x ** 2, a1))), 0.5)
            return m, sem, R2
        except Exception:
            return False
    # beta = (xTx)^-1 * xTy >>> xtx * beta = xty
    # crate matrix of x and y, calculate the transpose of x
    m = len(a1)  # number of data
    n = len(args) + 2  # number of unknown x, constant is seen as x^0
    if m - n < 1 or len(a0) != len(a1):
        return False
    if weight is not None:
        xlst = [weight, a1, *args]
    else:
        xlst = [[1] * m, a1, *args]
    ylst = a0
    xtx = list()
    xty = list()
    for i in range(n):
        xtx.append([])
        xty.append([])
        xty[i] = sum([xlst[i][k] * ylst[k] for k in range(m)])
        for j in range(n):
            xtx[i].append([])
            xtx[i][j] = sum([xlst[i][k] * xlst[j][k] for k in range(m)])
    # solve the system of linear equations using LU factorization algorithm
    # LU * beta = xty, U * beta = b, L * b = xty
    l: List[List[Any]] = list()
    u: List[List[Any]] = list()
    b: List[Any] = list()
    beta: List[Any] = list()
    for i in range(n):
        l.append([])
        u.append([])
        b.append([])
        beta.append([])
        for j in range(n):
            l[i].append([])
            u[i].append([])
            if j > i:
                l[i][j] = 0
            elif i > j:
                u[i][j] = 0
            else:
                l[i][j] = 1
    for i in range(n):
        if i >= 1:
            l[i][0] = xtx[i][0] / u[0][0]
        for j in range(n):
            if i == 0:
                u[i][j] = xtx[i][j]
            elif i == 1 and j >= 1:
                u[i][j] = xtx[i][j] - l[i][0] * u[0][j]
            elif i < n - 1:
                if j in range(1, i):
                    l[i][j] = (xtx[i][j] - sum([l[i][r] * u[r][j] for r in range(j)])) / u[j][j]
                if j in range(i, n):
                    u[i][j] = xtx[i][j] - sum([l[i][r] * u[r][j] for r in range(i)])
            elif i == n - 1:
                if j in range(1, i):
                    l[n - 1][j] = (xtx[n - 1][j] - sum([l[n - 1][r] * u[r][j] for r in range(j)])) / u[j][j]
                if j == n - 1:
                    u[i][j] = xtx[i][j] - sum([l[i][r] * u[r][j] for r in range(i)])
    # calculate matrix b, L * b = y
    b[0] = xty[0]
    for i in range(1, n):
        b[i] = xty[i] - sum([l[i][j] * b[j] for j in range(i)])
    # calculate matrix beta, b = U * beta
    beta[n - 1] = b[n - 1] / u[n - 1][n - 1]
    for i in [n - k for k in range(2, n + 1)]:
        beta[i] = (b[i] - sum([u[i][j] * beta[j] for j in range(i + 1, n)])) / u[i][i]

    # calculate the inverse of matrix xTx
    inv_l: List[List[Any]] = list()
    inv_u: List[List[Any]] = list()
    for i in range(n):
        inv_l.append([])
        inv_u.append([])
        for j in range(n):
            inv_l[i].append([])
            inv_u[i].append([])
            if i == j:
                inv_l[i][j] = 1 / l[i][j]
                inv_u[i][j] = 1 / u[i][j]
            elif i > j:
                inv_u[i][j] = 0
            elif j > i:
                inv_l[i][j] = 0

    for j in range(1, n):
        for i in range(n - 1):
            if i + j > n - 1:
                break
            else:
                inv_u[i][i + j] = -1 * sum([u[i][k] * inv_u[k][i + j] for k in range(i + 1, i + j + 1)]) / u[i][i]
            if i + j > n - 1:
                break
            else:
                inv_l[i + j][i] = -1 * sum([l[i + j][k] * inv_l[k][i] for k in range(i, i + j)]) / l[i + j][i + j]

    # inv_xTx = inv_u * inv_l
    inv_xtx: List[List[Any]] = list()
    for i in range(n):
        inv_xtx.append([])
        for j in range(n):
            inv_xtx[i].append([])
            inv_xtx[i][j] = sum([inv_u[i][k] * inv_l[k][j] for k in range(n)])
    # pow(inv_xtx[0][0], 0.5) is the errF in Excel Linest function

    # calculate Y values base on the fitted formula
    estimate_y = [sum([xlst[j][i] * beta[j] for j in range(n)]) for i in range(m)]
    resid = [(estimate_y[i] - a0[i]) ** 2 for i in range(m)]
    reg = [(i - sum(estimate_y) / len(estimate_y)) ** 2 for i in estimate_y]
    ssresid = sum(resid)  # residual sum of squares / sum squared residual
    ssreg = sum(reg)  # regression sum of square
    sstotal = ssreg + ssresid  # total sum of squares
    df = m - n + 1 - 1  # df = degree of freedom
    m_ssresid = ssresid / df
    se_beta = [pow(m_ssresid * inv_xtx[i][i], 0.5) for i in range(n)]
    rseb = (se_beta[0] / beta[0]) * 100 if beta[0] != 0 else se_beta[0]  # relative error of intercept
    r2 = ssreg / sstotal if sstotal != 0 else 1  # r2 = ssreg / sstotal

    def get_adjusted_y(*args):
        args = [[1] * len(args[0]), *args]
        return [sum([beta[i] * args[i][j] for i in range(len(beta))]) for j in range(len(args[0]))]

    return beta[0], se_beta[0], rseb, r2, 'mswd', beta[1:], se_beta[1:], get_adjusted_y, m_ssresid


def intercept_quadratic(a0: list, a1: list):
    """
    :param a0: known_y's, y = b + m1 * x + m2 * x ^ 2
    :param a1: known_x's
    :return: intercept | standard error | relative error | r2 | MSWD | [m1, m2] | [sem1, sem2], equation
    """
    # y = b + m1 * x + m2 * x ^ 2
    k = list(intercept_linest(a0, a1, [i ** 2 for i in a1]))
    b, seb, rseb, r2, mswd, [m1, m2], [sem1, sem2] = k[0:7]

    def get_adjusted_y(x: list):
        return [b + m1 * _x + m2 * _x ** 2 for _x in x]

    k[7] = get_adjusted_y

    return k


def intercept_polynomial(a0: list, a1: list, degree: int = 5):
    """
    :param a0: known_y's, y = b + m1 * x + m2 * x ^ 2
    :param a1: known_x's
    :param degree: the order of the fitting, default = 5
    :return: intercept | standard error | relative error | r2 | MSWD | [m1, m2] | [sem1, sem2], equation
    """
    # y = b + m1 * x + m2 * x ^ 2 + ... + m[n] * x ^ n
    k = list(intercept_linest(a0, *[[j ** (i + 1) for j in a1] for i in range(degree)]))
    b, seb, rseb, r2, mswd, m, sem = k[0:7]

    def get_adjusted_y(x: list):
        return [b + sum([m[i] * _x ** (i + 1) for i in range(degree)]) for _x in x]

    k[7] = get_adjusted_y

    return k


def intercept_logest(a0: list, a1: list):
    """
    :param a0: known_y's, y = b * m ^ x
    :param a1: known_x's
    :return: intercept | standard error | relative error | R2 | MSWD | m | sem
    """
    # y = b * m ^ x, Microsoft Excel LOGEST function, ln(y) = ln(b) + ln(m) * x
    a0 = [log(i) for i in a0]  # ln(y)
    linest_res = intercept_linest(a0, a1)
    b, seb, rseb, r2, mswd, [lnm], [selnm] = linest_res[0:7]
    b = exp(b)
    m = exp(lnm)
    sem = exp(lnm) * selnm
    seb = b * seb  # Excel.Logest function do not consider the error propagation
    rseb = seb / b * 100
    return b, seb, rseb, r2, mswd, m, sem


def intercept_power(a0: list, a1: list):
    """
    :param a0: known_y's, y = a * x ^ b + c
    :param a1: known_x's
    :return: intercept | standard error of intercept | relative error | R2 | MSWD | [a, b, c] | [sem, sec, seb]
    """

    def _pow_func(x, a, b, c):
        return a * x ** b + c

    def _solve_pow(params):
        a, b, c = params
        x, y = [0, 0, 0], [0, 0, 0]
        x[0] = sum(a1[:3]) / 3
        y[0] = sum(a0[:3]) / 3
        x[1] = sum(a1) / len(a1)
        y[1] = sum(a0) / len(a0)
        x[2] = sum(a1[-3:]) / 3
        y[2] = sum(a0[-3:]) / 3
        return np.array([
            _pow_func(x[0], a, b, c) - y[0],
            _pow_func(x[1], a, b, c) - y[1],
            _pow_func(x[2], a, b, c) - y[2],
        ])

    def _get_sum(a, b, c):
        y_predicted = [_pow_func(_x, a, b, c) for _x in a1]
        return sum([(y_predicted[i] - a0[i]) ** 2 for i in range(len(a0))])

    def _get_abc(b):  # Return a, b, c given b based on linest regression
        f = intercept_linest(a0, [_x ** b for _x in a1])
        return f[5][0], b, f[0]

    try:
        a, b, c = fsolve(func=_solve_pow, x0=np.array([1, 1, 1]))  # initial estimate
        count = 0
        step = 0.01
        while count < 100:
            a, b, c = _get_abc(b)
            s = _get_sum(a, b, c)
            b_left, b_right = b - step * b, b + step * b
            s_left = _get_sum(*_get_abc(b_left))
            s_right = _get_sum(*_get_abc(b_right))
            if s_left > s > s_right:
                b = b_right
                continue
            elif s_left < s < s_right:
                b = b_left
                continue
            elif s_left < s_right:
                b = (b + b_left) / 2
            else:
                b = (b + b_right) / 2
            step = step * 0.5
            count += 1
            if step < 0.000001:
                break
    except RuntimeError:
        return 'RuntimeError', 'None', 'None', 'None', 'None', 'None', 'None', \
               lambda x: [_pow_func(i, a, b, c) for i in x], 'None'
    except TypeError or IndexError:
        return 'NotEnoughPoints', 'None', 'None', 'None', 'None', 'None', 'None', \
               lambda x: [_pow_func(i, a, b, c) for i in x], 'None'

    f = intercept_linest(a0, [_x ** b for _x in a1])
    a, sea, c, sec = f[5][0], f[6][0], f[0], f[1]

    calculated_y = [_pow_func(i, a, b, c) for i in a1]
    resid = [(calculated_y[i] - a0[i]) ** 2 for i in range(len(a0))]
    reg = [(i - sum(calculated_y) / len(calculated_y)) ** 2 for i in calculated_y]
    ssresid = sum(resid)
    ssreg = sum(reg)
    sstotal = ssreg + ssresid
    df = len(a0) - 1
    m_ssresid = ssresid / df
    r2 = ssreg / sstotal if sstotal != 0 else 1

    intercept = c
    se_intercept_1 = sec
    dp = len(a1)  # data points
    z = [i ** b for i in a1]
    # calculate error of intercept
    errfz = pow(sum([i ** 2 for i in z]) / (dp * sum([i ** 2 for i in z]) - sum(z) ** 2), 0.5)
    errfx = pow(sum([i ** 2 for i in a1]) / (dp * sum([i ** 2 for i in a1]) - sum(a1) ** 2), 0.5)
    # seb = errfz * sey = errfz * ssresid / df -> se_intercept = sey * errfx = seb / errfz * errfx
    se_intercept = sec / errfz * errfx
    rse_intercept = se_intercept / intercept * 100

    return intercept, se_intercept, rse_intercept, r2, 'mswd', [a, b, c], 'se', \
           lambda x: [_pow_func(i, a, b, c) for i in x], m_ssresid


def intercept_exponential(a0: list, a1: list):
    """
    :param a0: known_y's, y = a * b ^ x + c
    :param a1: known_x's
    :return: intercept | standard error of intercept | relative error | R2 | MSWD | [m, c, b] | [sem, sec, seb]
    """

    def _exp_func(x, a, b, c):
        return a * b ** x + c

    def _solve_exp(params):
        a, b, c = params
        x, y = [0, 0, 0], [0, 0, 0]
        x[0] = sum(a1[:3]) / 3
        y[0] = sum(a0[:3]) / 3
        x[1] = sum(a1) / len(a1)
        y[1] = sum(a0) / len(a0)
        x[2] = sum(a1[-3:]) / 3
        y[2] = sum(a0[-3:]) / 3
        return np.array([
            _exp_func(x[0], a, b, c) - y[0],
            _exp_func(x[1], a, b, c) - y[1],
            _exp_func(x[2], a, b, c) - y[2],
        ])

    def _get_sum(a, b, c):
        y_predicted = [_exp_func(_x, a, b, c) for _x in a1]
        return sum([(y_predicted[i] - a0[i]) ** 2 for i in range(len(a0))])

    def _get_ac(b):
        f = intercept_linest(a0, [b ** _x for _x in a1])
        return f[5][0], b, f[0]

    try:
        a, b, c = fsolve(_solve_exp, np.array([1, 1, 1]))
        count = 0
        step = 0.01
        while count < 100:
            a, b, c = _get_ac(b)
            s = _get_sum(a, b, c)
            b_left, b_right = b - step * b, b + step * b
            s_left = _get_sum(*_get_ac(b_left))
            s_right = _get_sum(*_get_ac(b_right))
            if s_left > s > s_right:
                b = b_right
                continue
            elif s_left < s < s_right:
                b = b_left
                continue
            elif s_left < s_right:
                b = (b + b_left) / 2
            else:
                b = (b + b_right) / 2
            count += 1
            step = step * 0.5
            if step < 0.000001:
                break
    except RuntimeError:
        return 'RuntimeError', 'None', 'None', 'None', 'None', 'None', 'None', \
               lambda x: [_exp_func(i, a, b, c) for i in x], 'None'
    except TypeError or IndexError:
        return 'NotEnoughPoints', 'None', 'None', 'None', 'None', 'None', 'None', \
               lambda x: [_exp_func(i, a, b, c) for i in x], 'None'

    f = intercept_linest(a0, [b ** _x for _x in a1])
    a, sea, c, sec = f[5][0], f[6][0], f[0], f[1]

    calculated_y = [_exp_func(i, a, b, c) for i in a1]
    resid = [(calculated_y[i] - a0[i]) ** 2 for i in range(len(a0))]
    reg = [(i - sum(calculated_y) / len(calculated_y)) ** 2 for i in calculated_y]
    ssresid = sum(resid)
    ssreg = sum(reg)
    sstotal = ssreg + ssresid
    dp = len(a1)
    df = dp - 1
    m_ssresid = ssresid / df
    r2 = ssreg / sstotal if sstotal != 0 else 1

    z = [b ** i for i in a1]
    intercept = a + c
    se_intercept_1 = np.sqrt(sea ** 2 + sec ** 2)
    # calculate error of intercept
    errfz = pow(sum([i ** 2 for i in z]) / (dp * sum([i ** 2 for i in z]) - sum(z) ** 2), 0.5)
    errfx = pow(sum([i ** 2 for i in a1]) / (dp * sum([i ** 2 for i in a1]) - sum(a1) ** 2), 0.5)
    # seb = errfz * sey = errfz * ssresid / df -> se_intercept = sey * errfx = seb / errfz * errfx
    se_intercept = sec / errfz * errfx
    rse_intercept = se_intercept / intercept * 100

    if abs(intercept) > 10 * max(a0):
        return 'BadFitting', 'None', 'None', 'None', 'None', 'None', 'None', \
               lambda x: [_exp_func(i, a, b, c) for i in x], 'None'
    if intercept < 0:
        return 'Negative', 'None', 'None', 'None', 'None', 'None', 'None', \
               lambda x: [_exp_func(i, a, b, c) for i in x], 'None'

    return intercept, se_intercept, rse_intercept, r2, 'mswd', [a, b, c], 'se', \
           lambda x: [_exp_func(i, a, b, c) for i in x], m_ssresid


def intercept_Cl_correlation(y: list, x1: list, x2: list, Q: list, **kwargs):
    def _get_new_Q(_x2: list, _y: list, _r1: float, _r2: float, _f: float, _Q: list):
        return [(_r1 * _x2[i] + _r2 * _f - _r2 * _y[i]) * _Q[i] for i in range(np)]

    conv_tol = kwargs.pop('convergence', 0.001)
    iter_num = kwargs.pop('iteration', 100)

    np = len(y)
    r2 = 0.1885  # Ar38/Ar36 trapped
    # Start values
    r1 = 298.56  # Ar40/Ar36 trapped
    p = -262.8  # Cl36/Cl38 productivity
    f = 50  # Ar40r/Ar39K
    Di = 0
    delta_r1 = 10000

    while abs(delta_r1) >= abs(r1 * conv_tol / 100):
        # print(f'Iteration Num: {Di}, r1: {r1}, P: {p}, r2: {r2}, f: {f}')
        new_Q = _get_new_Q(x2, y, r1, r2, f, Q)
        res = intercept_linest(y, x1, new_Q)
        f = res[0]
        new_r1, p = res[5][0:2]
        delta_r1 = abs(new_r1 - r1)
        r1 = new_r1
        # new_r2 = [(y[i] - p * Q[i] * r1 * x2[i] - r1 * x1[i] - f) / (y[i] - f) for i in range(np)]
        # print(', '.join([str(i) for i in new_r2]))
        # r2 = sum(new_r2) / len(new_r2)
        Di += 1
        if Di >= iter_num:
            break
    # print(f'Regression Results: r1: {r1}, P: {p}, r2: {r2}, f: {f}')
    return r1, p, r2, f


'---------------------'
'----List Function----'
'---------------------'


def list_mul(a: list, e: list, f: list, sf: list, isRelative: bool = True):
    if isRelative:
        sf = [sf[i] * f[i] / 100 for i in range(len(sf))]
    k1 = [error_mul((a[i], e[i]), (f[i], sf[i])) for i in range(len(a))]
    k0 = [a[i] * f[i] for i in range(len(a))]
    return [k0, k1]


def list_rcpl(a: list, e: list, isRelative: bool = True):
    if isRelative:
        e = [item * a[i] / 100 for i, item in enumerate(e)]
    res = [[1 / i if i != 0 else 0 for i in a],
           [error_div((1, 0), (a[i], item)) if a[i] != 0 else 0 for i, item in enumerate(e)]]
    return res


def list_sub(a0: list, e0: list, a1: list, e1: list):
    k1 = [error_add(e0[i], e1[i]) for i in range(len(a0))]
    k0 = [a0[i] - a1[i] for i in range(len(a0))]
    return [k0, k1]


def list_merge(*args):
    res = []
    for i in args:
        res = res + i
    return res


'---------------------'
'--Error Propagation--'
'---------------------'


def error_add(*args: float):
    """
    :param args: errors in 1 sigma
    :return: propagated error
    """
    k = pow(sum([i ** 2 for i in args]), 0.5)
    return k


def error_mul(*args: tuple):
    """
    :param args: tuple of the value and its error
    :return: propagated error
    """
    e = []
    for i in range(len(args)):
        temp = 1
        for j in range(len(args)):
            if i != j:
                temp = temp * args[j][0]
        e.append(temp ** 2 * args[i][1] ** 2)
    k = pow(sum(e), 0.5)
    return k


def error_div(a0: tuple, a1: tuple):
    """
    :param a0: a tuple of the first number and its error
    :param a1: a tuple of another number and its error
    :return: propagated error
    """
    k = pow((-1 * a0[0] / a1[0] ** 2) ** 2 * a1[1] ** 2 + (1 / a1[0]) ** 2 * a0[1] ** 2, 0.5)
    return k


def error_pow(a0: tuple, a1: tuple):
    """
    :param a0: y = pow(a0, a1) -> y = a0 ^ a1
    :param a1:
    :return: propagated error
    """
    p1 = a0[1] ** 2 * (a1[0] * pow(a0[0], (a1[0] - 1))) ** 2
    p2 = a1[1] ** 2 * (pow(a0[0], a1[0]) * log(a0[0])) ** 2
    k = pow(p1 + p2, 0.5)
    return k


def error_log(a0: float, e0: float):
    """
    :param a0: y = ln(a0).
    :param e0: error in 1 sigma.
    :return: propagated error.
    """
    k = pow(e0 ** 2 * (1 / a0) ** 2, 0.5)
    return k


'---------------------'
'--Statistical Tools--'
'---------------------'


def get_MSWD():
    pass


def get_chi_square(f_obs, f_exp):
    # print(f_obs)
    # print(f_exp)
    # data points
    dp = min([len(f_obs), len(f_exp)])
    # chi-squared value
    chi = sum(list(map(lambda i: (f_obs[i] - f_exp[i]) ** 2 / f_exp[i], list(range(dp)))))
    # freedom degree
    df = dp - 1
    # p value
    p = distributions.chi2.sf(chi, df)
    return chi, p

# print(distributions.chi2.sf(0.703759706579149 * 6, 6))

# print(get_chi_square([8, 10, 12, 11, 7], [10, 10, 10, 10, 10]))

'---------------------'
'--Close Temperature--'
'---------------------'


def get_close_temp():
    return


'----------------'
'--Get Plot Data--'
'----------------'


def get_spectra(age: list, sage: list, Ar39k_list: list, f: int = 1):
    """
    :param age:
    :param sage: 1 sigma
    :param Ar39k_list:
    :param f:
    :return: x, y1, y2
    """
    sum_39Ark = sum(Ar39k_list)
    x, y1, y2 = [], [], []
    n = min(len(age), len(sage), len(Ar39k_list))
    for i, j in zip(age, sage):
        if isinstance(i, str) or isinstance(j, str):
            return False
    k1 = [age[i] + sage[i] * f for i in range(n)]  # upper
    k2 = [age[i] - sage[i] * f for i in range(n)]  # lower
    k4 = [float(i / sum_39Ark) for i in Ar39k_list]
    k3 = [sum(k4[:i + 1]) for i in range(n)]
    for i in range(n + 1):
        if i == 0:
            x.append(0)
            y1.append(k1[i])
            y2.append(k2[i])
        elif i < n:
            x.append(k3[i - 1])
            x.append(k3[i - 1])
            if i % 2 == 1:
                y1.append(k1[i - 1])
                y1.append(k2[i])
                y2.append(k2[i - 1])
                y2.append(k1[i])
            elif i % 2 == 0:
                y2.append(k1[i - 1])
                y2.append(k2[i])
                y1.append(k2[i - 1])
                y1.append(k1[i])
        elif i == n:
            x.append(1)
            if i % 2 == 1:
                y1.append(k1[i - 1])
                y2.append(k2[i - 1])
            elif i % 2 == 0:
                y2.append(k1[i - 1])
                y1.append(k2[i - 1])
        else:
            pass
    x = [x[i] * 100 for i in range(n * 2)]
    return x, y1, y2


def get_release_pattern():
    return


def get_diffusion_model():
    return

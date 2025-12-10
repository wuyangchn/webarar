import traceback
import numpy as np
import pandas as pd
from scipy.stats import distributions
from scipy.optimize import fsolve, curve_fit
from scipy.optimize import minimize
import matplotlib.pyplot as plt


def linest(a0: list, a1: list, *args):
    """
    Parameters
    ----------
    a0 : known_y's, y = b + m * x
    a1 : known_x's
    args : more known_x's

    Returns
    -------
    intercept | standard error | relative error | R2 | MSWD | other params: list |
             error of other params: list | equation | m_ssresid (y估计值的标准误差)

    """
    # beta = (xTx)^-1 * xTy >>> xtx * beta = xty
    # crate matrix of x and y, calculate the transpose of x
    if not args:
        x = np.concatenate(([[1]*len(a1)], [a1]), axis=0).transpose()
    else:
        x = np.concatenate(([[1]*len(a1)], [a1], args), axis=0).transpose()
    n = x.shape[-1]  # number of unknown x, constant is seen as x^0
    m = x.shape[0]  # number of data
    y = np.array([a0]).transpose()
    try:
        inv_xtx = np.linalg.inv(np.matmul(x.transpose(), x))
    except np.linalg.LinAlgError:
        raise np.linalg.LinAlgError(f"The determinant of the given matrix must not be zero ")
    beta = np.matmul(inv_xtx, np.matmul(x.transpose(), y))

    # calculate Y values base on the fitted formula
    estimate_y = np.matmul(x, beta)
    resid = (estimate_y - y) ** 2
    reg = (estimate_y - np.mean(y)) ** 2
    ssresid = resid.sum()  # 残差平方和
    ssreg = reg.sum()  # 回归平方和
    sstotal = ((y - np.mean(y)) ** 2).sum()
    df = m - n
    m_ssresid = ssresid / df  # 均方残差，与加权平均中的MSWD对应
    se_beta = (m_ssresid * np.diagonal(inv_xtx)) ** .5
    beta = beta.transpose()[0]
    rse_beta = se_beta / beta
    r2 = ssreg / sstotal if sstotal != 0 else np.inf

    def get_adjusted_y(*args):
        args = [[1] * len(args[0]), *args]
        return [sum([beta[i] * args[i][j] for i in range(len(beta))]) for j in range(len(args[0]))]

    return beta[0], se_beta[0], rse_beta[0] * 100, r2, m_ssresid, beta, se_beta, get_adjusted_y, m_ssresid


def exponential_2(a0: list, a1: list):

    def _exp_func(x, a, b, c):
        return a * np.exp(b * x) + c

    def _get_abc(b):  # Return a, b, c given b based on linest regression
        f = linest(a0, [np.exp(b * xi) for xi in a1])
        return f[5][1], b, f[0]

    @np.vectorize
    def _get_s(b):
        a, b, c = _get_abc(b)
        reg_y = [_exp_func(xi, a, b, c) for xi in a1]
        resid = [(reg_y[i] - a0[i]) ** 2 for i in range(len(a0))]
        ssresid = sum(resid)
        print(f"{a = }, {b = }, {c = }, {ssresid = }")
        return ssresid


    ini_f = linest(np.log(np.array(a0)), np.array(a1))
    ini_b = ini_f[5][1]

    print(f"{ini_b = }")

    bs = np.linspace(-1, 1, 500)
    ss = _get_s(bs)

    return bs, ss


X=[
26.2363146,
36.2553146,
46.2748146,
56.2979855,
66.3179855,
76.3374855,
86.3569855,
96.3769855,
106.3964855,
116.4185342,
126.4375342,
136.4584258,
146.4774258,
156.4964258,
166.5159258,
176.5409529,
186.5599529,
196.5814675,
206.6009675,
216.6204675,
226.6434336,
236.6634336,
246.6829336,
256.7019336,
266.7209336,
276.7404336,
286.765847,
296.784847,
306.8044075,
316.8244075,
326.8439075,
336.8629075,
346.8824075,
356.9019075,
366.9209075,
376.9404075,
386.9604075,
396.9851775,
]

Y=[
39.14941713,
39.18820511,
39.20586245,
39.20051082,
39.21817153,
39.22924604,
39.24986104,
39.25462422,
39.26069122,
39.25921195,
39.24602027,
39.23486851,
39.21989717,
39.20474297,
39.20924474,
39.16635925,
39.15363093,
39.12467004,
39.09512589,
39.07111879,
39.02333185,
39.00796447,
38.95826921,
38.92382854,
38.86003374,
38.82162987,
38.76763549,
38.71484786,
38.67839326,
38.60435577,
38.55484075,
38.48663544,
38.41643776,
38.34590528,
38.29368235,
38.20179052,
38.14125195,
38.05595975,
]


x = np.concatenate(([[1]*len(X)], [X]), axis=0).transpose()
y = np.array([Y]).transpose()
# n = x.shape[-1]  # number of unknown x, constant is seen as x^0
# m = x.shape[0]  # number of data
# inv_xtx = np.linalg.inv(np.matmul(x.transpose(), x))
# beta = np.matmul(inv_xtx, np.matmul(x.transpose(), y))
# estimate_y = np.matmul(x, beta)
# resid = (estimate_y - y) ** 2
# reg = (estimate_y - np.mean(y)) ** 2
# ssresid = resid.sum()  # 残差平方和
# ssreg = reg.sum()  # 回归平方和
# sstotal = ((y - np.mean(y)) ** 2).sum()
# df = m - n
# m_ssresid = ssresid / df  # 均方残差，与加权平均中的MSWD对应
# cov_beta = m_ssresid * inv_xtx
# se_beta = (m_ssresid * np.diagonal(inv_xtx)) ** .5
# beta = beta.transpose()[0]
# rse_beta = se_beta / beta
# r2 = ssreg / sstotal if sstotal != 0 else np.inf
#
# print(inv_xtx)
# print(beta)
# print(cov_beta)
# print(m_ssresid * (-sum(X)/(m * sum(np.array(X) ** 2) - sum(X)**2)))



bs, ss = exponential_2(Y, X)
#print(bs)
#print(ss)
plt.title(f"Exponential y=a*exp(b*x)+c: b vs. SSresid")
plt.plot(bs, ss)
plt.legend()
plt.show()


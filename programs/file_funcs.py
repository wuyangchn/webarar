"""
操作读取的excel文件
"""
import pickle
import traceback

from math import exp
from xlwt import Workbook as write_workbook
from xlrd import open_workbook, biffh
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.chartsheet import Chartsheet
from xlsxwriter.exceptions import FileCreateError
import os
import sys
import msoffcrypto

from re import findall
from programs import calc_funcs, basic_funcs, samples, styles, smp_funcs

try:
    from webarar.settings import SETTINGS_ROOT
except ModuleNotFoundError:
    SETTINGS_ROOT = ""


def get_post_file(file, media_dir):
    try:
        name, suffix = os.path.splitext(file.name)
        if suffix not in ['.xls', '.age', '.xlsx', '.arr', '.jpg', '.png', '.txt', '.log', '.seq', '.json', '.ahd']:
            raise TypeError("Wrong File")
        web_file_path = os.path.join(media_dir, file.name)
        with open(web_file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        print("File path on the server: %s" % web_file_path)
    except PermissionError:
        raise ValueError(f'Permission denied')
    except (Exception, BaseException) as e:
        print(traceback.format_exc())
        raise ValueError(f'Error in opening file: {e}')
    else:
        return web_file_path, name, suffix


def open_arr_file(filepath, samplename: str = ''):
    """
    file_path: full path of input file
    name： samplename
    return sample instance
    """
    try:
        with open(filepath, 'rb') as f:
            sample = pickle.load(f)
    except (Exception, BaseException):
        raise ValueError(f"Fail to open arr file: {filepath}")
    # Check arr version
    # Attention: recalculation will not be applied automatically
    sample = check_arr_version(sample)
    smp_funcs.update_table_data(sample)
    return sample


def open_age_xls(filepath: str, samplename: str = ''):
    """
    :param filepath:
    :param samplename:
    :return:
    """
    book_contents = read_calc_file(filepath)
    if not book_contents:
        raise ValueError('Fail to open the file')
    logs03 = book_contents['Logs03']
    calc_version = logs03[3][0]
    if calc_version not in ['25.2', '24.0']:
        raise ValueError(f'non-supported version: {calc_version}')
    data = book_contents['Data Tables']
    logs01 = book_contents['Logs01']
    logs02 = book_contents['Logs02']
    start_row = 5  # start_row --> 起始行号
    rows_num = len(data[1][start_row:]) - data[1][start_row:].count('')
    # print(f"Version: {calc_version}, Sequences: {rows_num}")
    if calc_version == '25.2':
        # rows_unm --> 样品阶段数
        sequence_name_index = [1]
        sequence_value_index = [2]
        sample_values_index = [16, 17, 21, 22, 26, 27, 31, 32, 36, 37]
        blank_values_index = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        corrected_values_index = [188, 189, 190, 191, 192, 193, 194, 195, 196, 197]
        degas_values_index = [138, 139, 140, 141, 142, 143, 144, 145,  # 36 a, c, ca, cl    0-9
                              146, 147,  # 37 ca    10-11
                              156, 157, 148, 149, 150, 151, 152, 153, 154, 155,  # 38 cl, a, c, k, ca   12-21
                              158, 159, 160, 161,  # 39 k, ca    22-25
                              162, 163, 164, 165, 166, 167, 168, 169]  # 40 r, a, c, k    26-33
        publish_values_index = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
        apparent_age_index = [198, 199, 200, 201, -999, -999, 202, 203]  # f, sf, ages, s, s, s, 40Arr%, 39Ar%
        isochron_values_index = [
            116, 117, 118, 119, 122,  # normal isochron
            -1, 127, 128, 129, 130, 133,  # inverse
            -1, -999, -999, -999, -999, -999,  # 39/38 vs 40/38
            -1, -999, -999, -999, -999, -999,  # 39/40 vs 39/40
            -1, -999, -999, -999, -999, -999,  # 38/39 vs 40/39
            -1, -999, -999, -999, -999, -999, -999]  # 3D isochron, 36/39, 38/39, 40/39
        isochron_mark_index = [115]
        total_param_index = [
            71, 72, 73, 74, 75, 76, 77, 78, 79, 80,  # 0-9
            81, 82, 83, 84, 85, 86, 87, 88, 89, 90,  # 10-19
            91, 92, 93, 94, 95, 96, -999, -999, 63, -999,  # 20-29
            -999, -999, -1, -1, -999, -999, -999, -999, -999, -999,  # 30-39
            -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 40-49
            -999, -999, -999, -999, -999, -999, -999, -999, 67, 49,  # 50-59
            50, -999, -999, -999, -999, -999, -999, 51, 52, 53,  # 60-69
            54, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 70-79
            -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 80-89
            -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 90-99
            -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 100-109
            -999, -999, -999, -999, -1,  # 110-114
        ]
    elif calc_version == '24.0':
        sequence_name_index = [1]
        sequence_value_index = [2]
        sample_values_index = [16, 17, 21, 22, 26, 27, 31, 32, 36, 37]
        blank_values_index = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        corrected_values_index = [-999, -999, -999, -999, -999, -999, -999, -999, -999, -999]
        degas_values_index = [136, -999, 137, -999, 139, -999, 138, -999,  # 36 a, c, ca, cl
                              140, -999,  # 37 ca,
                              145, -999, 141, -999, 142, -999, 143, -999, 144, -999,  # 38 cl, a, c, k, ca,
                              146, -999, 147, -999,  # 39 k, ca
                              148, -999, 149, -999, 150, -999, 151, -999]  # 40 r, a, c, k
        publish_values_index = [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        apparent_age_index = [156, 157, 104, 105, -999, -999, 106, 107]  # f, sf, ages, s, s, s, 39Ar%
        isochron_values_index = [
            114, 115, 116, 117, 120,  # normal isochron
            -1, 125, 126, 127, 128, 131,  # inverse
            -1, -999, -999, -999, -999, -999,  # 39/38 vs 40/38
            -1, -999, -999, -999, -999, -999,  # 39/40 vs 39/40
            -1, -999, -999, -999, -999, -999,  # 38/39 vs 40/39
            -1, -999, -999, -999, -999, -999, -999, -999, -999, -999]  # 3D isochron, 36/39, 38/39, 40/39, r1, r2, r3
        isochron_mark_index = [113]
        total_param_index = [
            69, 70, 71, 72, 73, 74, 75, 76, 77, 78,  # 0-9
            79, 80, 81, 82, 83, 84, 85, 86, 87, 88,  # 10-19
            89, 90, 91, 92, 93, 94, -999, -999, 63, -999,  # 20-29
            -999, -999, -1, -1, -999, -999, -999, -999, -999, -999,  # 30-39
            -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 40-49
            -999, -999, -999, -999, -999, -999, -999, -999, 65, 49,  # 50-59
            50, -999, -999, -999, -999, -999, -999, 51, 52, 53,  # 60-69
            54, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 70-79
            -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 80-89
            -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 90-99
            -999, -999, -999, -999, -999, -999, -999, -999, -999, -999,  # 100-99909
            -999, -999, -999, -999, -1,  # 110-114
        ]
    else:
        raise ValueError('.age version error!')

    # 2倍误差改回1倍
    for i in range(len(data)):
        if data[i][2] in ['2s', '%2s', '± 2s']:
            for j in range(rows_num):
                try:
                    data[i][start_row + j] = data[i][start_row + j] / 2
                except TypeError:
                    continue
    # degas相对误差改为绝对误差
    for i in degas_values_index + corrected_values_index:
        try:
            if data[i][2] in ['%1s', '%2s']:
                for j in range(rows_num):
                    try:
                        data[i][start_row + j] = data[i][start_row + j] * data[i - 1][start_row + j] / 100
                    except TypeError:
                        continue
        except IndexError:
            continue

    sample_values = basic_funcs.getPartialArry(data, start_row, rows_num, *sample_values_index)
    blank_values = basic_funcs.getPartialArry(data, start_row, rows_num, *blank_values_index)
    corrected_values = basic_funcs.getPartialArry(data, start_row, rows_num, *corrected_values_index)
    degas_values = basic_funcs.getPartialArry(data, start_row, rows_num, *degas_values_index)
    publish_values = basic_funcs.getPartialArry(data, start_row, rows_num, *publish_values_index)
    apparent_age_values = basic_funcs.getPartialArry(data, start_row, rows_num, *apparent_age_index)
    isochron_values = basic_funcs.getPartialArry(data, start_row, rows_num, *isochron_values_index)
    total_param = basic_funcs.getPartialArry(data, start_row, rows_num, *total_param_index)
    isochron_mark = basic_funcs.getPartialArry(data, start_row, rows_num, *isochron_mark_index)
    sequence_name = basic_funcs.getPartialArry(data, start_row, rows_num, *sequence_name_index)
    sequence_value = basic_funcs.getPartialArry(data, start_row, rows_num, *sequence_value_index)

    # 处理辐照时间
    month_convert = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    irradiation_index = logs02[1].index(data[63][5])
    irradiation_info = logs02[32][irradiation_index]
    irradiation_info_list = irradiation_info.split('\n')
    duration_hour = []
    end_time_second = []
    irradiation_end_time = []
    last_time = []
    for each_date in irradiation_info_list:
        if '/' in each_date:
            _year = each_date.split(' ')[1].split('/')[2]
            _month = each_date.split(' ')[1].split('/')[1].capitalize()
            if _month in month_convert.keys():
                _month = month_convert[_month]
            _day = each_date.split(' ')[1].split('/')[0]
            _hour = each_date.split(' ')[2].split('.')[0]
            _min = each_date.split(' ')[2].split('.')[1]
            end_time_second.append(calc_funcs.get_datetime(
                t_year=int(_year), t_month=int(_month), t_day=int(_day),
                t_hour=int(_hour), t_min=int(_min)))
            each_duration_hour = each_date.split(' ')[0].split('.')[0]
            each_duration_min = each_date.split(' ')[0].split('.')[1]
            each_duration = int(each_duration_hour) + round(int(each_duration_min) / 60, 2)
            duration_hour.append(each_duration)
            irradiation_end_time.append(f"{_year}-{_month}-{_day}-{_hour}-{_min}D{each_duration}")
            last_time = [_year, _month, _day, _hour, _min]

    experiment_start_time = []
    for i in basic_funcs.getTransposed(basic_funcs.getPartialArry(data, start_row, rows_num, *[59, 58, 57, 60, 61])):
        _year = str(i[0]) if '.' not in str(i[0]) else str(i[0]).split('.')[0]
        _month = str(month_convert[str(i[1]).capitalize()]) if str(i[1]).capitalize() in month_convert.keys() else str(
            i[1]).capitalize()
        _day = str(i[2]) if '.' not in str(i[2]) else str(i[2]).split('.')[0]
        _hour = str(i[3]) if '.' not in str(i[3]) else str(i[3]).split('.')[0]
        _min = str(i[4]) if '.' not in str(i[4]) else str(i[4]).split('.')[0]
        experiment_start_time.append([_year, _month, _day, _hour, _min])
    np = len(total_param[0])
    total_param[26] = [len(irradiation_end_time)] * np
    total_param[27] = ['S'.join(irradiation_end_time)] * np
    total_param[29] = [sum(duration_hour)] * np
    total_param[30] = ['-'.join(last_time)] * np
    total_param[31] = ['-'.join(i) for i in experiment_start_time]

    stand_time_second = [
        calc_funcs.get_datetime(*experiment_start_time[i]) - calc_funcs.get_datetime(*last_time) for i in range(np)]
    total_param[32] = [i / (3600 * 24 * 365.242) for i in stand_time_second]  # stand year

    # 补充、整理、调整数据
    if calc_version == '25.2':
        total_param[83] = [logs01[1][9]] * np  # No
        total_param[84] = [logs01[1][10]] * np  # %SD
        total_param[81] = [logs01[1][11]] * np  # K mass
        total_param[82] = [logs01[1][12]] * np  # K mass %SD

        total_param[85] = [logs01[1][13]] * np  # How many seconds in a year
        total_param[86] = [0] * np  # %SD

        total_param[87] = [logs01[1][14]] * np  # The constant of 40K/K
        total_param[88] = [logs01[1][15]] * np  # %SD

        total_param[89] = [logs01[1][16]] * np  # The constant of 35Cl/37Cl
        total_param[90] = [logs01[1][17]] * np  # %SD
        total_param[56] = [logs01[1][18]] * np  # The constant of 36/38Cl productivity
        total_param[57] = [logs01[1][19]] * np  # %SD
        total_param[91] = [logs01[1][24]] * np  # The constant of HCl/Cl
        total_param[92] = [logs01[1][25]] * np  # %SD

        total_param[50] = [logs01[1][26]] * np  # 40K(EC) activities param
        total_param[51] = [logs01[1][27]] * np  # %SD
        total_param[52] = [logs01[1][28]] * np  # 40K(\beta-) activities param
        total_param[53] = [logs01[1][29]] * np  # %SD
        total_param[48] = [logs01[1][26] + logs01[1][28]] * np  # 40K(EC) activities param
        total_param[49] = [calc_funcs.error_add(logs01[1][27] / 100 * logs01[1][26],
                                                logs01[1][29] / 100 * logs01[1][28]) / (total_param[48][0]) * 100 if
                           total_param[48][0] != 0 else 0] * np  # %SD

        total_param[34] = [logs01[1][36]] * np  # decay constant of 40K total
        total_param[35] = [logs01[1][37]] * np  # %SD
        total_param[36] = [logs01[1][30]] * np  # decay constant of 40K EC
        total_param[37] = [logs01[1][31]] * np  # %SD
        total_param[38] = [logs01[1][32]] * np  # decay constant of 40K \beta-
        total_param[39] = [logs01[1][33]] * np  # %SD
        total_param[40] = [0] * np  # decay constant of 40K \beta+
        total_param[41] = [0] * np  # %SD
        total_param[46] = [logs01[1][34]] * np  # decay constant of 36Cl
        total_param[47] = [logs01[1][35]] * np  # %SD
        total_param[42] = [logs01[1][38]] * np  # decay constant of 39Ar
        total_param[43] = [logs01[1][39]] * np  # %SD
        total_param[44] = [logs01[1][40]] * np  # decay constant of 37Ar
        total_param[45] = [logs01[1][41]] * np  # %SD

        # logs01[1][49]]  # 1 for using weighted YORK isochron regression, 2 for unweighted
        # logs01[1][50]]  # True for including errors on irradiation constants, False for excluding those
        # [logs01[1][67]]  # MDF method, 'LIN'
        total_param[93] = [logs01[1][70]] * np  # 40Ar/36Ar air
        total_param[94] = [logs01[1][71]] * np  # %SD

        total_param[97] = ['York-2'] * np  # Fitting method
        total_param[98] = [logs01[1][0]] * np  # Convergence
        total_param[99] = [logs01[1][1]] * np  # Iterations number
        total_param[100] = [logs01[1][67]] * np  # MDF method
        total_param[101] = [logs01[1][65]] * np  # force negative to zero when correct blank
        total_param[102] = [True] * np  # Apply 37Ar decay
        total_param[103] = [True] * np  # Apply 39Ar decay
        total_param[104] = [logs01[1][6]] * np  # Apply 37Ar decay
        total_param[105] = [logs01[1][7]] * np  # Apply 39Ar decay
        total_param[106] = [True] * np  # Apply K degas
        total_param[107] = [True] * np  # Apply Ca degas
        total_param[108] = [True] * np  # Apply Air degas
        total_param[109] = [logs01[1][8]] * np  # Apply Cl degas

        total_param[110] = [True if logs01[1][
                                        5] == 'MIN' else False] * np  # Calculating ages using Min equation [True] or conventional equation [False]
        total_param[111] = [logs01[1][89]] * np  # Use primary standard or not
        total_param[112] = [logs01[1][91]] * np  # Use standard age or not
        total_param[113] = [logs01[1][92]] * np  # Use primary ratio or not

        sample_info = {
            'sample': {'name': samplename or data[44][5], 'material': data[45][5], 'location': 'LOCATION'},
            'researcher': {'name': data[64][5]},
            'laboratory': {'name': logs01[1][44], 'info': '\n'.join([logs01[1][45], logs01[1][46], logs01[1][47]]),
                           'analyst': data[47][5]}
        }
    else:
        total_param[44] = [logs01[1][40]] * np
        total_param[45] = [logs01[1][41]] * np
        total_param[42] = [logs01[1][38]] * np
        total_param[43] = [logs01[1][39]] * np
        total_param[34] = [logs01[1][36]] * np
        total_param[35] = [logs01[1][37]] * np

        sample_info = {
            'sample': {'name': samplename or data[44][5], 'material': data[46][5], 'location': 'LOCATION'},
            'researcher': {'name': data[65][5]},
            'laboratory': {'name': logs01[1][44], 'info': '\n'.join([logs01[1][45], logs01[1][46], logs01[1][47]]),
                           'analyst': data[48][5]}
        }

        # For 24.0 version calc file, no errors
        def _set_list_zero(*index):
            for i in index:
                degas_values[i] = [0] * len(degas_values[i])

        _set_list_zero(*[i * 2 + 1 for i in range(0, int(len(degas_values) / 2 - 1))])

    # Change K/Ca to Ca/K
    if data[108][2] == 'K/Ca' and calc_version == '24.0' or data[110][2] == 'K/Ca' and calc_version == '24.0':
        publish_values[9] = [1 / i if calc_funcs.is_number(i) else None for i in publish_values[10]]
        publish_values[10] = [calc_funcs.error_div((1, 0), (publish_values[9][i], publish_values[10][i]))
                              if calc_funcs.is_number(publish_values[9][i], publish_values[10][i]) and
                                 publish_values[9][i] != 0 else None
                              for i in range(len(publish_values[9]))]

    isochron_mark = [1 if i == 4 else '' for i in isochron_mark]

    res = [sample_values, blank_values, corrected_values, degas_values, publish_values, apparent_age_values,
           isochron_values, total_param, sample_info, isochron_mark, sequence_name, sequence_value]

    return create_sample_from_calc(content=res)


def open_full_xls(filepath: str, samplename: str = ''):
    """
    filepath: absolute full path of input file
    return sample instance
    """
    try:
        res = open_xls(filepath)
    except (Exception, BaseException) as e:
        return e
    start_row = 5
    rows_num = len(res['Sample Parameters']) - 5
    for key, val in res.items():
        res[key] = basic_funcs.getTransposed(val[:start_row + rows_num])
        # 2倍误差改回1倍
        for i in range(len(res[key])):
            if res[key][i][2] in ['2s', '%2s', '± 2s']:
                _temp = []
                for j in range(rows_num):
                    try:
                        _temp.append(res[key][i][start_row + j] / 2)
                    except TypeError:
                        _temp.append('')
                res[key][i][start_row: start_row + rows_num] = _temp
    if res['Incremental Heating Summary'][13][2] == 'K/Ca':
        _temp, _s = [], []
        for j in range(rows_num):
            try:
                _temp.append(1 / res['Relative Abundances'][13][start_row + j])
                _s.append(calc_funcs.error_div((1, 0), (
                    res['Relative Abundances'][13][start_row + j], res['Relative Abundances'][14][start_row + j])))
            except TypeError:
                _temp.append(None)
                _s.append(None)
        res['Incremental Heating Summary'][13][start_row: start_row + rows_num] = _temp
        res['Incremental Heating Summary'][13][start_row: start_row + rows_num] = _s

    # degas相对误差改为绝对误差
    for i in range(len(res['Degassing Patterns'])):
        if res['Degassing Patterns'][i][2] in ['%1s', '%2s']:
            _temp = []
            for j in range(rows_num):
                try:
                    _temp.append(res['Degassing Patterns'][i][start_row + j] * res['Degassing Patterns'][i - 1][
                        start_row + j] / 100)
                except TypeError:
                    _temp.append('')
            res['Degassing Patterns'][i][start_row: start_row + rows_num] = _temp

    sequence_name = basic_funcs.getPartialArry(res['Procedure Blanks'], start_row, rows_num, *[1])
    sequence_value = basic_funcs.getPartialArry(res['Procedure Blanks'], start_row, rows_num, *[2])
    blank_values = basic_funcs.getPartialArry(
        res['Procedure Blanks'], start_row, rows_num,
        *[3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    sample_values = basic_funcs.getPartialArry(
        res['Intercept Values'], start_row, rows_num,
        *[3, 4, 8, 9, 13, 14, 18, 19, 23, 24])
    corrected_values = basic_funcs.getPartialArry(
        res['Relative Abundances'], start_row, rows_num,
        *[4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
    degas_values = basic_funcs.getPartialArry(
        res['Degassing Patterns'], start_row, rows_num,
        *[4, 5, 6, 7, 8, 9, 10, 11,
          12, 13,
          22, 23, 14, 15, 16, 17, 18, 19, 20, 21,
          24, 25, 26, 27,
          28, 29, 30, 31, 32, 33, 34, 35])
    publish_values = basic_funcs.getPartialArry(
        res['Incremental Heating Summary'], start_row, rows_num,
        *[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
    apparent_age_values = basic_funcs.getPartialArry(
        res['Relative Abundances'], start_row, rows_num, *[14, 15, 16, 17, -1, -1, 18, 19])
    isochron_values = [[]] * 39
    isochron_values[0:5] = basic_funcs.getPartialArry(
        res['Normal Isochron Table'], start_row, rows_num, *[4, 5, 6, 7, 10])
    isochron_values[5:11] = basic_funcs.getPartialArry(
        res['Inverse Isochron Table'], start_row, rows_num, *[-1, 4, 5, 6, 7, 10])
    total_param = basic_funcs.getPartialArry(
        res['Sample Parameters'], start_row, rows_num, *[
            # 1, 2,  # 0-1
            -1, -1, -1, -1,  # 2-5
            -1, -1, -1, -1,  # 6-9
            -1, -1, -1, -1, -1, -1,  # 10-15
            -1, -1, -1, -1,  # 16-19
            -1, -1,  # 20-21
            23, 24, -1, -1, -1, -1,  # 22-27
            -1, -1,  # 28-29
            22, -1, -1, -1,  # 30-33
            -1, -1,  # 34-35
            -1, -1,  # 36-37
            -1, -1,  # 38-39
            -1, -1,  # 40-41
            -1, -1,  # 42-43
            -1, -1,  # 44-45
            -1, -1,  # 46-47
            -1, -1,  # 48-49
            -1, -1,  # 50-51
            -1, -1,  # 52-53
            -1, -1,  # 54-55
            -1, -1,  # 56-57
            -1, -1,  # 58-59
            -1, -1, -1, -1, -1, -1, -1, -1, -1,  # 60-68
            10, 11, 12, 13,  #
            -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  #
            -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  #
            -1, -1, -1, -1,  #
            -1, -1, -1, -1,  #
            -1, -1, -1, -1, -1,  #
            -1, -1, -1, -1,  #
            -1, -1, -1, -1,  #
            -1,  #
        ])

    month_convert = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    experiment_start_time = []
    for i in basic_funcs.getTransposed(
            basic_funcs.getPartialArry(res['Sample Parameters'], start_row, rows_num, *[18, 17, 16, 19, 20])):
        _year = str(i[0]) if '.' not in str(i[0]) else str(i[0]).split('.')[0]
        _month = str(month_convert[str(i[1]).capitalize()]) if str(i[1]).capitalize() in month_convert.keys() else str(
            i[1]).capitalize()
        _day = str(i[2]) if '.' not in str(i[2]) else str(i[2]).split('.')[0]
        _hour = str(i[3]) if '.' not in str(i[3]) else str(i[3]).split('.')[0]
        _min = str(i[4]) if '.' not in str(i[4]) else str(i[4]).split('.')[0]
        experiment_start_time.append([_year, _month, _day, _hour, _min])

    total_param[31] = ['-'.join(i) for i in experiment_start_time]
    total_param[0:26] = basic_funcs.getPartialArry(
        res['Irradiation Constants'], start_row, rows_num,
        *[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28])

    isochron_values[11] = [''] * len(isochron_values[0])
    isochron_values[17] = [''] * len(isochron_values[0])
    isochron_values[23] = [''] * len(isochron_values[0])
    isochron_values[12:17] = calc_funcs.get_isochron(
        degas_values[20], degas_values[21], degas_values[24], degas_values[25], degas_values[10], degas_values[11]
    )  # 39/38, 40/38
    isochron_values[18:23] = calc_funcs.get_isochron(
        degas_values[20], degas_values[21], degas_values[10], degas_values[11], degas_values[24], degas_values[25]
    )  # 39/40, 38/40
    isochron_values[24:29] = calc_funcs.get_isochron(
        degas_values[10], degas_values[11], degas_values[24], degas_values[25], degas_values[20], degas_values[21]
    )  # 38/39, 40/39
    isochron_mark = [1 if i == 'P' else '' for i in basic_funcs.getPartialArry(
        res['Normal Isochron Table'], start_row, rows_num, *[3])]

    sample_info = {
        'sample': {'name': samplename, 'material': 'MATERIAL', 'location': 'LOCATION'},
        'researcher': {'name': 'RESEARCHER', 'addr': 'ADDRESS'},
        'laboratory': {'name': 'LABORATORY', 'addr': 'ADDRESS', 'analyst': 'ANALYST'}
    }

    res = [sample_values, blank_values, corrected_values, degas_values, publish_values,
           apparent_age_values, isochron_values, total_param, sample_info,
           isochron_mark, sequence_name, sequence_value]

    return create_sample_from_calc(content=res)


def open_xls(filepath: str):
    res = {}
    try:
        wb = open_workbook(filepath)
        for sheet_name in wb.sheet_names():
            sheet = wb.sheet_by_name(sheet_name)
            res[sheet_name] = [[sheet.cell(row, col).value for col in range(sheet.ncols)] for row in range(sheet.nrows)]
    except biffh.XLRDError as e:
        print('Error in opening excel file: %s' % str(e))
        return e
    else:
        return res


def open_filtered_xls(filepath: str):
    """
    :param filepath: directory of file
    :return: list = [dict, dict]
    """
    header = 2
    try:
        wb = open_workbook(filepath)
        sheet_1 = wb.sheet_by_name('Intercept Value')
        sheet_2 = wb.sheet_by_name('Procedure Blanks')
        if sheet_1.nrows != sheet_2.nrows:
            raise IndexError('Row counts differ')
    except biffh.XLRDError as e:
        print('Error in opening filtered excel file: %s' % str(e))
        return False
    except IndexError as e:
        print('Error in opening filtered excel file: %s' % str(e))
        return False
    else:
        # reading intercept sheet
        intercept_value = [[sheet_1.cell(row, col).value for col in range(sheet_1.ncols)] for row in
                           range(header, sheet_1.nrows)]
        # reading blank sheet
        blank_value = [[sheet_2.cell(row, col).value for col in range(sheet_2.ncols)] for row in
                       range(header, sheet_2.nrows)]
        # remember as dicts
        dict_intercept, dict_blank = {}, {}
        for row in range(len(intercept_value)):
            dict_intercept[intercept_value[row][0]] = intercept_value[row]
            dict_blank[intercept_value[row][0]] = blank_value[row]
        return [dict_intercept, dict_blank]


def open_air_xls(filepath: str):
    """
    :param filepath:
    :return:
    """
    book_contents = read_calc_file(filepath)
    if not book_contents:
        return

    (dict_blank, dict_intercept, filtered_file_path) = \
        create_blank_intercept_file(book_contents, filepath)
    # delete filtered file
    os.remove(filtered_file_path)
    return dict_intercept, dict_blank, book_contents


def read_calc_file(filepath: str):
    """
    :param filepath: file with suffix of .age or .air
    :return: dict, keys are sheet name, value are list of [[col 0], [col 1], ...] of corresponding sheet
    """
    PASSWORD = 'aapkop'  # password to open age file, the password to unhide worksheets is boris
    decrypt_file_path = filepath + '_decrypt.xls'
    try:
        # opening excel in decrypt function would reveal the hidden sheet without protect
        with open(filepath, 'rb') as age_file:
            office_file = msoffcrypto.OfficeFile(age_file)
            office_file.load_key(password=PASSWORD)
            office_file.decrypt(open(decrypt_file_path, 'wb'))
        wb = open_workbook(decrypt_file_path)
        worksheets = wb.sheet_names()
        book_contents = dict()
        for each_sheet in worksheets:
            sheet = wb.sheet_by_name(each_sheet)
            sheet_contents = [
                [sheet.cell(row, col).value for row in range(sheet.nrows)]
                for col in range(sheet.ncols)
            ]
            book_contents[each_sheet] = sheet_contents
        os.remove(decrypt_file_path)
    except Exception as e:
        print(traceback.format_exc())
        return False
    else:
        # print(book_contents)
        return book_contents


def create_sample_from_calc(content: list):
    """
    content:
        [
            sample_values, blank_values, corrected_values, degas_values, publish_values,
            apparent_age_values, isochron_values, total_param, sample_info, isochron_mark,
            sequence_name, sequence_value
        ]
    return sample instance
    """
    # Create sample file
    sample = samples.Sample()
    # Initializing
    smp_funcs.initial(sample)
    sample.SampleIntercept = content[0]
    sample.BlankIntercept = content[1]
    sample.CorrectedValues = content[2]
    sample.DegasValues = content[3]
    sample.PublishValues = content[4]
    sample.ApparentAgeValues = content[5]
    sample.IsochronValues = content[6]
    sample.TotalParam = content[7]
    smp_funcs.update_plot_from_dict(sample.Info, content[8])
    # sample.Info.update(content[8])
    sample.IsochronMark = content[9]
    sample.SequenceName = content[10]
    sample.SequenceValue = content[11]

    sample.SelectedSequence1 = [i for i in range(len(sample.IsochronMark)) if sample.IsochronMark[i] == 1]
    sample.SelectedSequence2 = [i for i in range(len(sample.IsochronMark)) if sample.IsochronMark[i] == 2]
    sample.UnselectedSequence = [i for i in range(len(sample.IsochronMark)) if
                                 i not in sample.SelectedSequence1 + sample.SelectedSequence2]
    sample.AgeSpectraPlot.initial_params.update({
        'useInputInitial': [
            sample.TotalParam[0][0], sample.TotalParam[1][0] * sample.TotalParam[0][0] / 100,
            sample.TotalParam[0][0], sample.TotalParam[1][0] * sample.TotalParam[0][0] / 100
        ]
    })
    try:
        # Re-calculating ratio and replot after reading age or full files
        smp_funcs.recalculate(sample, re_calc_ratio=True, re_plot=True, re_plot_style=True)
    except Exception as e:
        print(f'Error in setting plot: {traceback.format_exc()}')
    # Write tables after reading data from a full or age file
    smp_funcs.update_table_data(sample)
    return sample


def create_blank_intercept_file(book_contents: dict, filepath: str = ""):
    """
    :param book_contents: dict read from calc file
    :param filepath: calc file path
    :return: dict of blank, dict of intercept, filtered file path
    """
    wb = write_workbook()
    sheet_intercept = wb.add_sheet('Intercept Value', cell_overwrite_ok=True)
    sheet_blank = wb.add_sheet('Procedure Blanks', cell_overwrite_ok=True)
    sheet_intercept_header = ['Intercept Value', '', '36Ar[fA]', '1σ', 'r2',
                              '37Ar[fA]', '1σ', 'r2', '38Ar[fA]', '1σ', 'r2',
                              '39Ar[fA]', '1σ', 'r2', '40Ar[fA]', '1σ', 'r2',
                              'Day', 'Mouth', 'Year', 'Hour', 'Min']
    sheet_blank_header = ['Procedure Blanks', '', 'Real Procedure Blanks', '36Ar[fA]', '1σ', '37Ar[fA]', '1σ',
                          '38Ar[fA]', '1σ', '39Ar[fA]', '1σ', '40Ar[fA]', '1σ', 'Day', 'Mouth', 'Year', 'Hour',
                          'Min']
    # rows_unm-->样品阶段数
    rows_num = len(set(book_contents['Data Tables'][1])) - 2
    # intercept value
    data_tables_value = book_contents['Data Tables']

    month_convert = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    # write intercept
    for j in range(0, 22):
        sheet_intercept.write(0, j, sheet_intercept_header[j])
    for i in range(2, rows_num + 2):
        for j in range(0, 2):
            sheet_intercept.write(i, j, data_tables_value[j + 14][i + 3])
        for j in range(2, 5):
            sheet_intercept.write(i, j, data_tables_value[j + 14][i + 3])
        for j in range(5, 17):
            sheet_intercept.write(i, j, data_tables_value[j + 14 + (j - 2) // 3 * 2][i + 3])
        for j in range(17, 22):
            if j == 18:
                month_str = data_tables_value[j + 40][i + 3]
                month_int = month_convert[month_str] if month_str.capitalize() in month_convert.keys() else month_str
                sheet_intercept.write(i, j, month_int)
            else:
                sheet_intercept.write(i, j, data_tables_value[j + 40][i + 3])
    # write blank
    for j in range(0, 18):
        sheet_blank.write(0, j, sheet_blank_header[j])
    for i in range(2, rows_num + 2):
        for j in range(0, 2):
            sheet_blank.write(i, j, data_tables_value[j + 1][i + 3])
        for j in range(3, 13):
            sheet_blank.write(i, j, data_tables_value[j][i + 3])
    # save file
    filtered_file_path = filepath + '_new_filter.xls'
    try:
        wb.save(filtered_file_path)
    except PermissionError:
        print('file has already been opened, overwriting is forbidden')
        return False
    [dict_intercept, dict_blank] = open_filtered_xls(filtered_file_path)
    return dict_blank, dict_intercept, filtered_file_path


def open_raw_file(filepath: str, extension: str = 'xls'):
    """
    :param filepath: directory of file
    :param extension: filter 1 for .xls files, 2 for .ahd files
    :return: step_list -> [[[header of step one], [cycle one in the step], [cycle two in the step]],[[],[]]]
        example:
            [
                [
                    [1, '6/8/2019  8:20:51 PM', 'BLK', 'B'],  # step header
                    # [sequence index, date time, label, value]
                    ['1', 12.30, 87.73, 12.30, 1.30, 12.30, 0.40, 12.30, 0.40, 12.30, 0.44],  # step/sequence 1
                    # [cycle index, time, Ar40 signal, time, Ar39 signal, ..., time, Ar36 signal]
                    ['2', 24.66, 87.70, 24.66, 1.14, 24.66, 0.36, 24.66, 0.35, 24.66, 0.43],  # step/sequence 2
                    ...
                    ['10', 123.06, 22262.68, 123.06, 6.54, 123.06, 8.29, 123.06, 0.28, 123.06, 29.22],
                ],
                [
                    ...
                ]
            ]
    """
    try:
        handler = {'xls': open_raw_xls, 'ahd': open_raw_ahd}[extension.lower()]
    except KeyError:
        print(traceback.format_exc())
        return False
    else:
        return handler(filepath)


def open_raw_xls(filepath):
    try:
        wb = open_workbook(filepath)
        sheets = wb.sheet_names()
        sheet = wb.sheet_by_name(sheets[0])
        value, step_header, step_list = [], [], []
        for row in range(sheet.nrows):
            row_set = []
            for col in range(sheet.ncols):
                if sheet.cell(row, col).value == '':
                    pass
                else:
                    row_set.append(sheet.cell(row, col).value)
            if row_set != [] and len(row_set) > 1:
                value.append(row_set)
        for each_row in value:
            # if the first item of each row is float (1.0, 2.0, ...) this row is the header of a step.
            if isinstance(each_row[0], float):
                each_row[0] = int(each_row[0])
                step_header.append(each_row)
        for step_index, each_step_header in enumerate(step_header):
            row_start_number = value.index(each_step_header)
            try:
                row_stop_number = value.index(step_header[step_index + 1])
            except IndexError:
                row_stop_number = len(value) + 1
            step_values = [
                each_step_header[0:4],
                *list(map(
                    lambda x: [x[0], x[1], x[2], x[1], x[3], x[1], x[4], x[1], x[5], x[1], x[6]],
                    [value[i] for i in range(row_start_number + 2, row_stop_number - 7, 1)]))
            ]
            step_list.append(step_values)
    except Exception as e:
        print('Error in opening the original file: %s' % str(e))
        return False
    else:
        return step_list


def open_raw_ahd(filepath):
    try:
        value, step_header, step_list = [], [], []
        with open(filepath, 'r', encoding='utf-16-le') as f:
            value = f.read()
        value = [[j for j in i.split('\t') if j != ''] for i in value.split('\n')]
        datetime = 'ddmmyyyy'
        if datetime == 'ddmmyyyy':
            dd, mm, yyyy = value[6][1].split('/')
            value[6][1] = '/'.join([mm, dd, yyyy])
        step_count = int(value[12][2])
        step_header = [1, '  '.join(value[6][1:3]), value[0][1], value[8][1]]
        step_list.append([step_header])
        for step_index in range(step_count):
            start_row = 15 + 5 * step_index
            step_list[0].append([
                str(step_index+1),
                float(value[start_row+4][0]), float(value[start_row+4][1]),
                float(value[start_row+3][0]), float(value[start_row+3][1]),
                float(value[start_row+2][0]), float(value[start_row+2][1]),
                float(value[start_row+1][0]), float(value[start_row+1][1]),
                float(value[start_row+0][0]), float(value[start_row+0][1]),
            ])
    except Exception as e:
        print('Error in opening the original file: %s' % str(e))
        return False
    else:
        return step_list


def import_blank_list(filepath: str):
    # 读取excel数据表
    wb = open_workbook(filepath)
    # 获取sheet名字，得到名字列表
    blank_sheet_index = 1
    blank_sheet_begin_at = 2
    # 根据sheet名字判断是否为正确的文件
    sheet = wb.sheet_by_index(blank_sheet_index)
    file_contents = [[sheet.cell(row_num, col_num).value for col_num in range(sheet.ncols)] for row_num in
                     range(blank_sheet_begin_at, sheet.nrows)]
    file_dict = dict()
    for i in range(len(file_contents)):
        file_contents[i][0] = ''
        file_dict[file_contents[i][2]] = file_contents[i]

    print(file_dict)


def save_webarar_file(dir, sample: samples.Sample):
    # file_path = os.path.join(dir, f"{sample.Info['sample']['name']}.arr")
    file_path = os.path.join(dir, f"{sample.Info.sample.name}.arr")
    with open(file_path, 'wb') as f:
        f.write(pickle.dumps(sample))
    # with open(file_path, 'w') as f:  # save serialized json data to a readable text
    #     f.write(basic_funcs.getJsonDumps(sample))
    return f"{sample.Info.sample.name}.arr"


def save_setting_file(dir, name, type, params):
    """
    type == 'irra' or 'calc' or 'smp'
    """
    file_path = os.path.join(dir, f"{name}.{type}")
    # with open(file_path, 'wb') as f:
    #     f.write(pickle.dumps(params))
    return update_setting_file(file_path, params)


def update_setting_file(file_path, params):
    # with open(file_path, 'wb') as f:
    #     f.write(pickle.dumps(params))
    with open(file_path, 'w') as f:  # save serialized json data to a readable text
        f.write(basic_funcs.getJsonDumps(params))
    return file_path


def save_txt_file(file_path, text):
    with open(file_path, 'w') as f:
        f.write(text)
    return file_path


def delete_setting_file(file_path):
    try:
        os.remove(file_path)
    except Exception:
        return False
    else:
        return True


def read_setting_file(file_path):
    import json
    try:
        with open(file_path, 'r') as f:
            params = json.load(f)
    except UnicodeDecodeError:
        with open(file_path, 'rb') as f:
            params = pickle.load(f)
    return params


def check_arr_version(old):
    print(f'Arr version: {old.ArrVersion}')
    new = samples.Sample()
    smp_funcs.initial(new)

    print("update sample version")
    if old.ArrVersion == '20221015':
        smp_funcs.update_plot_from_dict(new.Info, old._Sample__info)
        # new.Info.update(old._Sample__info)
        new.SequenceName = old._Sample__sample_intercept[0]
        new.SequenceValue = old._Sample__sample_intercept[1]
        new.BlankIntercept = old._Sample__blank_intercept[2:]
        new.SampleIntercept = old._Sample__sample_intercept[2:]

        new.NewIntercept = old._Sample__new_intercept
        new.NewBlank = old._Sample__new_intercept
        new.NewParam = old._Sample__new_param
        new.AnalysisDateTime = old._Sample__analysis_date_time

        new.BlankCorrected = old._Sample__blank_corrected
        new.MassDiscrCorrected = old._Sample__mass_discr_corrected
        new.DecayCorrected = old._Sample__decay_corrected
        new.InterfereneCorrected = old._Sample__interference_corrected
        new.CorrectedValues = old._Sample__corrected_values[2:]
        new.DegasValues = old._Sample__degas_values[2:]

        new.PublishValues = old._Sample__publish_table[2:]
        new.IsochronMark = old._Sample__isochron_values[2]
        new.IsochronValues = old._Sample__isochron_values[3:]
        new.TotalParam = old._Sample__total_param[2:]

        new.ApparentAgeValues = old._Sample__apparent_age_values
        new.ApparentAgeValues[5:8] = [[None] * len(new.ApparentAgeValues[0])] + new.PublishValues[7:9]

        new.SelectedSequence1 = old._Sample__selected_sequence_1
        new.SelectedSequence2 = old._Sample__selected_sequence_2
        new.UnselectedSequence = old._Sample__unselected_sequence

        new.CalcParams = old._Sample__calc_params
        return check_arr_version(new)
    elif old.ArrVersion == '20230521':
        try:
            smp_funcs.update_plot_from_dict(new.Info, old._Sample__info)
            # new.Info.__dict__.update(old._Sample__info)
            new.SequenceName = old._Sample__sequence_name
            new.SequenceValue = old._Sample__sequence_value
            new.BlankIntercept = old._Sample__blank_intercept
            new.SampleIntercept = old._Sample__sample_intercept

            new.NewIntercept = old._Sample__new_intercept
            new.NewBlank = old._Sample__new_intercept
            new.NewParam = old._Sample__new_param
            new.AnalysisDateTime = old._Sample__analysis_date_time

            new.BlankCorrected = old._Sample__blank_corrected
            new.MassDiscrCorrected = old._Sample__mass_discr_corrected
            new.DecayCorrected = old._Sample__decay_corrected
            new.InterfereneCorrected = old._Sample__interference_corrected
            new.CorrectedValues = old._Sample__corrected_values
            new.DegasValues = old._Sample__degas_values

            new.PublishValues = old._Sample__publish_values
            new.IsochronMark = old._Sample__isochron_mark
            new.IsochronValues = old._Sample__isochron_values
            new.TotalParam = old._Sample__total_params
            new.ApparentAgeValues = old._Sample__apparent_age_values

            new.SelectedSequence1 = old._Sample__selected_sequence_1
            new.SelectedSequence2 = old._Sample__selected_sequence_2
            new.UnselectedSequence = old._Sample__unselected_sequence
            new.CalcParams = old._Sample__calc_params

            new.ArrVersion = '20230709'
            return check_arr_version(new)
        except:
            old.ArrVersion = '20230709'
            return check_arr_version(old)
    # elif old.ArrVersion == '20230709':
    #     old.IsochronValues = old.IsochronValues + [['']*len(old.SequenceName)]*7
    #     old.TotalParamsTable.header = samples.TOTAL_PARAMS_HEADERS
    #     old.IsochronsTable.header = samples.ISOCHRON_TABLE_HEADERS
    #     old.IsochronsTable.colcount = len(old.IsochronsTable.header)
    #     old.IsochronsTable.coltypes = [{'type': 'text'}] + [{'type': 'numeric'}] * (old.IsochronsTable.colcount - 1)
    #     old.ThreeDIsochronPlot = samples.Plot(
    #         id='figure_7', name='Three D Isochron', type='isochron',
    #         xaxis=samples.Plot.Axis(title='{sup|36}Ar{sub|a+Cl} / {sup|40}Ar{sub|a+r}'),
    #         yaxis=samples.Plot.Axis(title='{sup|38}Ar{sub|a+Cl} / {sup|40}Ar{sub|a+r}'),
    #         zaxis=samples.Plot.Axis(title='{sup|39}Ar{sub|K} / {sup|40}Ar{sub|a+r}'),
    #     )
    #     old.Components['figure_7'] = old.ThreeDIsochronPlot
    #     for k, v in old.Components.items():
    #         if isinstance(v, samples.Plot):
    #             v.label = samples.Plot.Label()
    #     old.ArrVersion = '20230724'
    #     return check_arr_version(old)
    # elif old.ArrVersion == '20230724':
    #     old.AgeSpectraPlot.initial_params = old.CalcParams
    #     old.IsochronsTable.header = samples.ISOCHRON_TABLE_HEADERS
    #     smp_funcs.update_table_data(old)  # Update tables after updating the arr file
    #     # Recalculate isochron data and replot
    #     # smp_funcs.recalculate(old, re_calc_ratio=True, re_plot=True, re_style=True)
    #     old.ArrVersion = new.ArrVersion
    #     return check_arr_version(old)

    # Check attributes of sample instance
    if isinstance(old.Info, dict):
        smp_funcs.update_plot_from_dict(new.Info, old.Info)
        setattr(old, 'Info', new.Info)
    if getattr(old, 'ArrVersion', 0) != getattr(new, 'ArrVersion', 1):
        smp_funcs.get_merged_smp(old, new)
        smp_funcs.set_plot_style(old)
    setattr(old, 'ArrVersion', new.ArrVersion)
    print('This is the Latest Version')
    return old


def get_lines_data(sequenceData):
    def _get_scatter_x(a: list, nope=50):
        interval = (max(a) - 0) / nope
        return [interval * (i + 1) for i in range(nope)]

    linesData, linesResults = [], []
    for i in range(5):
        try:
            _ = basic_funcs.getTransposed(sequenceData[i])
            x, y = _[0], _[1]
            line_res = calc_funcs.intercept_linest(a0=y, a1=x)
            quad_res = calc_funcs.intercept_quadratic(a0=y, a1=x)
            exp_res = calc_funcs.intercept_exponential(a0=y, a1=x)
            pow_res = calc_funcs.intercept_power(a0=y, a1=x)
            ave_res = calc_funcs.intercept_average(a0=y)

            if abs(pow_res[0]) > 10 * max(y):
                pow_res = ['BadFitting', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
            elif pow_res[0] < 0:
                pow_res = ['Negative', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']

            lines_x = [_x for _x in [0] + _get_scatter_x(x)]
            linesData.append([])
            for res in [line_res, quad_res, exp_res, pow_res, ave_res]:
                try:
                    linesData[i].append(basic_funcs.getTransposed([lines_x, res[7](lines_x)]))
                except Exception as e:
                    linesData[i].append([])
            # linesData.append([
            #     [[_x, line_res[0] + _x * line_res[5][0]] for _x in (0, max(x))],
            #     [[_x, quad_res[0] + _x * quad_res[5][0] + _x ** 2 * quad_res[5][1]] for _x in [0] + _get_scatter_x(x)],
            #     [[_x, exp_res[5][0] * exp_res[5][1] ** _x + exp_res[5][2]] for _x in
            #      [0] + _get_scatter_x(x)] if isinstance(exp_res[0], float) else [],
            #     [[0, pow_res[0]]] + [[_x, pow_res[5][0] * _x ** pow_res[5][1] + pow_res[5][2]] for _x in
            #                          _get_scatter_x(x)] if isinstance(pow_res[0], float) else [],
            #     [[_x, ave_res[0]] for _x in (0, max(x))],
            # ])
            linesResults.append([line_res[0:4], quad_res[0:4], exp_res[0:4], pow_res[0:4], ave_res[0:4]])
        except IndexError:
            linesData.append([[], [], [], []])
            linesResults.append([[], [], [], []])
    return linesData, linesResults


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
        xls = Workbook(self.filepath)
        style = xls.add_format(self.style)

        # unicode for supscript numbers
        sup_36 = '\u00B3\u2076'
        sup_37 = '\u00B3\u2077'
        sup_38 = '\u00B3\u2078'
        sup_39 = '\u00B3\u2079'
        sup_40 = '\u2074\u2070'

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
        spectra_data = basic_funcs.getTransposed(self.sample.AgeSpectraPlot.data)
        spectra_set1_data = basic_funcs.getTransposed(self.sample.AgeSpectraPlot.set1.data) or [[]] * 3
        spectra_set2_data = basic_funcs.getTransposed(self.sample.AgeSpectraPlot.set2.data) or [[]] * 3
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
        set_data = [set1_data, set2_data, set3_data] = basic_funcs.getIsochronSetData(
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
        set_data = [set1_data, set2_data, set3_data] = basic_funcs.getIsochronSetData(
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
        set_data = [set1_data, set2_data, set3_data] = basic_funcs.getIsochronSetData(
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
        set_data = [set1_data, set2_data, set3_data] = basic_funcs.getIsochronSetData(
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
        set_data = [set1_data, set2_data, set3_data] = basic_funcs.getIsochronSetData(
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

        _write_results(sht_result, 10, 0, 'Total Age', [
            *self.sample.AgeSpectraPlot.info[0:2], '', self.sample.AgeSpectraPlot.info[4],
            self.sample.AgeSpectraPlot.info[6], '',
            '', 1, len(self.sample.SequenceName), '', '', ''])
        _write_results(sht_result, 10, 12, 'Total Age', [
            *self.sample.AgeSpectraPlot.info[0:2], '', self.sample.AgeSpectraPlot.info[4],
            self.sample.AgeSpectraPlot.info[6], '',
            '', 1, len(self.sample.SequenceName), '', '', ''])
        try:
            _write_results(sht_result, 17, 0, 'Set 1 Age Plateau', [
                *self.sample.AgeSpectraPlot.set1.info[0:2], '',
                self.sample.AgeSpectraPlot.set1.info[4], self.sample.AgeSpectraPlot.set1.info[6], '',
                self.sample.AgeSpectraPlot.set1.info[3], '', self.sample.AgeSpectraPlot.set1.info[2],
                '', '', ''
            ])
        except IndexError:
            pass
        try:
            _write_results(sht_result, 17, 12, 'Set 2 Age Plateau', [
                *self.sample.AgeSpectraPlot.set2.info[0:2], '',
                self.sample.AgeSpectraPlot.set2.info[4], self.sample.AgeSpectraPlot.set2.info[6], '',
                self.sample.AgeSpectraPlot.set2.info[2], '', self.sample.AgeSpectraPlot.set2.info[3],
                '', '', ''
            ])
        except IndexError:
            pass
        for row_index, figure in enumerate(['figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6']):
            for col_index, set in enumerate(['set1', 'set2']):
                try:
                    _isochron_results = getattr(smp_funcs.get_component_byid(self.sample, figure), set)
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
                except IndexError:
                    continue

        for sht_name, [prop_name, sht_type, row, col, _, smp_attr_name, header_name] in self.template.sheet():
            if sht_type == "table":
                data = basic_funcs.getTransposed(getattr(self.sample, smp_attr_name, None).data)
                sht = xls.add_worksheet(sht_name)
                sht.hide_gridlines(2)  # 0 = show grids, 1 = hide print grid, else = hide print and screen grids
                sht.hide()  # default hidden table sheet
                sht.set_column(0, len(data), width=12)  # column width
                header = getattr(styles, header_name)
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
                        smp_funcs.get_component_byid(self.sample, 'figure_2').xaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_2').xaxis.max,
                        smp_funcs.get_component_byid(self.sample, 'figure_2').yaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_2').yaxis.max,
                    ]
                    self.get_chart_isochron(xls, sht, data_area, axis_range,
                                            title_name="Normal Isochron", x_axis_name=f"{sup_39}Ar / {sup_36}Ar",
                                            y_axis_name=f"{sup_40}Ar / {sup_36}Ar")
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
                        smp_funcs.get_component_byid(self.sample, 'figure_3').xaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_3').xaxis.max,
                        smp_funcs.get_component_byid(self.sample, 'figure_3').yaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_3').yaxis.max,
                    ]
                    self.get_chart_isochron(xls, sht, data_area, axis_range,
                                            title_name="Inverse Isochron", x_axis_name=f"{sup_39}Ar / {sup_40}Ar",
                                            y_axis_name=f"{sup_36}Ar / {sup_40}Ar")
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
                        smp_funcs.get_component_byid(self.sample, 'figure_4').xaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_4').xaxis.max,
                        smp_funcs.get_component_byid(self.sample, 'figure_4').yaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_4').yaxis.max,
                    ]
                    self.get_chart_isochron(xls, sht, data_area, axis_range,
                                            title_name="K-Cl-Ar 1 Isochron", x_axis_name=f"{sup_39}Ar / {sup_38}Ar",
                                            y_axis_name=f"{sup_40}Ar / {sup_38}Ar")
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
                        smp_funcs.get_component_byid(self.sample, 'figure_5').xaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_5').xaxis.max,
                        smp_funcs.get_component_byid(self.sample, 'figure_5').yaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_5').yaxis.max,
                    ]
                    self.get_chart_isochron(xls, sht, data_area, axis_range,
                                            title_name="K-Cl-Ar 2 Isochron", x_axis_name=f"{sup_39}Ar / {sup_40}Ar",
                                            y_axis_name=f"{sup_38}Ar / {sup_40}Ar")
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
                        smp_funcs.get_component_byid(self.sample, 'figure_6').xaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_6').xaxis.max,
                        smp_funcs.get_component_byid(self.sample, 'figure_6').yaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_6').yaxis.max,
                    ]
                    self.get_chart_isochron(xls, sht, data_area, axis_range,
                                            title_name="K-Cl-Ar 3 Isochron", x_axis_name=f"{sup_38}Ar / {sup_39}Ar",
                                            y_axis_name=f"{sup_40}Ar / {sup_39}Ar")
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
                        smp_funcs.get_component_byid(self.sample, 'figure_8').xaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_8').xaxis.max,
                        smp_funcs.get_component_byid(self.sample, 'figure_8').yaxis.min,
                        smp_funcs.get_component_byid(self.sample, 'figure_8').yaxis.max,
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
        chart.x_axis.update({'name': 'Cumulative \u00B3\u2079Ar released (%)', 'min': xMin, 'max': xMax})
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
        sup_36 = '\u00B3\u2076'
        sup_37 = '\u00B3\u2077'
        sup_38 = '\u00B3\u2078'
        sup_39 = '\u00B3\u2079'
        sup_40 = '\u2074\u2070'
        # series name
        series_name = [
            f'{sup_36}Ara', f'{sup_37}ArCa', f'{sup_38}ArCl', f'{sup_39}ArK', f'{sup_40}Arr',
            f'{sup_36}Ar', f'{sup_37}Ar', f'{sup_38}Ar', f'{sup_39}Ar', f'{sup_40}Ar',
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
        self.sample = samples.Sample()
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
        for index, each_col in enumerate(basic_funcs.getTransposed(
                [basic_funcs.getTransposed(self.isochron_data)[i] for i in self.sample.SelectedSequence1])):
            isochron_set1_ws.from_list(index, each_col)  # Normal, invers, K-Cl-Ar 1, K-Cl-Ar 2, K-Cl-Ar 3, 3D
        for index, each_col in enumerate(basic_funcs.getTransposed(
                [basic_funcs.getTransposed(self.isochron_data)[i] for i in self.sample.SelectedSequence2])):
            isochron_set2_ws.from_list(index, each_col)  # Normal, invers, K-Cl-Ar 1, K-Cl-Ar 2, K-Cl-Ar 3, 3D
        for index, each_col in enumerate(basic_funcs.getTransposed(
                [basic_funcs.getTransposed(self.isochron_data)[i] for i in self.sample.UnselectedSequence])):
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
        self.sample = samples.Sample()
        self.figure = samples.Plot()
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
        data = basic_funcs.getTransposed(data)
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
            if not basic_funcs.thisListIsEmpty(self.figure.line1.info):
                content += self._get_isochron_line(*self.figure.line1.data, width=1, color='1 0 0')
            if not basic_funcs.thisListIsEmpty(self.figure.line2.info):
                content += self._get_isochron_line(*self.figure.line2.data, width=1, color='0 0 1')
            for point in basic_funcs.getTransposed(self.figure.data):
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
                data = basic_funcs.getTransposed(data)
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

import traceback
import uuid
from programs import samples, calc_funcs, basic_funcs
from math import exp, log
from scipy.signal import find_peaks
import copy
import re


# smp operation
def initial(sample: samples.Sample):
    # 已更新 2023/7/4
    sample.TotalParam = [[]] * 115
    sample.BlankIntercept = [[]] * 10
    sample.SampleIntercept = [[]] * 10
    sample.PublishValues = [[]] * 11
    sample.DecayCorrected = [[]] * 10
    sample.CorrectedValues = [[]] * 10
    sample.DegasValues = [[]] * 32
    sample.ApparentAgeValues = [[]] * 8
    sample.IsochronValues = [[]] * 47

    # Doi
    if not hasattr(sample, 'Doi') or getattr(sample, 'Doi') is None:
        setattr(sample, 'Doi', str(uuid.uuid4().hex))

    # Info
    result_tuple_name = (
        "plateau_f", "s_plateau_f", "inverse_f", "s_inverse_f", "normal_f", "s_normal_f",
        "plateau_age", "s_plateau_age", "plateau_mswd", "plateau_chisq", "plateau_pvalue",
        "inverse_age", "s_inverse_age", "inverse_mswd", "inverse_chisq", "inverse_pvalue",
        "normal_age", "s_normal_age", "normal_mswd", "normal_chisq", "normal_pvalue",
    )
    from collections import namedtuple
    result_set_1 = dict((name, None) for name in result_tuple_name)
    result_set_2 = dict((name, None) for name in result_tuple_name)
    # result_set_2 = basic_funcs.namedtuple("Results", result_tuple_name)
    setattr(sample, 'Info', samples.Info(
        id='0', name='info', attr_name='Info',
        sample=samples.Info(
            name='SAMPLE NAME', material='MATERIAL', location='LOCATION'
        ),
        researcher=samples.Info(
            name='RESEARCHER', addr='ADDRESS', email='EMAIL'
        ),
        laboratory=samples.Info(
            name='LABORATORY', addr='ADDRESS', email='EMAIL', info='INFORMATION', analyst='ANALYST'
        ),
        results=samples.Info(
            name='RESULTS', plateau_F=[], plateau_age=[], total_F=[], total_age=[],
            isochron_F=[], isochron_age=[], J=[],
            set1=result_set_1, set2=result_set_2
        ),
        reference=samples.Info(
            name='REFERENCE', journal='JOURNAL', doi='DOI'
        ),
    ))

    # Plots and Tables
    setattr(sample, 'UnknownTable', samples.Table(
        id='1', name='Unknown', header=samples.SAMPLE_INTERCEPT_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 20))
    ))
    setattr(sample, 'BlankTable', samples.Table(
        id='2', name='Blank', header=samples.BLANK_INTERCEPT_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 20))
    ))
    setattr(sample, 'CorrectedTable', samples.Table(
        id='3', name='Corrected', header=samples.CORRECTED_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 35))
    ))
    setattr(sample, 'DegasPatternTable', samples.Table(
        id='4', name='Degas Pattern', header=samples.DEGAS_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 35))
    ))
    setattr(sample, 'PublishTable', samples.Table(
        id='5', name='Publish', header=samples.PUBLISH_TABLE_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 20))
    ))
    setattr(sample, 'AgeSpectraTable', samples.Table(
        id='6', name='Age Spectra', header=samples.SPECTRUM_TABLE_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 26))
    ))
    setattr(sample, 'IsochronsTable', samples.Table(
        id='7', name='Isochrons', header=samples.ISOCHRON_TABLE_HEADERS,
        textindexs=[0], numericindexs=list(range(1, 42))
    ))
    setattr(sample, 'TotalParamsTable', samples.Table(
        id='8', name='Total Params', header=samples.TOTAL_PARAMS_HEADERS,
        textindexs=[0, 29, 30, 32, 33, 60, *list(range(101, 115))], numericindexs=list(range(1, 120))
    ))

    initial_plot_styles(sample)
    setattr(
        sample.AgeSpectraPlot, 'initial_params', {
            'useInverseInitial': True, 'useNormalInitial': False, 'useOtherInitial': False,
            'useInputInitial': [298.56, 0, 298.56, 0]
        }
    )

    return sample


def initial_plot_styles(sample: samples.Sample, except_attrs: list = []):
    """
    Initialize plot components styles based on Default Styles. Except attrs is a list containing attrs
    that are not expected to be initialized.
    Judgment order:
        1. The attr name is in except attrs and the sample has this attr: skip
        2. The value is not a dict instance: setattr()
        3. The sample has attr and it is a Set/Label/Text/Axis instance: iteration
    """

    def set_attr(obj, name, value):
        if name in except_attrs and hasattr(obj, name):
            pass
        elif not isinstance(value, dict):
            setattr(obj, name, value)
        else:
            if not (hasattr(obj, name) and isinstance(getattr(obj, name), samples.Plot.BasicAttr)):
                setattr(obj, name, getattr(samples.Plot, value['type'].capitalize())())
            for k, v in value.items():
                set_attr(getattr(obj, name), k, v)

    default_styles = copy.deepcopy(samples.DEFAULT_PLOT_STYLES)
    for figure_index, figure_attr in default_styles.items():
        plot = getattr(sample, figure_attr['attr_name'], samples.Plot())
        for key, attr in figure_attr.items():
            set_attr(plot, key, attr)


def re_set_smp(sample: samples.Sample):
    std = initial(samples.Sample())
    get_merged_smp(sample, std)


def update_plot_from_dict(plot, attrs: dict):
    """
    plot is a Sample.Plot instance, attrs should be a dict like {'xaxis': {'show_splitline': False}, 'yaxis': {...}}
    """

    def _do(plot, attrs: dict):
        for k1, v1 in attrs.items():
            if isinstance(v1, dict):
                _do(getattr(plot, k1), v1)
            else:
                setattr(plot, k1, v1)

    _do(plot=plot, attrs=attrs)
    return plot


def get_diff_smp(backup: (dict, samples.Sample), smp: (dict, samples.Sample)):
    """
    Comparing two sample component dicts or sample instances, and return difference between them.
    Parameters:
        backup: backup of sample.Components or sample before changed,
        smp: sample.Components or sample after changed
    Return:
        dict of keys and values that have difference, iterate to a sepcial difference,

            for example:
                A = Sample(id = 'a', set1 = Set(id = 'set1', data = [])),
                B = Sample(id = 'b', set1 = Set(id = 'set1', data = [2023])),
                res = get_diff_smp(A, B) will be {'id': 'b', 'set1': {'data': [2023]}}
    """
    res = {}
    if isinstance(backup, samples.Sample) and isinstance(smp, samples.Sample):
        return get_diff_smp(backup.__dict__, smp.__dict__)
    for name, attr in smp.items():
        if name not in backup.keys() or type(attr) != type(backup[name]):
            res.update({name: attr})
            continue
        if isinstance(attr, dict):
            _res = get_diff_smp(backup[name], attr)
            if _res != {}:
                res.update({name: _res})
            continue
        if isinstance(attr, (samples.Plot, samples.Table, samples.Plot.Text, samples.Plot.Axis, samples.Plot.Set,
                             samples.Plot.Label, samples.Plot.BasicAttr, samples.Info)):
            _res = get_diff_smp(backup[name].__dict__, attr.__dict__)
            if _res != {}:
                res.update({name: _res})
            continue
        if str(backup[name]) == str(attr) or backup[name] == attr:
            continue
        else:
            res.update({name: attr})
    return res


def get_merged_smp(a: samples.Sample, b: (samples.Sample, dict)):
    """
    Comparing two sample instances a and b
    This function is used to update sample instance to make sure JS can read properties it required.
    Parameters:
        a: sample instance that has old attributes,
        b: new sample instance that has some new attributes or a has similar but different name for this attribute
    Return:
        return none, but a will be updated after calling this function

            for example:
                A = Sample(id = 'a', set1 = Set(id = 'set1', data = [], symbolSize = 10)),
                B = Sample(id = 'b', set1 = Set(id = 'set1', data = [2023], symbol_size = 5, line_type = 'solid')),
                after get_merged_smp(A, B), A will be Sample(id = 'a', 'set1' = Set(id = 'set1', data = [],
                                                        symbol_size = 10, line_type = 'solid'))
    """
    def get_similar_name(_name: str):
        res = []
        for i in range(len(_name) + 1):
            str_list = [i for i in _name]
            str_list.insert(i, '_')
            res.append(''.join(str_list))
        for i in range(len(_name)):
            str_list = [i for i in _name]
            str_list[i] = str_list[i].capitalize()
            res.append(''.join(str_list))
        for i in range(len(_name)):
            str_list = [i for i in _name]
            if _name[i] in '-_':
                str_list.pop(i)
                res.append(''.join(str_list))
        return res

    if not isinstance(b, dict):
        b = b.__dict__

    for name, attr in b.items():
        if hasattr(a, name):
            if isinstance(attr, (samples.Plot, samples.Table, samples.Info, samples.Plot.BasicAttr)):
                if not type(getattr(a, name)) == type(attr):
                    setattr(a, name, type(attr)())
                get_merged_smp(getattr(a, name), attr)
            if isinstance(attr, dict) and isinstance(getattr(a, name), dict):
                setattr(a, name, basic_funcs.mergeDicts(getattr(a, name), attr))
            if isinstance(attr, list) and isinstance(getattr(a, name), list):
                if len(attr) > len(getattr(a, name)):
                    setattr(a, name, getattr(a, name) + attr[len(getattr(a, name)):])
            continue
        else:
            for xxx in get_similar_name(name):
                for xx in get_similar_name(xxx):
                    for x in get_similar_name(xx):
                        if hasattr(a, x):
                            # print(f'Has similar {name} = {x}: {getattr(a, x)}')
                            setattr(a, name, getattr(a, x))
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break
            if not hasattr(a, name):
                setattr(a, name, attr)


def get_components(sample: samples.Sample):
    """
    Get updated sample.Components dict
    """
    components_name = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8',
        'figure_1', 'figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6', 'figure_7', 'figure_8', 'figure_9',
    ]
    components = {}
    for key in components_name:
        comp = get_component_byid(sample, key)
        components.update({key: comp})
    return components


def get_component_byid(sample: samples.Sample, comp_id: str):
    """
    Get a component (Table or Plot) based on input id
    """
    for key, val in sample.__dict__.items():
        if isinstance(val, (samples.Plot, samples.Table, samples.Info)) and getattr(val, 'id') == comp_id:
            return val


def get_plot_set(plot: samples.Plot, comp_id):
    """
    Get a Set, Text, Axis, Label of a sample instance based on given id
    """
    for v in [getattr(plot, k) for k in dir(plot)]:
        if isinstance(v, samples.Plot.BasicAttr) and v.id.lower() == comp_id.lower():
            return v
    return None


def update_table_data(sample: samples.Sample):
    for key, comp in get_components(sample).items():
        if type(comp) == samples.Table:
            if key == '1':
                data = basic_funcs.setTableData(
                    sample.SequenceName, sample.SequenceValue, *sample.SampleIntercept)
            elif key == '2':
                data = basic_funcs.setTableData(
                    sample.SequenceName, sample.SequenceValue, *sample.BlankIntercept)
            elif key == '3':
                data = basic_funcs.setTableData(
                    sample.SequenceName, sample.SequenceValue, *sample.CorrectedValues)
            elif key == '4':
                data = basic_funcs.setTableData(
                    sample.SequenceName, sample.SequenceValue, *sample.DegasValues)
            elif key == '5':
                data = basic_funcs.setTableData(
                    sample.SequenceName, sample.SequenceValue, *sample.PublishValues)
            elif key == '6':
                data = basic_funcs.setTableData(
                    sample.SequenceName, sample.SequenceValue, *sample.ApparentAgeValues)
            elif key == '7':
                data = basic_funcs.setTableData(
                    sample.SequenceName, sample.SequenceValue, sample.IsochronMark, *sample.IsochronValues)
            elif key == '8':
                data = basic_funcs.setTableData(
                    sample.SequenceName, sample.SequenceValue, *sample.TotalParam)
            else:
                data = [['']]
            setattr(comp, 'data', data)


# Reduction functions
def corr_blank(sample: samples.Sample):
    """Blank Correction"""
    corrBlank = sample.TotalParam[102][0]
    set_negative_zero = sample.TotalParam[101][0]
    if not corrBlank:
        sample.BlankCorrected = copy.deepcopy(sample.SampleIntercept)
        sample.CorrectedValues = copy.deepcopy(sample.BlankCorrected)
        return
    blank_corrected = [[]]*10
    try:
        for i in range(5):
            blank_corrected[i * 2:2 + i * 2] = calc_funcs.corr_blank(
                *sample.SampleIntercept[i * 2:2 + i * 2], *sample.BlankIntercept[i * 2:2 + i * 2])
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError('Blank correction error')
    if set_negative_zero:
        blank_corrected[0] = [i if i >= 0 else 0 for i in blank_corrected[0]]
    sample.BlankCorrected = blank_corrected
    sample.CorrectedValues = copy.deepcopy(sample.BlankCorrected)


def corr_massdiscr(sample: samples.Sample):
    """Mass Discrimination Correction"""
    corrMassdiscr = sample.TotalParam[103][0]
    if not corrMassdiscr:
        sample.MassDiscrCorrected = copy.deepcopy(sample.BlankCorrected)
        sample.CorrectedValues = copy.deepcopy(sample.MassDiscrCorrected)
        return
    MASS = sample.TotalParam[71:81]
    mdf_corrected = [[]]*10
    try:
        for i in range(5):
            mdf_corrected[i * 2:2 + i * 2] = calc_funcs.corr_discr(
                *sample.BlankCorrected[i * 2:2 + i * 2],
                *sample.TotalParam[69:71], m=MASS[i*2], m40=MASS[8], isRelative=True,
                method=sample.TotalParam[100][0])
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError('Mass discrimination correction error')
    sample.MassDiscrCorrected = mdf_corrected
    sample.CorrectedValues = copy.deepcopy(sample.MassDiscrCorrected)


def corr_decay(sample: samples.Sample):
    """Ar37 and Ar39 Decay Correction"""
    decay_corrected = [[]]*10
    try:
        irradiation_cycles = [list(filter(None, re.split(r'[DS]', each_step))) for each_step in sample.TotalParam[27]]
        t1 = [i.split('-') for i in sample.TotalParam[31]]  # t1: experimental times
        t2, t3 = [], []  # t2: irradiation times, t3: irradiation durations
        for each_step in irradiation_cycles:
            t2.append([item.split('-') for i, item in enumerate(each_step) if i % 2 == 0])
            t3.append([item for i, item in enumerate(each_step) if i % 2 == 1])
        decay_corrected[2:4] = calc_funcs.corr_decay(
            *sample.MassDiscrCorrected[2:4], t1, t2, t3, *sample.TotalParam[44:46], isRelative=True)
        decay_corrected[6:8] = calc_funcs.corr_decay(
            *sample.MassDiscrCorrected[6:8], t1, t2, t3, *sample.TotalParam[42:44], isRelative=True)
        # Negative number set to zero in decay correction
        decay_corrected[2] = [0 if i < 0 else i for i in decay_corrected[2]]
        decay_corrected[6] = [0 if i < 0 else i for i in decay_corrected[6]]
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError('Decay correction correction error')

    corrDecay37 = sample.TotalParam[104][0]
    corrDecay39 = sample.TotalParam[105][0]
    if corrDecay37:
        sample.CorrectedValues[2:4] = copy.deepcopy(decay_corrected[2:4])
    if corrDecay39:
        sample.CorrectedValues[6:8] = copy.deepcopy(decay_corrected[6:8])


def calc_degas_ca(sample: samples.Sample):
    """Degas Pattern for Ca"""
    corrDecasCa = sample.TotalParam[106][0]
    n = len(sample.CorrectedValues[2])
    ar37ca = sample.CorrectedValues[2:4]
    ar39ca = calc_funcs.list_mul(*ar37ca, *sample.TotalParam[8:10], isRelative=True)
    ar38ca = calc_funcs.list_mul(*ar37ca, *sample.TotalParam[10:12], isRelative=True)
    ar36ca = calc_funcs.list_mul(*ar37ca, *sample.TotalParam[12:14], isRelative=True)
    sample.DegasValues[8:10] = ar37ca
    sample.DegasValues[22:24] = ar39ca if corrDecasCa else [[0] * n, [0] * n]
    sample.DegasValues[18:20] = ar38ca if corrDecasCa else [[0] * n, [0] * n]
    sample.DegasValues[4:6] = ar36ca if corrDecasCa else [[0] * n, [0] * n]
    sample.PublishValues[1] = ar37ca[0]


def calc_degas_k(sample: samples.Sample):
    """Degas Pattern for K"""
    corrDecasK = sample.TotalParam[107][0]
    set_negative_zero = sample.TotalParam[101][0]
    n = len(sample.CorrectedValues[6])
    ar39k = calc_funcs.list_sub(*sample.CorrectedValues[6:8], *sample.DegasValues[22:24])
    ar39k[0] = [0 if i < 0 and set_negative_zero else i for i in ar39k[0]]
    ar40k = calc_funcs.list_mul(*ar39k, *sample.TotalParam[14:16], isRelative=True)
    ar38k = calc_funcs.list_mul(*ar39k, *sample.TotalParam[16:18], isRelative=True)

    sample.PublishValues[3] = ar39k[0]
    sample.DegasValues[20:22] = ar39k
    sample.DegasValues[30:32] = ar40k if corrDecasK else [[0] * n, [0] * n]
    sample.DegasValues[16:18] = ar38k if corrDecasK else [[0] * n, [0] * n]


def calc_degas_cl(sample: samples.Sample):
    """Degas Pattern for Cl"""
    corrDecasCl = sample.TotalParam[108][0]
    decay_const = sample.TotalParam[46:48]
    cl36_cl38_p = sample.TotalParam[56:58]
    ar38ar36 = sample.TotalParam[4:6]
    stand_time_year = sample.TotalParam[32]
    set_negative_zero = sample.TotalParam[101][0]
    # ============
    decay_const[1] = [decay_const[0][i] * decay_const[1][i] / 100 for i in
                      range(len(decay_const[0]))]  # convert to absolute error
    cl36_cl38_p[1] = [cl36_cl38_p[0][i] * cl36_cl38_p[1][i] / 100 for i in
                      range(len(cl36_cl38_p[0]))]  # convert to absolute error
    # convert to absolute error
    ar38ar36[1] = [ar38ar36[0][i] * ar38ar36[1][i] / 100 for i in range(len(ar38ar36[0]))]
    # ============
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl
    ar36acl = calc_funcs.list_sub(*sample.CorrectedValues[0:2], *sample.DegasValues[4:6])
    # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl
    ar38acl = calc_funcs.list_sub(*calc_funcs.list_sub(
        *sample.CorrectedValues[4:6], *sample.DegasValues[16:18]), *sample.DegasValues[18:20])
    if set_negative_zero:
        for index, item in enumerate(ar36acl[0]):
            if item < 0:
                ar36acl[0][index] = 0
            if ar38acl[0][index] < 0:
                ar38acl[0][index] = 0
    try:
        if not corrDecasCl:
            raise ValueError("Do not apply degas chlorine")
        v3 = [cl36_cl38_p[0][i] * (1 - exp(-1 * decay_const[0][i] * stand_time_year[i])) for i in
              range(len(stand_time_year))]
        s3 = [pow((cl36_cl38_p[1][i] * (1 - exp(-1 * decay_const[0][i] * stand_time_year[i]))) ** 2 +
                  (cl36_cl38_p[0][i] * stand_time_year[i] * (exp(-1 * decay_const[0][i] * stand_time_year[i])) *
                   decay_const[1][i]) ** 2, 0.5) for i in range(len(stand_time_year))]
        s3 = [calc_funcs.error_div((1, 0), (v3[i], s3[i])) for i in range(len(s3))]
        v3 = [1 / v3[i] for i in range(len(v3))]
        # 36ArCl
        ar36cl = [[], []]
        ar36cl[0] = [(ar36acl[0][i] * ar38ar36[0][i] - ar38acl[0][i]) / (ar38ar36[0][i] - v3[i])
                     for i in range(len(ar36acl[0]))]
        s1 = [(ar36acl[1][i] * ar38ar36[0][i] / (ar38ar36[0][i] - v3[i])) ** 2 for i in range(len(ar36cl[0]))]
        s2 = [(ar38acl[1][i] / (ar38ar36[0][i] - v3[i])) ** 2 for i in range(len(ar36cl[0]))]
        s3 = [(s3[i] * (ar36acl[0][i] * ar38ar36[0][i] - ar38acl[0][i]) / (ar38ar36[0][i] - v3[i]) ** 2) ** 2
              for i in range(len(ar36cl[0]))]
        s4 = [(ar36acl[0][i] / (ar38ar36[0][i] - v3[i]) -
               (ar36acl[0][i] * ar38ar36[0][i] - ar38acl[0][i]) / (ar38ar36[0][i] - v3[i]) ** 2) ** 2 *
              (ar38ar36[1][i]) ** 2 for i in range(len(ar36cl[0]))]
        ar36cl[1] = [pow(s1[i] + s2[i] + s3[i] + s4[i], 0.5) for i in range(len(ar36cl[0]))]

        # 38ArCl
        ar38cl = [[], []]
        ar38cl[1] = [calc_funcs.error_mul(
            (ar36cl[0][i], ar36cl[1][i]), (v3[i], s3[i])) for i in range(len(ar36cl[0]))]
        ar38cl[0] = [ar36cl[0][i] * v3[i] for i in range(len(ar36cl[0]))]

        # Negative number set to zero
        ar36cl[0] = [0 if i < 0 and set_negative_zero else i for i in ar36cl[0]]
        # force 36ArCl to zero if 36Ar - 36ArCa - 36Cl < 0
        ar36cl[0] = [0 if ar36acl[0][i] - item < 0 and set_negative_zero else item
                     for i, item in enumerate(ar36cl[0])]

    except Exception as e:
        print('Error in corr Cl: {}, lines: {}'.format(e, e.__traceback__.tb_lineno))
        n = len(ar36acl[0])
        ar36cl = [[0] * n, [0] * n]
        ar38cl = [[0] * n, [0] * n]
    sample.DegasValues[6:8] = ar36cl
    sample.DegasValues[10:12] = ar38cl
    sample.PublishValues[2] = ar38cl[0]


def calc_degas_atm(sample: samples.Sample):
    """Degas for Atmospheric Gas """
    corrDecasAtm = sample.TotalParam[109][0]
    set_negative_zero = sample.TotalParam[101][0]
    n = len(sample.CorrectedValues[0])
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl
    ar36acl = calc_funcs.list_sub(*sample.CorrectedValues[0:2], *sample.DegasValues[4:6])
    if set_negative_zero:
        ar36acl[0] = [i if i >= 0 else 0 for i in ar36acl[0]]
    # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl
    # ar38acl = calc_funcs.list_sub(
    #     *calc_funcs.list_sub(*sample.CorrectedValues[2:4], *sample.DegasValues[16:18]), *sample.DegasValues[18:20])
    # 36ArAir
    ar36a = calc_funcs.list_sub(*ar36acl, *sample.DegasValues[6:8])
    # If ar36acl - ar36cl < 0, let ar36a = ar36 - ar36ca
    if set_negative_zero:
        ar36a[0] = [item if item >= 0 else ar36acl[index] for index, item in enumerate(ar36a[0])]
    # 38ArAir
    ar38a = calc_funcs.list_mul(*ar36a, *sample.TotalParam[4:6], isRelative=True)
    # 40ArAir
    ar40a = calc_funcs.list_mul(*ar36a, *sample.TotalParam[0:2], isRelative=True)
    sample.DegasValues[0:2] = ar36a
    sample.DegasValues[12:14] = ar38a if corrDecasAtm else [[0] * n, [0] * n]
    sample.DegasValues[26:28] = ar40a if corrDecasAtm else [[0] * n, [0] * n]
    sample.PublishValues[0] = ar36a[0]


def calc_degas_r(sample: samples.Sample):
    """Degas for Radiogenic Ar40"""
    ar40ar = calc_funcs.list_sub(*sample.CorrectedValues[8:10], *sample.DegasValues[30:32])
    ar40r = calc_funcs.list_sub(*ar40ar, *sample.DegasValues[26:28])
    ar40r[0] = [item if item >= 0 else 0 for item in ar40r[0]]
    sample.DegasValues[24:26] = ar40r
    sample.PublishValues[4] = ar40r[0]


def calc_ratio(sample: samples.Sample):
    ar40r_percent = [item / sample.CorrectedValues[8][index] * 100 if sample.CorrectedValues[8][index] != 0 else 0
                     for index, item in enumerate(sample.DegasValues[24])]
    sum_ar39k = sum(sample.DegasValues[20])
    ar39k_percent = [item / sum_ar39k * 100 if sum_ar39k != 0 else 0 for item in sample.DegasValues[20]]
    ar40rar39k = calc_funcs.list_mul(
        *sample.DegasValues[24:26], *calc_funcs.list_rcpl(*sample.DegasValues[20:22], isRelative=False),
        isRelative=False)
    CaK = calc_funcs.list_mul(*calc_funcs.list_mul(
        *sample.DegasValues[8:10], *calc_funcs.list_rcpl(*sample.DegasValues[20:22], isRelative=False)),
                              *calc_funcs.list_rcpl(*sample.TotalParam[20:22], isRelative=True))
    isochron_1 = calc_funcs.get_isochron(
        *sample.DegasValues[20:22], *calc_funcs.list_sub(
            *sample.CorrectedValues[8:10], *sample.DegasValues[30:32]), *sample.DegasValues[0:2])
    isochron_2 = calc_funcs.get_isochron(
        *sample.DegasValues[20:22], *sample.DegasValues[0:2], *calc_funcs.list_sub(
            *sample.CorrectedValues[8:10], *sample.DegasValues[30:32]))
    isochron_3 = calc_funcs.get_isochron(
        *sample.DegasValues[20:22], *sample.DegasValues[24:26], *sample.DegasValues[10:12])
    isochron_4 = calc_funcs.get_isochron(
        *sample.DegasValues[20:22], *sample.DegasValues[10:12], *sample.DegasValues[24:26])
    isochron_5 = calc_funcs.get_isochron(
        *sample.DegasValues[10:12], *sample.DegasValues[24:26], *sample.DegasValues[20:22])

    # assignation
    sample.ApparentAgeValues[0:2] = ar40rar39k
    sample.ApparentAgeValues[6:8] = [ar40r_percent, ar39k_percent]
    sample.PublishValues[7:11] = [ar40r_percent, ar39k_percent, *CaK]
    sample.IsochronValues = [[]] * 39
    sample.IsochronValues[0:5] = isochron_1
    sample.IsochronValues[6:11] = isochron_2
    sample.IsochronValues[12:17] = isochron_3
    sample.IsochronValues[18:23] = isochron_4
    sample.IsochronValues[24:29] = isochron_5

    # === Cl-Atm-Correlation Plot ===
    # === Ar values ===
    # 3D ratio, 36Ar(a+cl)/40Ar(a+r), 38Ar(a+cl)/40Ar(a+r), 39Ar(k)/40Ar(a+r),
    ar40ar = calc_funcs.list_sub(*sample.CorrectedValues[8:10], *sample.DegasValues[30:32])
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl (and also 36Arc)
    ar36acl = calc_funcs.list_sub(*sample.CorrectedValues[0:2], *sample.DegasValues[4:6])
    # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl (and also 38Arc)
    ar38acl = calc_funcs.list_sub(*calc_funcs.list_sub(*sample.CorrectedValues[4:6], *sample.DegasValues[16:18]), *sample.DegasValues[18:20])
    # 38ArCl
    ar38cl = sample.DegasValues[10:12]
    # 39ArK
    ar39k = sample.DegasValues[20:22]
    # isochron_6 = calc_funcs.get_3D_isochron(*ar36acl, *ar38acl, *ar40ar, *ar39k)
    isochron_6 = calc_funcs.get_3D_isochron(*ar36acl, *ar38acl, *ar39k, *ar40ar)  # Points on the plot will be more disperse than the above
    sample.IsochronValues[30:39] = isochron_6

    # a = [
    #         [i - sum(ar36acl[0]) / len(ar36acl[0]) for i in ar36acl[0]],
    #         [i - sum(ar38acl[0]) / len(ar38acl[0]) for i in ar38acl[0]],
    #         [i - sum(ar40ar[0]) / len(ar40ar[0]) for i in ar40ar[0]],
    # ]  # centralization
    # a_transposed = basic_funcs.getTransposed(a)
    # cov = basic_funcs.getProducted(a, a_transposed, len(ar40ar[0]) - 1)
    # print(f"cov = {cov}")

    # np = min([len(ar36acl[0]), len(ar38acl[0]), len(ar39k[0]), len(ar40ar[0])])  # number of points plotted
    # # === Cl parameters ===
    # ar40ar36trap = sample.TotalParam[0:2]
    # ar38ar36trap = sample.TotalParam[4:6]
    # decay_const = sample.TotalParam[46:48]
    # cl36_cl38_p = sample.TotalParam[56:58]
    # stand_time_year = sample.TotalParam[32]
    # decay_const[1] = [
    #     decay_const[0][i] * decay_const[1][i] / 100 for i in range(len(decay_const[0]))]  # convert to absolute error
    # cl36_cl38_p[1] = [
    #     cl36_cl38_p[0][i] * cl36_cl38_p[1][i] / 100 for i in range(len(cl36_cl38_p[0]))]  # convert to absolute error
    # PQ = [cl36_cl38_p[0][i] * (1-exp(-1*decay_const[0][i]*stand_time_year[i])) for i in range(len(cl36_cl38_p[0]))]
    # print(f"PQ = {PQ}")
    # print(f"PQ_max = {max(PQ)}, PQ_min = {min(PQ)}, average = {sum(PQ) / len(PQ)}")
    # a = [PQ[i] * 298.56 / (0.1885 * PQ[i] - 1) for i in range(len(PQ))]
    # print(f"a = {a}")
    # print(f"a_max = {max(a)}, a_min = {min(a)}, average = {sum(a) / len(a)}")


    # === Calculation ===
    # v3 = [cl36_cl38_p[0][i] * (1 - exp(-1 * decay_const[0][i] * stand_time_year[i])) for i in
    #       range(len(stand_time_year))]
    # s3 = [pow((cl36_cl38_p[1][i] * (1 - exp(-1 * decay_const[0][i] * stand_time_year[i]))) ** 2 +
    #           (cl36_cl38_p[0][i] * stand_time_year[i] * (exp(-1 * decay_const[0][i] * stand_time_year[i])) *
    #            decay_const[1][i]) ** 2, 0.5) for i in range(len(stand_time_year))]
    # sQ = [calc_funcs.error_div((1, 0), (v3[i], s3[i])) for i in range(len(s3))]
    # Q = [1 / v3[i] for i in range(len(v3))]
    # x1 = [(ar40ar[0][i] + ar36acl[0][i]) / (Q[i] * ar39k[0][i]) for i in range(np)]
    # x2 = [ar36acl[0][i] / (Q[i] * ar39k[0][i]) for i in range(np)]
    # x3 = [(ar38acl[0][i] - Q[i] * ar36acl[0][i]) / (Q[i] * ar39k[0][i]) for i in range(np)]
    # x4 = v3
    # y = [ar40ar[0][i] / ar39k[0][i] for i in range(np)]
    # === Isochron data ===
    # isochron_7 = [x1, [0] * np, x2, [0] * np, x3, [0] * np, x4, [0] * np, y, [0] * np]
    # sample.IsochronValues[37:47] = isochron_7
    # Q = [(1 - exp(-1 * decay_const[0][i] * stand_time_year[i])) for i in range(len(stand_time_year))]
    # sQ = [pow((cl36_cl38_p[0][i] * stand_time_year[i] * (exp(-1 * decay_const[0][i] * stand_time_year[i])) *
    #            decay_const[1][i]) ** 2, 0.5) for i in range(len(stand_time_year))]
    #
    # y = [ar40ar[0][i] / ar39k[0][i] if ar39k[0][i] !=0 else 0 for i in range(np)]
    # x1 = [ar36acl[0][i] / ar39k[0][i] if ar39k[0][i] !=0 else 0 for i in range(np)]
    # x2 = [ar38acl[0][i] / ar39k[0][i] if ar39k[0][i] !=0 else 0 for i in range(np)]

    # _1, _2, _3 = basic_funcs.getIsochronSetData([x1, x2, x3, x4, y], sample.SelectedSequence1, sample.SelectedSequence2, sample.UnselectedSequence)
    # with open('all_data.txt', 'w+') as f:
    #     for i in basic_funcs.getTransposedArry(_1):
    #         a = '  '.join([str(j) for j in i]) + '\n'
    #         f.writelines([a])
    #
    # with open('set_2_data.txt', 'w+') as f:
    #     for i in basic_funcs.getTransposedArry(_2):
    #         a = '  '.join([str(j) for j in i]) + '\n'
    #         f.writelines([a])
    #
    # with open('set_3_data.txt', 'w+') as f:
    #     for i in basic_funcs.getTransposedArry(_3):
    #         a = '  '.join([str(j) for j in i]) + '\n'
    #         f.writelines([a])

    # === Isochron data ===
    # isochron_7 = [x1, [0] * np, x2, [0] * np, y, [0] * np]
    # sample.IsochronValues[37:43] = isochron_7
    #
    # total_data = [y, x1, x2, Q]
    # with open('second_all_data.txt', 'w+') as f:
    #     for i in basic_funcs.getTransposedArry([x1, x2, Q, y]):
    #         a = '  '.join([str(j) for j in i]) + '\n'
    #         f.writelines([a])
    # print('========================== Total Data ================================')
    # r1, p, r2, f = calc_funcs.intercept_Cl_correlation(*total_data)
    # print(calc_age(f, 0, sample))
    # print('======================== End Total Data ==============================')
    # set1, set2, set3 = basic_funcs.getIsochronSetData(total_data, sample.SelectedSequence1, sample.SelectedSequence2, sample.UnselectedSequence)
    # print('========================== Set 1 ================================')
    # try:
    #     r1, p, r2, f = calc_funcs.intercept_Cl_correlation(*set1)
    #     print(calc_age(f, 0, sample))
    # except:
    #     pass
    # print('======================== End Set1 ==============================')
    # print('========================== Set 2 ================================')
    # try:
    #     r1, p, r2, f = calc_funcs.intercept_Cl_correlation(*set2)
    #     print(calc_age(f, 0, sample))
    # except:
    #     pass
    # print('======================== End Set2 ==============================')
    # print('========================== Set 3 ================================')
    # try:
    #     r1, p, r2, f = calc_funcs.intercept_Cl_correlation(*set3)
    #     print(calc_age(f, 0, sample))
    # except:
    #     pass
    # print('======================== End Set3 ==============================')


def get_plateau_results(sample: samples.Sample, sequence_index: list, ar40rar39k: list = None,
                        ar39k_percentage: list = None):
    def _get_partial(points, *args):
        return [arg[min(points): max(points) + 1] for arg in args]
    def _get_partial_spectra(points, *args):
        return [arg[2 * min(points): 2 * max(points) + 2] for arg in args]
    if len(sequence_index) == 0:
        return [[], []], [[], [], []], [0, 0, 0, 0], [0, 0, 0, 0], ''
    if ar40rar39k is None:
        ar40rar39k = sample.ApparentAgeValues[0:2]
    if ar39k_percentage is None:
        ar39k_percentage = sample.ApparentAgeValues[7]

    age = [calc_age(ar40rar39k[0][i], ar40rar39k[1][i], sample) for i in range(len(ar40rar39k[0]))]
    age = basic_funcs.getTransposed(age)[0:2]
    plot_data = _get_partial_spectra(sequence_index, *list(calc_funcs.get_spectra(*age, ar39k_percentage)))
    f_values = _get_partial(sequence_index, *ar40rar39k)
    age = _get_partial(sequence_index, *age)
    sum_ar39k = sum(_get_partial(sequence_index, ar39k_percentage)[0])
    # Close the spectrum
    if plot_data[0][0] > 0:
        y = (plot_data[1][0] + plot_data[2][0]) / 2
        plot_data[0].insert(0, plot_data[0][0])
        plot_data[1].insert(0, y)
        plot_data[2].insert(0, y)
    if plot_data[0][-1] < 100:
        y = (plot_data[1][-1] + plot_data[2][-1]) / 2
        plot_data[0].append(plot_data[0][-1])
        plot_data[1].append(y)
        plot_data[2].append(y)

    if len(sequence_index) >= 2 and age != []:
        wmf = calc_funcs.err_wtd_mean(*f_values)
        wmage = calc_age(*wmf[0:2], sample)
    else:
        wmf = [0, 0, len(sequence_index), 0, 0, 0]
        wmage = [0, 0, 0, 0]
    text = f't = {wmage[0]:.2f} ± {wmage[1]:.2f} | {wmage[2]:.2f} | {wmage[3]:.2f} Ma\n' \
           f'WMF = {wmf[0]:.2f} ± {wmf[1]:.2f}, n = {wmf[2]}\n' \
           f'MSWD = {wmf[3]:.2f}, ∑{{sup|39}}Ar = {sum_ar39k:.2f}%\n' \
           f'χ{{sup|2}} = {wmf[4]:.2f}, p = {wmf[5]:.2f}'
    return age, plot_data, wmf[0:4], wmage, text


def recalc_plateaus(sample: samples.Sample, **kwargs):
    try:
        if sample.AgeSpectraPlot.initial_params['useNormalInitial']:
            r_1, sr_1 = sample.NorIsochronPlot.set1.info[1]
            r_2, sr_2 = sample.NorIsochronPlot.set2.info[1]
        elif sample.AgeSpectraPlot.initial_params['useInverseInitial']:
            r_1, sr_1 = sample.InvIsochronPlot.set1.info[1]
            r_2, sr_2 = sample.InvIsochronPlot.set2.info[1]
        else:
            [r_1, sr_1, r_2, sr_2] = sample.AgeSpectraPlot.initial_params['useInputInitial']
    except Exception as e:
        r_1 = r_2 = 298.56
        sr_1 = sr_2 = 0.31
    initial_1 = kwargs.get('initial_r_1', r_1)
    initial_2 = kwargs.get('initial_r_2', r_2)
    s_initial_1 = kwargs.get('s_initial_r_1', sr_1)
    s_initial_2 = kwargs.get('s_initial_r_2', sr_2)

    def _get_ar40rar39k(r, sr):
        ar36a = sample.DegasValues[0:2]
        ar39k = sample.DegasValues[20:22]
        ar40rar39k = sample.ApparentAgeValues[0:2]
        try:
            # Try calculate based on corrected values
            # 40ArAir, sR is absolute error
            ar40a = calc_funcs.list_mul(*ar36a, [r] * len(ar36a[0]), [sr] * len(ar36a[0]), isRelative=False)
            ar40ar = calc_funcs.list_sub(*sample.CorrectedValues[8:10], *sample.DegasValues[30:32])
            if max(ar40ar[0]) <= 0:
                raise ValueError('Corrected lists are empty')
            ar40r = calc_funcs.list_sub(*ar40ar, *ar40a)
            ar40rar39k = calc_funcs.list_mul(
                *ar40r, *calc_funcs.list_rcpl(*ar39k, isRelative=False), isRelative=False)
        except Exception as e:
            ar40r = sample.DegasValues[24:26]
            old_R = sample.TotalParam[0][0]
            s_old_R = sample.TotalParam[1][0] * sample.TotalParam[0][0] / 100
            ar40rar39k = [
                [(ar40r[0][i] + ar36a[0][i] * (old_R - r)) / ar39k[0][i] if ar39k[0][i] != 0 else 0 for i in
                 range(min([len(ar40r[0]), len(ar36a[0])]))],
                [calc_funcs.error_div(
                    ((ar40r[0][i] + ar36a[0][i] * (old_R - r)),
                     calc_funcs.error_add(ar40r[0][i], calc_funcs.error_mul(
                             (ar36a[0][i], ar36a[0][i]), (old_R - r, calc_funcs.error_add(s_old_R, sr))))),
                    (ar39k[0][i], ar39k[0][i])) if ar39k[0][i] != 0 else 0
                 for i in range(min([len(ar40r[0]), len(ar36a[0])]))]
            ]
        finally:
            return ar40rar39k

    # Get ages and linepoints for each set
    set1_age, set1_data, set1_wmf, set1_wmage, sample.AgeSpectraPlot.text1.text = \
        get_plateau_results(sample, sample.SelectedSequence1, _get_ar40rar39k(initial_1, s_initial_1))
    set2_age, set2_data, set2_wmf, set2_wmage, sample.AgeSpectraPlot.text2.text = \
        get_plateau_results(sample, sample.SelectedSequence2, _get_ar40rar39k(initial_2, s_initial_2))
    # Get weighted mean age and parameters
    sample.AgeSpectraPlot.set1.info = [*set1_wmf, *set1_wmage]  # Info = weighted mean f, sf, np, mswd, age, s, s, s
    sample.AgeSpectraPlot.set2.info = [*set2_wmf, *set2_wmage]  # Info = weighted mean f, sf, np, mswd, age, s, s, s
    # Transpose
    sample.AgeSpectraPlot.set1.data = basic_funcs.getTransposed(set1_data)
    sample.AgeSpectraPlot.set2.data = basic_funcs.getTransposed(set2_data)

    # record results
    get_component_byid(sample=sample, comp_id="0").results.set1["plateau_mswd"] = set1_wmf[-1]
    get_component_byid(sample=sample, comp_id="0").results.set1["plateau_chisq"] = set1_wmf[-1]
    get_component_byid(sample=sample, comp_id="0").results.set1["plateau_pvalue"] = set1_wmf[-1]

    #"""3D corrected plateaus"""
    # 3D ratio, 36Ar(a+cl)/40Ar(a+r), 38Ar(a+cl)/40Ar(a+r), 39Ar(k)/40Ar(a+r),
    ar40ar = calc_funcs.list_sub(*sample.CorrectedValues[8:10], *sample.DegasValues[30:32])
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl
    ar36acl = calc_funcs.list_sub(*sample.CorrectedValues[0:2], *sample.DegasValues[4:6])
    # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl
    ar38acl = calc_funcs.list_sub(*calc_funcs.list_sub(*sample.CorrectedValues[4:6], *sample.DegasValues[16:18]), *sample.DegasValues[18:20])
    # 39ArK
    ar39k = sample.DegasValues[20:22]
    # 40Arr
    def get_modified_f(c, sc, a, sa, b, sb):
        ar40r = list(map(lambda zi, xi, yi: zi - a * xi - b * yi, ar40ar[0], ar36acl[0], ar38acl[0]))
        sar40r = list(map(lambda zi, szi, xi, sxi, yi, syi:
                          calc_funcs.error_add(szi, calc_funcs.error_mul((xi, sxi), (a, sa)),
                                               calc_funcs.error_mul((yi, syi), (b, sb))),
                          *ar40ar, *ar36acl, *ar38acl))
        f = list(map(lambda ar40ri, ar39ki: ar40ri / ar39ki, ar40r, ar39k[0]))
        sf = list(map(lambda ar40ri, sar40ri, ar39ki, sar39ki:
                      calc_funcs.error_div((ar40ri, sar40ri), (ar39ki, sar39ki)),
                      ar40r, sar40r, *ar39k))
        return [f, sf]

    isochron_7 = calc_funcs.get_3D_isochron(*ar36acl, *ar38acl, *ar40ar, *ar39k)
    [set1_data, set2_data, set3_data] = basic_funcs.getIsochronSetData(
        isochron_7, sample.SelectedSequence1, sample.SelectedSequence2, sample.UnselectedSequence)

    __isochron_7 = calc_funcs.get_3D_isochron(*ar36acl, *ar38acl, *ar39k, *ar40ar)
    [__set1_data, __set2_data, __set3_data] = basic_funcs.getIsochronSetData(
        __isochron_7, sample.SelectedSequence1, sample.SelectedSequence2, sample.UnselectedSequence)

    def __get_modified_f(c, sc, a, sa, b, sb):
        f = list(map(lambda zi, xi, yi: 1 / (zi - a * xi - b * yi), __isochron_7[4], __isochron_7[0], __isochron_7[2]))
        sf = [0] * len(f)
        return [f, sf]

    # set 1:
    try:
        k = calc_funcs.wtd_3D_regression(*set1_data[:9])
        set1_ar40rar39k = get_modified_f(*k[:6])

        # __k = calc_funcs.wtd_3D_regression(*__set1_data[:9])
        # __set1_ar40rar39k = __get_modified_f(*__k[:6])
        #
        # for i in range(len(set1_ar40rar39k[0])):
        #     print(f"{set1_ar40rar39k[0][i]} == {__set1_ar40rar39k[0][i]}")
        #
        # k = calc_funcs.wtd_3D_regression(*__set1_data[:9])
        # set1_ar40rar39k = __get_modified_f(*k[:6])

    except:
        print(traceback.format_exc())
        set1_ar40rar39k = [[0] * len(ar39k[0]), [0] * len(ar39k[0])]
    # set 2:
    try:
        k = calc_funcs.wtd_3D_regression(*set2_data[:9])
        set2_ar40rar39k = get_modified_f(*k[:6])
    except:
        set2_ar40rar39k = [[0] * len(ar39k[0]), [0] * len(ar39k[0])]
    set4_age, set4_data, set4_wmf, set4_wmage, set4_text = \
        get_plateau_results(sample, sample.SelectedSequence1, set1_ar40rar39k)
    set5_age, set5_data, set5_wmf, set5_wmage, set5_text = \
        get_plateau_results(sample, sample.SelectedSequence2, set2_ar40rar39k)
    # Set set4 and set5
    sample.AgeSpectraPlot.set4.data = basic_funcs.getTransposed(set4_data)
    sample.AgeSpectraPlot.set5.data = basic_funcs.getTransposed(set5_data)
    sample.AgeSpectraPlot.set4.info = [*set4_wmf, *set4_wmage]  # Info = weighted mean f, sf, np, mswd, age, s, s, s
    sample.AgeSpectraPlot.set5.info = [*set5_wmf, *set5_wmage]  # Info = weighted mean f, sf, np, mswd, age, s, s, s
    # """end"""


def recalc_isochrons(sample: samples.Sample, **kwargs):
    def _get_isochron_results(data: list, figure_type: int = 0, isClplot: bool = False):
        """
        data: isochron data, [[x: float], [sx: float], [y: float], [sy: float], [ri: float]]
        figure_type: int, 0 = None, 1 = normal, intercept is initial, slop is f,
                    2 = inverse, 3 = K-Cl-Ar plot 3
        """
        york_res, initial, f_value, age, text =[0]*11, [0, 0], [0, 0], [0]*4, ''
        if len(data[0]) >= 3:
            try:
                york_res = calc_funcs.wtd_york2_regression(*data[0:5])
            except Exception as e:
                print(f"Error in using york regression: {e}")
                return york_res, initial, f_value, age, text
            # york_res = intercept -> [0:2], slope -> [2:4], mswd -> [4], convergence -> [5], iteration -> [6],
            #            magnification -> [7], r2 -> [8]
            # Calculate ages
            if not york_res or york_res[0] == 0:
                return [0]*9, initial, f_value, age, text
            if figure_type == 1:
                initial, f_value = york_res[0:2], york_res[2:4]
            elif figure_type == 2:
                initial = [1 / york_res[0], calc_funcs.error_div((1, 0), (york_res[0], york_res[1]))]
                k = calc_funcs.wtd_york2_regression(data[2], data[3], data[0], data[1], data[4])
                f_value = [1 / k[0], calc_funcs.error_div((1, 0), (k[0], k[1]))]
            elif figure_type == 3:
                initial, f_value = york_res[2:4], york_res[0:2]
            age = calc_age(*f_value, sample)  # age, analytical err, internal err, full external err

            initial_ratio_text = 'initial'
            if not isClplot:
                initial_ratio_text = f"({{sup|40}}Ar/{{sup|36}}Ar){{sub|0}}"
            if isClplot:
                initial_ratio_text = f"({{sup|40}}Ar/{{sup|38}}Ar){{sub|Cl}}"
            text = f't = {age[0]:.2f} ± {age[1]:.2f} | {age[2]:.2f} | {age[3]:.2f} Ma\n' \
                   f'{initial_ratio_text} = {initial[0]:.2f} ± {initial[1]:.2f}\n' \
                   f'MSWD = {york_res[4]:.2f}, R{{sup|2}} = {york_res[8]:.4f}\n' \
                   f'χ{{sup|2}} = {york_res[9]:.2f}, p = {york_res[10]:.2f}'
            if isClplot and (figure_type == 2 or figure_type == 3):
                f_values = calc_funcs.list_rcpl(*data[0:2], isRelative=False) if figure_type == 2 else data[2:4]
                wmf = calc_funcs.err_wtd_mean(*f_values)
                wmage = calc_age(*wmf[0:2], sample)
                text = text + "\n\n" + \
                       f'WMF = {wmf[0]:.2f} ± {wmf[1]:.2f}, MSWD = {wmf[3]:.2f}\n' \
                       f't = {wmage[0]:.2f} ± {wmage[1]:.2f} | {wmage[2]:.2f} | {wmage[3]:.2f} Ma\n' \
                       f'χ{{sup|2}} = {wmf[4]:.2f}, p = {wmf[5]:.2f}'
        return york_res[:9], initial, f_value, age, text

    isochron_dict = {
        'figure_2': {'isClplot': False, 'figure_type': 1, 'data_index': [0, 5], 'name': 'Normal Isochron'},
        'figure_3': {'isClplot': False, 'figure_type': 2, 'data_index': [6, 11], 'name': 'Inverse Isochron'},
        'figure_4': {'isClplot': True, 'figure_type': 1, 'data_index': [12, 17], 'name': 'Cl Correlation 1'},
        'figure_5': {'isClplot': True, 'figure_type': 2, 'data_index': [18, 23], 'name': 'Cl Correlation 2'},
        'figure_6': {'isClplot': True, 'figure_type': 3, 'data_index': [24, 29], 'name': 'Cl Correlation 3'},
        'figure_7': {'isClplot': False, 'figure_type': 0, 'data_index': [30, 39], 'name': 'Cl Correlation 3D'},
    }
    for key, val in isochron_dict.items():
        figure = get_component_byid(sample, key)
        # Changing selected sequence lists will change data lists, too
        figure.set3.data, figure.set1.data, figure.set2.data = \
            sample.UnselectedSequence, sample.SelectedSequence1, sample.SelectedSequence2
    for key, val in isochron_dict.items():
        figure = get_component_byid(sample, key)
        set_data = [set1_data, set2_data, set3_data] = basic_funcs.getIsochronSetData(
            figure.data, sample.SelectedSequence1, sample.SelectedSequence2, sample.UnselectedSequence)
        if key != 'figure_7':
            x_scale = calc_funcs.get_axis_scale(figure.data[0])
            # y_scale = [figure.yaxis.min, figure.yaxis.max]
            for index, _set in enumerate(['set1', 'set2']):
                york_res, initial, f_value, age, text = \
                    _get_isochron_results(set_data[index], figure_type=val['figure_type'], isClplot=val['isClplot'])
                if len([sample.SelectedSequence1, sample.SelectedSequence2][index]) < 3:
                    line_points = [[], []]
                    line_params = []
                else:
                    line_points = [
                        [x_scale[0], x_scale[0] * york_res[2] + york_res[0]],
                        [x_scale[1], x_scale[1] * york_res[2] + york_res[0]]
                    ]
                    line_params = [york_res[2], york_res[0]]
                setattr(getattr(figure, _set), 'info', [york_res, initial, f_value, age])
                setattr(getattr(figure, ['line1', 'line2'][index]), 'data', line_points)
                setattr(getattr(figure, ['line1', 'line2'][index]), 'info', line_params)
                setattr(getattr(figure, ['text1', 'text2'][index]), 'text', text)
        else:
            try:
                k = calc_funcs.wtd_3D_regression(*set1_data[:9])
                ar38ar36 = sample.TotalParam[4][0]
                ar40ar36 = (k[2] + k[4] * ar38ar36) * -1 / k[0]
                f = 1 / k[0]
                sf = calc_funcs.error_div((1, 0), (k[0], k[1]))
                try:
                    PQ = -1 * k[4] / k[2]
                    Q = 1 - exp(-1 * sample.TotalParam[46][0] * sum(sample.TotalParam[32]) / len(sample.TotalParam[32]))
                    P = PQ / Q
                except:
                    print(traceback.format_exc())
                    P = 0
                figure.set1.info = [k, calc_age(f, sf, sample), [ar38ar36, ar40ar36, P]]
            except:
                figure.set1.info = [[0] * 14, [0] * 4, [0, 0, 0]]
            try:
                k = calc_funcs.wtd_3D_regression(*set2_data[:9])
                ar38ar36 = sample.TotalParam[4][0]
                ar40ar36 = (k[2] + k[4] * ar38ar36) * -1 / k[0]
                f = 1 / k[0]
                sf = calc_funcs.error_div((1, 0), (k[0], k[1]))
                try:
                    PQ = -1 * k[4] / k[2]
                    Q = 1 - exp(-1 * sample.TotalParam[46][0] * sum(sample.TotalParam[32]) / len(sample.TotalParam[32]))
                    P = PQ / Q
                except:
                    print(traceback.format_exc())
                    P = 0
                figure.set2.info = [k, calc_age(f, sf, sample), [ar38ar36, ar40ar36, P]]
            except:
                figure.set2.info = [[0] * 14, [0] * 4, [0, 0, 0]]
            try:
                k = calc_funcs.wtd_3D_regression(*set3_data[:9])
                ar38ar36 = sample.TotalParam[4][0]
                ar40ar36 = (k[2] + k[4] * ar38ar36) * -1 / k[0]
                f = 1 / k[0]
                sf = calc_funcs.error_div((1, 0), (k[0], k[1]))
                try:
                    PQ = -1 * k[4] / k[2]
                    Q = 1 - exp(-1 * sample.TotalParam[46][0] * sum(sample.TotalParam[32]) / len(sample.TotalParam[32]))
                    P = PQ / Q
                except:
                    print(traceback.format_exc())
                    P = 0
                figure.set3.info = [k, calc_age(f, sf, sample), [ar38ar36, ar40ar36, P]]
            except:
                figure.set3.info = [[0] * 12, [0] * 4, [0, 0, 0]]
            rightside_text = [
                f"z = {figure.set1.info[0][2]:.4f} x {'+' if figure.set1.info[0][4] > 0 else '-'} "
                f"{abs(figure.set1.info[0][4]):.4f} y {'+' if figure.set1.info[0][0] > 0 else '-'} "
                f"{abs(figure.set1.info[0][0]):.4f}",
                "t = {0:.2f} ± {1:.2f} | {2:.2f} | {3:.2f}".format(*list(figure.set1.info[1])),
                f"MSWD = {figure.set1.info[0][7]:.4f}, r2 = {figure.set1.info[0][8]:.4f}, Di = {figure.set1.info[0][10]}, "
                f"χ2 = {figure.set1.info[0][12]:.2f}, p = {figure.set1.info[0][13]:.2f}",
                f"<sup>40</sup>Ar/<sup>36</sup>Ar = {figure.set1.info[2][1]:.2f}",
                f"if <sup>38</sup>Ar/<sup>36</sup>Ar = {figure.set1.info[2][0]}",
                f"<sup>36</sup>Cl/<sup>38</sup>Cl productivity = {figure.set1.info[2][2]:.2f}", " ", " ",
                f"z = {figure.set2.info[0][2]:.4f} x {'+' if figure.set2.info[0][4] > 0 else '-'} "
                f"{abs(figure.set2.info[0][4]):.4f} y {'+' if figure.set2.info[0][0] > 0 else '-'} "
                f"{abs(figure.set2.info[0][0]):.4f}",
                "t = {0:.2f} ± {1:.2f} | {2:.2f} | {3:.2f}".format(*list(figure.set2.info[1])),
                f"MSWD = {figure.set2.info[0][7]:.4f}, r2 = {figure.set2.info[0][8]:.4f}, Di = {figure.set2.info[0][10]}, "
                f"χ2 = {figure.set2.info[0][12]:.2f}, p = {figure.set2.info[0][13]:.2f}",
                f"<sup>40</sup>Ar/<sup>36</sup>Ar = {figure.set2.info[2][1]:.2f}",
                f"if <sup>38</sup>Ar/<sup>36</sup>Ar = {figure.set2.info[2][0]}",
                f"<sup>36</sup>Cl/<sup>38</sup>Cl productivity = {figure.set2.info[2][2]:.2f}",
                f"Unselected", f"Age = {figure.set3.info[1][0]:.2f} ± {figure.set3.info[1][1]:.2f}",
                f"<sup>40</sup>Ar/<sup>36</sup>Ar = {figure.set3.info[2][1]:.2f}",
                f"if <sup>38</sup>Ar/<sup>36</sup>Ar = {figure.set3.info[2][0]}",
            ]
            setattr(figure, 'rightside_text', rightside_text)
        pass
    try:
        if not hasattr(sample, 'DegasPatternPlot'):
            setattr(sample, 'DegasPatternPlot', samples.Plot(id='figure_8', name='Degas Pattern Plot'))
        isotope_percentage = lambda l: [e / sum(l) * 100 if sum(l) != 0 else 0 for e in l]
        sample.DegasPatternPlot.data = [
            isotope_percentage(sample.DegasValues[0]),  # Ar36a
            isotope_percentage(sample.DegasValues[8]),  # Ar37Ca
            isotope_percentage(sample.DegasValues[10]),  # Ar38Cl
            isotope_percentage(sample.DegasValues[20]),  # Ar39K
            isotope_percentage(sample.DegasValues[24]),  # Ar40r
            isotope_percentage(sample.CorrectedValues[0]),  # Ar36
            isotope_percentage(sample.CorrectedValues[2]),  # Ar37
            isotope_percentage(sample.CorrectedValues[4]),  # Ar38
            isotope_percentage(sample.CorrectedValues[6]),  # Ar39
            isotope_percentage(sample.CorrectedValues[8]),  # Ar40
        ]
        sample.DegasPatternPlot.info = [True] * 10
    except Exception as e:
        print('Error in DegasPatternPlot: {}, lines: {}'.format(e, e.__traceback__.tb_lineno))
        raise ValueError('\nError in DegasPatternPlot: {}, lines: {}'.format(e, e.__traceback__.tb_lineno))


def recalc_agedistribution(sample: samples.Sample, **kwargs):
    for i in range(2):
        try:
            # Age bars
            sample.AgeDistributionPlot.set3.data = basic_funcs.removeNone(sample.ApparentAgeValues[2:4])
            # Set histogram data
            s = getattr(sample.AgeDistributionPlot.set1, 'bin_start', None)
            w = getattr(sample.AgeDistributionPlot.set1, 'bin_width', None)
            c = getattr(sample.AgeDistributionPlot.set1, 'bin_count', None)
            r = getattr(sample.AgeDistributionPlot.set1, 'bin_rule', None)
            # print(f's = {s}, r = {r}, w = {w}, c = {c}')
            histogram_data = calc_funcs.get_histogram_data(sample.ApparentAgeValues[2], s=s, r=r, w=w, c=c)
            sample.AgeDistributionPlot.set1.data = [histogram_data[1], histogram_data[0], histogram_data[2]]  # [half_bins, counts]
            setattr(sample.AgeDistributionPlot.set1, 'bin_start', histogram_data[3])
            setattr(sample.AgeDistributionPlot.set1, 'bin_rule', histogram_data[4])
            setattr(sample.AgeDistributionPlot.set1, 'bin_width', histogram_data[5])
            setattr(sample.AgeDistributionPlot.set1, 'bin_count', histogram_data[6])
            h = getattr(sample.AgeDistributionPlot.set2, 'band_width', None)
            k = getattr(sample.AgeDistributionPlot.set2, 'band_kernel', 'normal')
            t = getattr(sample.AgeDistributionPlot.set2, 'band_extend', False)
            a = getattr(sample.AgeDistributionPlot.set2, 'auto_width', 'Scott')
            n = getattr(sample.AgeDistributionPlot.set2, 'band_points', 1000)
            # print(f'h = {h}, k = {k}, a = {a}, n = {n}, extend = {t}')
            kda_data = calc_funcs.get_kde(
                sample.ApparentAgeValues[2], h=h, k=k, n=n, a=a,
                s=float(getattr(sample.AgeDistributionPlot.xaxis, 'min')) if t else histogram_data[3],
                e=float(getattr(sample.AgeDistributionPlot.xaxis, 'max')) if t else histogram_data[7],
            )
            sample.AgeDistributionPlot.set2.data = kda_data[0]  # [values, kda]
            setattr(sample.AgeDistributionPlot.set2, 'band_width', kda_data[1])
            setattr(sample.AgeDistributionPlot.set2, 'band_kernel', kda_data[2])
            setattr(sample.AgeDistributionPlot.set2, 'auto_width', kda_data[3])
            # sorted_data = [i[0] for i in sorted(zipped_data, key=lambda x: x[1])]
            text = f'n = {len(sample.ApparentAgeValues[2])}'
            peaks = find_peaks(kda_data[0][1])
            for index, peak in enumerate(peaks[0].tolist()):
                text = text + f'\nPeak {index}: {kda_data[0][0][peak]:.2f}'
            setattr(sample.AgeDistributionPlot.text1, 'text', text)
        except AttributeError:
            print(traceback.format_exc())
            re_set_smp(sample)
            continue
        except (Exception, BaseException):
            print(traceback.format_exc())
            sample.AgeDistributionPlot.data = [[], []]
            sample.AgeDistributionPlot.set1.data = [[], []]
            sample.AgeDistributionPlot.set2.data = [[], []]
        break


def set_plot_data(sample: samples.Sample, isInit: bool = True, isIsochron: bool = True,
                  isPlateau: bool = True, **kwargs):

    print(f"isInit: {isInit}, isIsochron: {isIsochron}, isPlateau: {isPlateau}")

    # Initialization, apply age spectra data and isochron plot data
    if isInit:
        # Set isochron points data
        isochron_dict = {
            'figure_2': {'data_index': [0, 5], 'name': 'Normal Isochron'},
            'figure_3': {'data_index': [6, 11], 'name': 'Inverse Isochron'},
            'figure_4': {'data_index': [12, 17], 'name': 'Cl Correlation 1'},
            'figure_5': {'data_index': [18, 23], 'name': 'Cl Correlation 2'},
            'figure_6': {'data_index': [24, 29], 'name': 'Cl Correlation 3'},
            'figure_7': {'data_index': [30, 39], 'name': 'Cl Correlation 3D'},
        }
        for key, val in isochron_dict.items():
            figure = get_component_byid(sample, key)
            try:
                # data = [x, sx, y, sy, (z, sz,) r1, (r2, r3,), index from 1]
                figure.data = sample.IsochronValues[val['data_index'][0]:val['data_index'][1]] + \
                              [[i + 1 for i in range(len(sample.SequenceName))]]
            except (Exception, BaseException):
                print(traceback.format_exc())
                figure.data = [[]] * (val['data_index'][1] - val['data_index'][0]) +\
                              [[i + 1 for i in range(len(sample.SequenceName))]]
            finally:
                # Ellipse
                if key != 'figure_7':
                    ellipse_data = []
                    for point in basic_funcs.getTransposed(figure.data[:5]):
                        if '' not in point and None not in point:
                            ellipse_data.append(calc_funcs.get_ellipse(*point))
                            getattr(figure, 'ellipse', samples.Plot.Set(id='ellipse')).data = ellipse_data

        # Set age spectra lines
        # Try to calculate total gas age
        try:
            a0, e0 = sum(sample.DegasValues[24]), pow(sum([i ** 2 for i in sample.DegasValues[25]]), 0.5)
            a1, e1 = sum(sample.DegasValues[20]), pow(sum([i ** 2 for i in sample.DegasValues[21]]), 0.5)
            total_f = [a0 / a1, calc_funcs.error_div((a0, e0), (a1, e1)), len(sample.DegasValues[24]), None]
            total_age = calc_age(*total_f[:2], sample)
        except (Exception, BaseException):
            sample.AgeSpectraPlot.info = [0, 0, 0, None, 0, 0, 0, 0]  # Info = f, sf, np, None, total age, s, s, s
        else:
            sample.AgeSpectraPlot.info = [*total_f, *total_age]  # Info = f, sf, np, None, total age, s, s, s
        try:
            sample.AgeSpectraPlot.data = list(
                calc_funcs.get_spectra(*sample.ApparentAgeValues[2:4], sample.ApparentAgeValues[7]))
            sample.AgeSpectraPlot.data = basic_funcs.getTransposed(sample.AgeSpectraPlot.data)
        except (Exception, BaseException):
            sample.AgeSpectraPlot.data = []

        # Set age distribution plot data
        recalc_agedistribution(sample)

    # Recalculate isochron lines
    if isIsochron:
        try:
            recalc_isochrons(sample)
        except (Exception, BaseException):
            print(traceback.format_exc())
            pass

    # Recalculate plateaus
    if isPlateau:
        try:
            recalc_plateaus(sample)
        except (Exception, BaseException):
            print(traceback.format_exc())
            pass

    # Obtain text content in right side of the page showing ages and fitting lines
    def get_age_str(info: list):
        if info is None:
            return '...'
        elif len(info) >= 3:
            return f"{info[0]:.2f} ± {info[2]:.2f}"
        elif len(info) >= 2:
            return f"{info[0]:.2f} ± {info[1]:.2f}"
        else:
            return '...'

    try:
        # Obtain text content in right side of the page showing ages and fitting lines
        set1_normal_age = sample.NorIsochronPlot.set1.info[3]
        set1_inverse_age = sample.InvIsochronPlot.set1.info[3]
        set1_weighted_age = sample.AgeSpectraPlot.set1.info[4:8]
        set2_normal_age = sample.NorIsochronPlot.set2.info[3]
        set2_inverse_age = sample.InvIsochronPlot.set2.info[3]
        set2_weighted_age = sample.AgeSpectraPlot.set2.info[4:8]
        total_age = sample.AgeSpectraPlot.info[4:8]
    except (Exception, BaseException):
        print(traceback.format_exc())
    else:
        for key, comp in get_components(sample).items():
            if isinstance(comp, samples.Plot) and key != 'figure_7':
                if comp.type == 'isochron' and key != 'figure_8':
                    line1_params = comp.set1.info[0]
                    line1_equation = f"y = {line1_params[0]:.4G} {'+' if line1_params[2] >= 0 else '-'} " \
                                     f"{abs(line1_params[2]):.4G}x"
                    line2_params = comp.set2.info[0]
                    line2_equation = f"y = {line2_params[0]:.4G} {'+' if line2_params[2] >= 0 else '-'} " \
                                     f"{abs(line2_params[2]):.4G}x"
                else:
                    line1_equation = line2_equation = '...'
                rightside_text = [
                    "Normal Isochron", f"{set1_normal_age[0]:.2f} ± {set1_normal_age[2]:.2f}",
                    "Inverse Isochron", f"{set1_inverse_age[0]:.2f} ± {set1_inverse_age[2]:.2f}",
                    "Weighted Plateau", f"{set1_weighted_age[0]:.2f} ± {set1_weighted_age[2]:.2f}",
                    "York Regress Line", line1_equation,
                    "Normal Isochron", f"{set2_normal_age[0]:.2f} ± {set2_normal_age[2]:.2f}",
                    "Inverse Isochron", f"{set2_inverse_age[0]:.2f} ± {set2_inverse_age[2]:.2f}",
                    "Weighted Plateau", f"{set2_weighted_age[0]:.2f} ± {set2_weighted_age[2]:.2f}",
                    "York Regress Line", line2_equation,
                    "Total Age", f"{total_age[0]:.2f} ± {total_age[2]:.2f}",
                ]
                setattr(comp, 'rightside_text', rightside_text)
            else:
                continue
        pass


def reset_plot_scale(sample: samples.Sample, only_figure: str = None):
    for k, v in get_components(sample).items():
        if isinstance(v, samples.Plot):
            if only_figure is not None and k != only_figure:
                continue
            if k == 'figure_1':
                try:
                    data = basic_funcs.getTransposed(
                        v.data + v.data + v.set1.data + v.set1.data + v.set2.data + v.set2.data)
                    ylist = data[1] + data[2]
                    yscale = calc_funcs.get_axis_scale(ylist, min_interval=5, extra_count=1)
                    xscale = [0, 100, 20]
                except (Exception, BaseException):
                    print(traceback.format_exc())
                    continue
            elif k == 'figure_3':
                try:
                    xlist = v.data[0]
                    xscale = calc_funcs.get_axis_scale(xlist)
                    yscale = [0, 0.004, 4, 0.001]
                except (Exception, BaseException):
                    print(traceback.format_exc())
                    continue
            elif k == 'figure_7':
                try:
                    xlist, ylist, zlist = v.data[0], v.data[2], v.data[4]
                    xscale = calc_funcs.get_axis_scale(xlist)
                    yscale = calc_funcs.get_axis_scale(ylist)
                    zscale = calc_funcs.get_axis_scale(zlist)
                    setattr(getattr(v, 'zaxis'), 'min', zscale[0])
                    setattr(getattr(v, 'zaxis'), 'max', zscale[1])
                    setattr(getattr(v, 'zaxis'), 'split_number', zscale[2])
                except (Exception, BaseException):
                    print(traceback.format_exc())
                    continue
            elif k == 'figure_9':
                try:
                    xlist = v.set3.data[0] + [v.set3.data[0][i] - v.set3.data[1][i] for i in range(len(v.set3.data[0]))] + [
                        v.set3.data[0][i] + v.set3.data[1][i] for i in range(len(v.set3.data[0]))]
                    ylist = v.set1.data[1]
                    xscale = calc_funcs.get_axis_scale(xlist)
                    yscale = calc_funcs.get_axis_scale(ylist)
                except (Exception, BaseException):
                    continue
            else:
                try:
                    xlist = v.data[0]
                    ylist = v.data[2]
                    xscale = calc_funcs.get_axis_scale(xlist)
                    yscale = calc_funcs.get_axis_scale(ylist)
                except (Exception, BaseException):
                    print(traceback.format_exc())
                    continue
            setattr(getattr(v, 'xaxis', samples.Plot.Axis()), 'min', xscale[0])
            setattr(getattr(v, 'xaxis', samples.Plot.Axis()), 'max', xscale[1])
            setattr(getattr(v, 'xaxis', samples.Plot.Axis()), 'split_number', xscale[2])
            setattr(getattr(v, 'yaxis', samples.Plot.Axis()), 'min', yscale[0])
            setattr(getattr(v, 'yaxis', samples.Plot.Axis()), 'max', yscale[1])
            setattr(getattr(v, 'yaxis', samples.Plot.Axis()), 'split_number', yscale[2])
            if only_figure is not None and k == only_figure:
                return xscale, yscale


def reset_text_position(sample: samples.Sample, only_figure: str = None):
    """
    Reset text position to default, if only figure is defined, only this figure will be reset.
    """
    for figure_id in list(samples.DEFAULT_PLOT_STYLES.keys()):
        if only_figure is not None and figure_id != only_figure:
            continue
        figure = get_component_byid(sample, figure_id)
        text_1 = get_plot_set(figure, 'Text for Set 1')
        if text_1 is not None:
            setattr(text_1, 'pos', [20, 30])
        text_2 = get_plot_set(figure, 'Text for Set 2')
        if text_2 is not None:
            setattr(text_2, 'pos', [70, 60])


def set_plot_style(sample: samples.Sample):

    # Reset styles
    initial_plot_styles(sample, except_attrs=['rightside_text', 'data'])

    # Auto scale
    reset_plot_scale(sample)

    # Auto position of text
    reset_text_position(sample)

    # Set title et al., which are deleted in initialzing
    # suffix = f"{sample.Info['sample']['name']} {sample.Info['sample']['material']}"
    suffix = f"{sample.Info.sample.name} {sample.Info.sample.material}"
    for figure_id, figure in get_components(sample).items():
        if isinstance(figure, samples.Plot):
            if not hasattr(figure, 'title'):
                setattr(figure, 'title', samples.Plot.Text())
            setattr(getattr(figure, 'title'), 'text', f"{suffix} {getattr(figure, 'name', '')}")


def set_table_style(sample: samples.Sample):
    header = lambda index: [
        '',
        samples.SAMPLE_INTERCEPT_HEADERS, samples.BLANK_INTERCEPT_HEADERS, samples.CORRECTED_HEADERS,
        samples.DEGAS_HEADERS, samples.PUBLISH_TABLE_HEADERS, samples.SPECTRUM_TABLE_HEADERS,
        samples.ISOCHRON_TABLE_HEADERS, samples.TOTAL_PARAMS_HEADERS
    ][index]
    for key, component in get_components(sample).items():
        if isinstance(component, samples.Table):
            component.header = header(index=int(component.id))
            component.colcount = len(component.header)
            component.coltypes = [{'type': 'numeric'}] * (component.colcount)
            textindexs = getattr(component, 'textindexs', [0]) if hasattr(component, 'textindexs') else [0]
            for i in textindexs:
                component.coltypes[i] = {'type': 'text'}


def calc_apparent_ages(sample: samples.Sample):
    ar40rar39k = sample.ApparentAgeValues[0:2]
    age = [calc_age(item, ar40rar39k[1][i], sample, index=i) for i, item in enumerate(ar40rar39k[0])]
    sample.ApparentAgeValues[2:6] = basic_funcs.getTransposed(age)
    sample.PublishValues[5:7] = copy.deepcopy(sample.ApparentAgeValues[2:4])


def calc_age(ar40ar39, sar40ar39, sample: samples.Sample, index: int = 0):
    params = sample.TotalParam
    calcParams = {}
    useMinEquation = sample.TotalParam[110][index]
    J = sample.TotalParam[67][index]
    sJ = sample.TotalParam[68][index] / 100 * J
    try:
        if useMinEquation:
            calcParams = {
                'L': params[34][index], 'sL': params[35][index] / 100 * params[34][index],
                'Le': params[36][index], 'sLe': params[37][index] / 100 * params[36][index],
                'Lb': params[38][index], 'sLb': params[39][index] / 100 * params[38][index],
                'A': params[48][index], 'sA': params[49][index] / 100 * params[48][index],
                'Ae': params[50][index], 'sAe': params[51][index] / 100 * params[50][index],
                'Ab': params[52][index], 'sAb': params[53][index] / 100 * params[52][index],
                't': params[59][index], 'st': params[60][index] / 100 * params[59][index],
                'W': params[81][index], 'sW': params[82][index] / 100 * params[81][index],
                'No': params[83][index], 'sNo': params[84][index] / 100 * params[83][index],
                'Y': params[85][index], 'sY': params[86][index] / 100 * params[85][index],
                'f': params[87][index], 'sf': params[88][index] / 100 * params[87][index],
            }
        else:
            raise TypeError
    except (TypeError, KeyError, IndexError, ZeroDivisionError):
        calcParams = {
            'L': params[34][index], 'sL': params[35][index] / 100 * params[34][index],
        }
        useMinEquation = False
    finally:
        return calc_funcs.calc_age(ar40ar39, sar40ar39, J, sJ, useMinEquation=useMinEquation, **calcParams)


def recalculate(
        sample: samples.Sample, re_initial: bool = False,
        re_corr_blank: bool = False, re_corr_massdiscr: bool = False,
        re_corr_decay: bool = False, re_degas_ca: bool = False, re_degas_k: bool = False,
        re_degas_cl: bool = False, re_degas_atm: bool = False, re_degas_r: bool = False,
        re_calc_ratio: bool = False, re_calc_apparent_age: bool = False,
        re_plot: bool = False, re_plot_style: bool = False, re_set_table: bool = False,
        re_table_style: bool = False, **kwargs
):
    if sample.UnselectedSequence == sample.SelectedSequence1 == sample.SelectedSequence2 == []:
        sample.UnselectedSequence = list(range(len(sample.SequenceName)))
    # --- initializing ---
    if re_initial:  # 1
        re_set_smp(sample)
    # --- calculating ---
    if re_corr_blank:  # 2
        corr_blank(sample)
    if re_corr_massdiscr:  # 3
        corr_massdiscr(sample)
    if re_corr_decay:  # 4
        corr_decay(sample)
    if re_degas_ca:  # 5
        calc_degas_ca(sample)
    if re_degas_k:  # 6
        calc_degas_k(sample)
    if re_degas_cl:  # 7
        calc_degas_cl(sample)
    if re_degas_atm:  # 8
        calc_degas_atm(sample)
    if re_degas_r:  # 9
        calc_degas_r(sample)
    if re_calc_ratio:  # 10
        calc_ratio(sample)
    if re_calc_apparent_age:  # 11
        calc_apparent_ages(sample)
    # --- plot and table ---
    if re_plot:  # 12
        set_plot_data(sample, **kwargs)
    if re_plot_style:  # 13
        set_plot_style(sample)
    if re_set_table:  # 14
        update_table_data(sample)
    if re_table_style:  # 15
        set_table_style(sample)
    return sample

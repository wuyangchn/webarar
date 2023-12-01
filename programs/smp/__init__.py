# from . import sample, smp_funcs
import traceback
import programs as arpy
import pandas as pd
import numpy as np


def create_sample_from_df(content: pd.DataFrame, smp_info: dict):
    """
    content:
        [
            sample_values, blank_values, corrected_values, degas_values, publish_values,
            apparent_age_values, isochron_values, total_param, sample_info, isochron_mark,
            sequence_name, sequence_value
        ]
    return sample instance
    """
    # # Create sample file
    # smp = samples.Sample()
    # # Initializing
    # smp_funcs.initial(smp)
    #
    # smp.SampleIntercept = content['smp'].transpose().values.tolist()
    # smp.BlankIntercept = content['blk'].transpose().values.tolist()
    # smp.CorrectedValues = content['cor'].transpose().values.tolist()
    # smp.DegasValues = content['deg'].transpose().values.tolist()
    # smp.PublishValues = content['pub'].transpose().values.tolist()
    # smp.ApparentAgeValues = content['age'].transpose().values.tolist()
    # smp.IsochronValues = content['iso'].transpose().values.tolist()
    # smp.TotalParam = content['pam'].transpose().values.tolist()
    # smp.IsochronMark = content['mak'].transpose().values.tolist()
    # smp.SequenceName = content['seq'][0].transpose().values.tolist()
    # smp.SequenceValue = content['seq'][1].transpose().values.tolist()
    #
    # smp_funcs.update_plot_from_dict(smp.Info, smp_info)
    #
    # smp.SelectedSequence1 = np.flatnonzero(content['mak'] == 1).tolist()
    # smp.SelectedSequence2 = np.flatnonzero(content['mak'] == 2).tolist()
    # smp.UnselectedSequence = np.flatnonzero(pd.isna(content['mak'])).tolist()
    #
    # try:
    #     # Re-calculating ratio and plot after reading age or full files
    #     smp_funcs.recalculate(smp, re_calc_ratio=True, re_plot=True, re_plot_style=True)
    # except Exception as e:
    #     print(f'Error in setting plot: {traceback.format_exc()}')
    # # Write tables after reading data from a full or age file
    # smp_funcs.update_table_data(smp)
    # return smp

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
    smp = arpy.Sample()
    # Initializing
    arpy.smp_funcs.initial(smp)

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

    arpy.smp_funcs.update_plot_from_dict(smp.Info, smp_info)

    smp.SelectedSequence1 = [index for index, item in enumerate(smp.IsochronMark) if item == 1]
    smp.SelectedSequence2 = [index for index, item in enumerate(smp.IsochronMark) if item == 2]
    smp.UnselectedSequence = [index for index, item in enumerate(smp.IsochronMark) if item not in [1, 2]]

    try:
        # Re-calculating ratio and plot after reading age or full files
        arpy.smp_funcs.recalculate(smp, re_calc_ratio=True, re_plot=True, re_plot_style=True)
    except Exception as e:
        print(f'Error in setting plot: {traceback.format_exc()}')
    # Write tables after reading data from a full or age file
    arpy.smp_funcs.update_table_data(smp)
    return smp

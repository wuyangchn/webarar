#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - files - arr_file
# ==========================================
#
#
#
"""
# === External imports ===
import os
import pickle

from .. import smp

SAMPLE_MODULE = smp.Sample().__module__


def to_sample(file_path, sample_name: str = ""):
    """
    file_path: full path of input file
    name： samplename
    return sample instance
    """
    try:
        with open(file_path, 'rb') as f:
            sample = renamed_load(f)
    except (Exception, BaseException):
        raise ValueError(f"Fail to open arr file: {file_path}")
    # Check arr version
    # recalculation will not be applied automatically
    sample = check_version(sample)
    return sample


def save(file_path, sample: smp.Sample):
    """ Save arr project as arr files

    Parameters
    ----------
    file_path : str, filepath
    sample : Sample instance

    Returns
    -------
    str, file name
    """
    file_path = os.path.join(file_path, f"{sample.Info.sample.name}.arr")
    with open(file_path, 'wb') as f:
        f.write(pickle.dumps(sample))
    # with open(file_path, 'w') as f:
    # # save serialized json data to a readable text
    #     f.write(basic_funcs.getJsonDumps(sample))
    return f"{sample.Info.sample.name}.arr"


def check_version(sample: smp.Sample):
    """

    Parameters
    ----------
    sample

    Returns
    -------

    """
    if sample.ArrVersion != smp.VERSION:
        smp.initial.re_set_smp(sample)
    return sample


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        renamed_module = module
        if '.sample' in module and module != SAMPLE_MODULE:
            renamed_module = SAMPLE_MODULE

        return super(RenameUnpickler, self).find_class(renamed_module, name)


def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()


#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang 
# webarar - new_file
# ==========================================
#
#
# 
"""
from .. import smp


def to_sample(file_path: str = '', sample_name: str = None):
    """
    Parameters
    ----------
    file_path
    sample_name

    Returns
    -------

    """
    sample = smp.Sample()
    # initial settings
    smp.initial.initial(sample)
    if sample_name is not None:
        sample.Info.sample.name = sample_name
    return sample

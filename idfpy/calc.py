#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import numpy as np


def merge(m1, m2):
    '''merge two masked arrays, the first taking precedence over the second'''
    assert m1.shape == m2.shape, 'input arrays unequal shape'
    merged = m1.copy()
    complement = m1.mask & ~m2.mask
    merged[complement] = m2[complement]
    return merged


def agg(*ms, method='sum', axis=-1):
    func = {
        'min': np.ma.min,
        'max': np.ma.max,
        'sum': np.ma.sum,
        'mean': np.ma.mean,
        }.get(method)
    result = func(np.stack(ms, axis=axis), axis=axis)
    return np.ma.masked_invalid(result)
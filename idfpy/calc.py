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


def nanmin(*ms, axis=-1):
    '''take the average over a sequence of arrays'''
    return np.nanmin(np.stack(ms, axis=axis), axis=axis)


def nanmax(*ms, axis=-1):
    '''take the average over a sequence of arrays'''
    return np.nanmax(np.stack(ms, axis=axis), axis=axis)


def nansum(*ms, axis=-1):
    '''take the average over a sequence of arrays'''
    return np.nansum(np.stack(ms, axis=axis), axis=axis)


def nanmean(*ms, axis=-1):
    '''take the average over a sequence of arrays'''
    return np.nanmean(np.stack(ms, axis=axis), axis=axis)
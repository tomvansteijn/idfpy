# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from .idf import IdfFile


def open(idfile, mode='rb', header=None):
    '''IdfFile instance from file'''
    return IdfFile(idfile, mode=mode, header=header)


def read(idffile, masked=False):
    '''read IDF file and return data array'''
    with open(idfile) as src:
        return src.read(masked=masked)

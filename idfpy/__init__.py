# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from .idf import IdfFile


def open(idfile, mode='rb', header=None):
    return IdfFile(idfile, mode=mode, header=header)

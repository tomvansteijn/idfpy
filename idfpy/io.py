#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from idfpy import idf


def read_array(idffile):
    with idf.IdfFile(idffile) as src:
        return src.read(masked=True)


def read_header(idffile):
    with idf.IdfFile(idffile) as src:
        return src.header


def write_array(idffile, array, header):
    with idf.IdfFile(idffile, 'wb', header) as dst: 
        dst.write(array)
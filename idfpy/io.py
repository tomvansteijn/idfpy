#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from idfpy import idf


def read_array(idffile, masked=True):
    with idf.IdfFile(idffile) as src:
        return src.read(masked=masked)


def read_header(idffile):
    with idf.IdfFile(idffile) as src:
        return src.header


def get_transform(idffile):
    with idf.IdfFile(idffile) as src:
        return src.geotransform


def write_array(idffile, array, header):
    with idf.IdfFile(idffile, 'wb', header) as dst: 
        dst.write(array)
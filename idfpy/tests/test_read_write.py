#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import numpy as np
import idfpy


def test_read_write_equal_header():
    # read original
    sourcefile = r'bxk1-d-ck.idf'
    with idfpy.open(sourcefile) as src:
        source = src.read(masked=True)
        header = src.header.copy()

    # write copy
    destfile = r'bxk1-d-ck_copy.idf'
    with idfpy.open(destfile, 'wb', header=header) as dst:
        dst.write(source)

    # read copy and compare
    with idfpy.open(destfile, 'rb') as cpy:
        copy = cpy.read(masked=True)
        copy_header = cpy.header

    assert header == copy_header


def test_read_write_equal_values():
    # read original
    sourcefile = r'bxk1-d-ck.idf'
    with idfpy.open(sourcefile) as src:
        source = src.read(masked=True)
        header = src.header.copy()

    # write copy
    destfile = r'bxk1-d-ck_copy.idf'
    with idfpy.open(destfile, 'wb', header=header) as dst:
        dst.write(source)

    # read copy and compare
    with idfpy.open(destfile, 'rb') as dst:
        copy = dst.read(masked=True)

    np.testing.assert_array_equal(source, copy)

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import idfpy

import numpy as np
import pytest

import shutil
import os


@pytest.fixture
def sourcefile(tmpdir):
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    sourcefilename = r'bxk1-d-ck.idf'
    sourcefile = os.path.join(datadir, sourcefilename)
    testfile = tmpdir.join(sourcefilename)
    shutil.copyfile(sourcefile, testfile)
    return testfile


@pytest.fixture
def destfile(tmpdir):
    copyfilename = r'bxk1-d-ck_copy.idf'
    testfile = tmpdir.join(copyfilename)
    return testfile


def test_read_twice(sourcefile):
    # read
    with idfpy.open(sourcefile) as src:
        source = src.read(masked=True)
        header = src.header.copy()

    # read again
    with idfpy.open(sourcefile) as src:
        source_again = src.read(masked=True)
        header_again = src.header.copy()

    np.testing.assert_array_equal(source, source_again)


def test_write_equal_header(sourcefile, destfile):
    # read original
    with idfpy.open(sourcefile) as src:
        source = src.read(masked=True)
        header = src.header.copy()

    # write copy
    with idfpy.open(destfile, 'wb', header=header) as dst:
        dst.write(source)

    # read copy and compare
    with idfpy.open(destfile, 'rb') as cpy:
        copy = cpy.read(masked=True)
        copy_header = cpy.header

    assert header == copy_header


def test_write_equal_values(sourcefile, destfile):
    # read original
    with idfpy.open(sourcefile) as src:
        source = src.read(masked=True)
        header = src.header.copy()

    # write copy
    with idfpy.open(destfile, 'wb', header=header) as dst:
        dst.write(source)

    # read copy and compare
    with idfpy.open(destfile, 'rb') as cpy:
        copy = cpy.read(masked=True)

    np.testing.assert_array_equal(source, copy)


def test_write_twice(sourcefile, destfile):
    # read original
    with idfpy.open(sourcefile) as src:
        source = src.read(masked=True)
        header = src.header.copy()

    # write copy
    with idfpy.open(destfile, 'wb', header=header) as dst:
        dst.write_header()
        dst.write(source)
        dst.write(source)

    # read copy and compare
    with idfpy.open(destfile, 'rb') as cpy:
        copy = cpy.read(masked=True)
        copy_header = cpy.header

    assert header == copy_header
    np.testing.assert_array_equal(source, copy)


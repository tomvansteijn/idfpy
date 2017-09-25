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


def test_sample(sourcefile):
    coords = [(256060., 483140.), ]
    # sample
    with idfpy.open(sourcefile) as src:
        value, = next(src.sample(coords))
    assert np.isclose(value, 3.6234)


def test_sample_nodata(sourcefile):
    coords = [(252550., 486450.), ]
    # sample
    with idfpy.open(sourcefile) as src:
        value, = next(src.sample(coords))
    assert np.isnan(value)


def test_sample_outside(sourcefile):
    coords = [(260310., 486450.), ]
    # sample
    with idfpy.open(sourcefile) as src:
        value, = next(src.sample(coords))
    assert np.isnan(value)

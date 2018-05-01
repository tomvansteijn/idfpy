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


class TestIdfFile(object):
    def test_open(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            assert not src.closed

    def test_is_closed(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            pass
        assert src.closed

    def test_len(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            assert len(src) == 5808

    def test_irec(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            src.irec == 52

    def test_geotransform(self, sourcefile):
        expected_geotransform = (
            251500.,
            100.,
            0.,
            489200.,
            0.,
            -100.,
            )

        with idfpy.open(sourcefile) as src:
            for value, expected_value in \
            zip(src.geotransform, expected_geotransform):
                if isinstance(value, float):
                    assert np.isclose(value, expected_value)
                else:
                    assert value == expected_value

    def test_copy(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            cpy = src.copy()
            assert cpy is not src
            assert cpy.filepath == src.filepath
            assert cpy.mode == src.mode
            assert cpy.closed == src.closed
            assert cpy.header is not src.header
            assert cpy.header == src.header

    def test_check_read(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            pass
        with pytest.raises(IOError):
            src.read()

        src.open(mode='wb')
        with pytest.raises(ValueError):
            src.read()

    def test_read_header(self, sourcefile):
        expected_header = {
            'dmax': 9.759389877319336,
            'dmin': 0.041515398770570755,
            'dx': 100.,
            'dy': 100.,
            'ieq': False,
            'itb': False,
            'ivf': False,
            'lahey': 1271,
            'ncol': 88,
            'nodata': -9999.,
            'nrow': 66,
            'xmax': 260300.,
            'xmin': 251500.,
            'ymax': 489200.,
            'ymin': 482600.,
            }
        with idfpy.open(sourcefile) as src:
            header = src.header

        for key, value in header.items():
            assert key in expected_header
            expected_value = expected_header[key]
            if isinstance(value, float):
                assert np.isclose(value, expected_value)
            else:
                assert value == expected_value

    def test_read(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            data = src.read(masked=False)
        assert np.isclose(data.mean(), -1512.6943)

    def test_read_masked(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            data = src.read(masked=True)
        assert np.isclose(data.mean(), 2.71736125)

    def test_check_write(self, destfile):
        with idfpy.open(destfile, 'wb') as dst:
            z = np.zeros((66, 88))
        with pytest.raises(IOError):
            dst.write(z)

        dst.open(mode='rb')
        with pytest.raises(ValueError):
            dst.write(z)

    def test_out_of_bounds(self, sourcefile):
        with idfpy.open(sourcefile) as src:
            assert not src.is_out_of_bounds(0, 0)
            assert not src.is_out_of_bounds(65, 0)
            assert not src.is_out_of_bounds(0, 87)
            assert not src.is_out_of_bounds(65, 87)

            assert src.is_out_of_bounds(-1, 0)
            assert src.is_out_of_bounds(0, -1)
            assert src.is_out_of_bounds(66, 0)
            assert src.is_out_of_bounds(0, 88)
            assert src.is_out_of_bounds(66, 88)



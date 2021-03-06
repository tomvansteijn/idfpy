#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from idfpy import calc
from idfpy import io

from pathlib import Path
import click


def match_shape(idffile, desired_shape):
    '''check if the shape of idffile with is equal to desired shape'''
    desired_nrow, desired_ncol = desired_shape
    header = io.read_header(idffile)
    return (
        header['nrow'] == desired_nrow and
        header['ncol'] == desired_ncol
        )


@click.command()
@click.argument('pattern', type=str)
@click.argument('method', type=click.Choice(['min', 'max', 'sum', 'mean']))
@click.argument('outfile', type=str)
def stack(pattern, method, outfile, path='.'):
    '''stack and aggregate idf's using min, max or mean'''
    p = Path(path)
    idffiles = [f for f in p.glob(pattern) if not f == outfile]
    if not len(idffiles):
        raise ValueError('no match for \'{p:}\''.format(p=pattern))
    header = io.read_header(idffiles[0])
    shape = header['nrow'], header['ncol']
    arrays = (io.read_array(f) for f in idffiles if match_shape(f, shape))
    io.write_array(outfile, calc.agg(*arrays, method=method), header)


@click.command()
@click.argument('pattern', type=str)
@click.option('--epsg', type=int, default=28992, help='The coordinate reference system')
def idf2tif(pattern, epsg, path='.'):
    '''stack and aggregate idf's using min, max or mean'''
    from idfpy import idfraster

    p = Path(path)    
    for idffile in p.glob(pattern):
        with idfraster.IdfRaster(str(idffile)) as src:
            src.to_raster(str(idffile.with_suffix('.tif')), epsg=epsg, driver='GTiff')


@click.command()
@click.argument('pattern', type=str)
@click.option('--epsg', type=int, default=28992, help='The coordinate reference system')
def idf2asc(pattern, epsg, path='.'):
    '''stack and aggregate idf's using min, max or mean'''
    from idfpy import idfraster

    p = Path(path)    
    for idffile in p.glob(pattern):
        with idfraster.IdfRaster(str(idffile)) as src:
            src.to_raster(str(idffile.with_suffix('.asc')), epsg=epsg, driver='AAIGrid')
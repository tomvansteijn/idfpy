#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from idfpy import calc
from idfpy import io

from pathlib import Path
import click

@click.command()
@click.argument('pattern', type=str)
@click.argument('method', type=click.Choice(['min', 'max', 'sum', 'mean']))
@click.argument('outfile', type=str)
@click.argument('path', type=str, default='.')
def stack(pattern, method, outfile, path):
    '''stack and aggregate idf's using min, max or mean'''
    p = Path(path)
    files = [f for f in p.glob(pattern) if not f == outfile]
    if not len(files):
        raise ValueError('no match for \'{p:}\''.format(p=pattern))
    header = io.read_header(files[0])
    arrays = (io.read_array(f) for f in files)
    agg = {
        'min': calc.nanmin,
        'max': calc.nanmax,
        'sum': calc.nansum,
        'mean': calc.nanmean,
        }.get(method)
    io.write_array(outfile, agg(*arrays), header)




Idfpy
=====
A simple module for reading and writing iMOD IDF files. IDF is a simple binary format used by the iMOD_https://www.deltares.nl/nl/software/imod-2 groundwater modelling software.

The format contains:
1. A header with grid and spatial extent information
2. An array of floats

The array of floats is translated to a rectangular grid using the ``ncol`` and ``nrow`` fields of the header. The IDF format contains no spatial reference.

Installation
------------
This package is not yet published. In the meanwhile, use pip:

    pip install git+https://github.com/tomvansteijn/idfpy.git

Usage
-----

Example:
    import idfpy
    with idfpy.open('kh.idf') as src:
        kh = src.read(masked=True)

    print('kh mean: {:.1f}'.format(kh.mean()))
    print('kh coverage: {:.1f}%'.format(
        kh.mask.sum() / kh.mask.count * 1e2
        ))

Files can also be sampled using a sequence of X, Y coordinates:

    import idfpy
    coords = [(250_000., 400_000.), ]
    with idfpy.open('kh.idf') as src:
        values = [v[0] for v in src.sample(coords)]

    print(values)

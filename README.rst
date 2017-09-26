Idfpy
=====
A simple module for reading and writing iMOD IDF files. IDF is a simple binary format used by the `iMOD <https://www.deltares.nl/nl/software/imod-2>`_ groundwater modelling software.

The format contains:
    1. A header with grid and spatial extent information
    2. An array of floats

The array of floats is translated to a rectangular grid using the ``ncol`` and ``nrow`` fields of the header. The IDF format contains no spatial reference, it is projection unaware.

Installation
------------
This package is not yet published. In the meanwhile, use pip:
::
    pip install git+https://github.com/tomvansteijn/idfpy.git
    python setup.py install
::
Installation requires Python 3+ and Numpy.

Usage
-----

Example:
::
    import idfpy
    with idfpy.open('bxk1-d-ck.idf') as src:
        bxk1d = src.read(masked=True)

    print('bxk1d mean: {:.1f}'.format(bxk1d.mean()))
    print('bxk1d coverage: {:.1f}%'.format(
        (1 - bxk1d.mask.sum() / bxk1d.mask.size) * 1e2
        ))
::

Files can also be sampled using a sequence of X, Y coordinates:
::
    import idfpy
    coords = [(255_872., 485_430.), ]
    with idfpy.open('bxk1-d-ck.idf') as src:
        values = [v[0] for v in src.sample(coords)]

    print(values)
::

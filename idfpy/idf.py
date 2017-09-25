#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import numpy as np

from enum import Enum
import logging
import struct


class IdfFileHeaderFormat(object):
    '''Static class containing Idf file header definition'''
    fields = [
    ('lahey', 'i'),
    ('ncol', 'i'),
    ('nrow', 'i'),
    ('xmin', 'f'),
    ('xmax', 'f'),
    ('ymin', 'f'),
    ('ymax', 'f'),
    ('dmin', 'f'),
    ('dmax', 'f'),
    ('nodata', 'f'),
    ('ieq', '?'),
    ('itb', '?'),
    ('ivf', '?'),
    ]

    pad_bytes = 1
    # See: iMOD user manual 4.0

    names = [n for n, f in fields]
    byteformat = ''.join(f for n, f in fields) + pad_bytes*'x'
    length = struct.calcsize(byteformat)


class IdfFileMode(Enum):
    '''Idf file binary read or write mode'''
    rb = 0
    wb = 1


class IdfFile(object):
    '''iMOD Idf file read and write object'''
    def __init__(self, filepath, mode='rb', header=None):
        # set filepath as property
        self.filepath = filepath

        # set other default properties
        self.closed = True
        self.nodatavals = []

        # get mode enum and set as property
        try:
            self.mode = IdfFileMode[mode]
        except KeyError:
            raise ValueError(
                "mode string must be one of 'rb' or 'wb', not {}".format(mode))

        # open filehandle
        self.open()

        # set header or read from file
        if header is not None:
            self.header = header
        elif self.mode == IdfFileMode.rb:
            self.header = self.read_header()
        else:
            self.header = {}  # no header, empty dict

    def __repr__(self):
        return (
            '{s.__class__.__name__:}(filepath={s.filepath:}, '
            'mode={s.mode.name:}, closed={s.closed:})').format(
            s=self,
            )

    def __len__(self):
        if self.header is not None:
            return self.header['ncol'] * self.header['nrow']

    def __enter__(self):
        '''enter with statement block'''
        return self

    def __exit__(self, *args):
        '''exit with statement block'''
        self.close()

    def open(self):
        '''open file handle'''
        self.f = open(self.filepath, self.mode.name)
        self.closed = False

    def close(self):
        '''close file handle'''
        self.f.close()
        self.closed = True

    def copy(self):
        '''return new instance with copy of header'''
        return self.__class__(
            filepath=self.filepath,
            mode=self.mode.name,
            header=self.header.copy(),
            )

    def check_read(self):
        '''check if reading from file is ok'''
        if self.mode != IdfFileMode.rb:
            raise ValueError("cannot read in '{}' mode".format(self.mode.name))
        if self.closed:
            raise IOError('cannot read closed Idf file')
        return True

    def read_header(self, is_checked=False):
        '''read header from Idf file'''
        if not is_checked:
            self.check_read()

        # set file back to first byte
        self.f.seek(0)

        # read values according to headerformat and save in dict
        header_values = struct.unpack(
            IdfFileHeaderFormat.byteformat,
            self.f.read(IdfFileHeaderFormat.length),
            )
        header = {n: v
            for n, v in zip(IdfFileHeaderFormat.names, header_values)
            }

        # read conditional values from header
        if not header['ieq']:
            header['dx'], header['dy'] = struct.unpack('2f',
                self.f.read(4*2))
        if header['itb']:
            header['top'], header['bot'] = struct.unpack('2f',
                self.f.read(4*2))
        if header['ieq']:
            header['dx(col)'] = struct.unpack('f'*header['ncol'],
                self.f.read(4*header['ncol']))
            header['dy(row)'] = struct.unpack('f'*header['nrow'],
                self.f.read(4*header['nrow']))

        # set nodata value
        self.nodatavals = [header['nodata'], ]

        return header

    @property
    def irec(self):
        return (10 + (not self.header['ieq']) * 2 + self.header['ieq'] * 2
            + self.header['itb'] * 2 + 1) * 4

    def read(self, masked=False):
        '''read values from Idf file and return data as (masked) array'''
        is_checked = self.check_read()
        if not self.header:
            self.header = self.read_header(is_checked=is_checked)

        # set file to start of data
        self.f.seek(self.irec)

        # read values
        values = np.fromfile(self.f, np.float32,
            self.header['nrow']*self.header['ncol'])

        # reshape values to array shape(nrow, ncol)
        values = values.reshape(self.header['nrow'], self.header['ncol'])

        if masked:
            return np.ma.masked_values(values, self.nodatavals[0])
        else:
            return values

    def check_write(self):
        '''check if write to file is ok'''
        if self.mode != IdfFileMode.wb:
            raise ValueError("cannot write in '{}' mode".format(self.mode.name))
        if self.closed:
            raise IOError('cannot write to closed Idf file')
        if not self.header:
            raise ValueError('cannot write when header is empty')
        return True

    def update_header(self, array):
        '''update header based on Idf data'''

        # update shape
        nrow, ncol = array.shape
        self.header['nrow'] = nrow
        self.header['ncol'] = ncol
        self.header['xmax'] = self.header['xmin'] + self.header['dx'] * ncol
        self.header['ymax'] = self.header['ymin'] + self.header['dy'] * nrow

        # update nodata value
        if isinstance(array, np.ma.MaskedArray):
            self.header['nodata'] = array.fill_value

        # update value range
        self.header['dmin'] = array.min()
        self.header['dmax'] = array.max()


    def write_header(self, is_checked=False):
        '''write header to file'''
        if not is_checked:
            self.check_write()

        # set file back to first byte
        self.f.seek(0)

        # write values according to headerformat
        header_values = [self.header[k] for k in IdfFileHeaderFormat.names]
        self.f.write(struct.pack(IdfFileHeaderFormat.byteformat,
            *header_values,
            ))

        # write conditional values
        if not self.header['ieq']:
            self.f.write(struct.pack('f', self.header['dx']))
            self.f.write(struct.pack('f', self.header['dy']))
        if self.header['itb']:
            self.f.write(struct.pack('f', self.header['top']))
            self.f.write(struct.pack('f', self.header['bot']))
        if self.header['ieq']:
            self.f.write(struct.pack(len(self.header['dx(col)'])*'f',
                self.header['dx(col)']))
            self.f.write(struct.pack(len(self.header['dy(row)'])*'f',
                self.header['dy(row)']))
        if self.header['ivf']:
            raise NotImplementedError('write method ivf=true not implemented')

    def write(self, array):
        '''write to header and values to file'''
        is_checked = self.check_write()

        # update header
        self.update_header(array)

        # write header
        self.write_header(is_checked=is_checked)

        # set file to start of data
        self.f.seek(self.irec)

        # unmask
        if isinstance(array, np.ma.MaskedArray):
            array = array.filled()

        # write values
        flattened = array.flatten()
        self.f.write(struct.pack('f'*len(flattened), *flattened))

    def is_out(self, row, col):
        '''return True if row, col is out of bounds according to header'''
        return ((col < 0) or (col > self.header['ncol']) or
               (row < 0) or (row > self.header['nrow']))

    def sample(self, coords, bounds_warning=True):
        '''sample Idf for sequence of X,Y coordinates'''
        self.check_read()

        values = self.read()
        for x, y in coords:
            col = int((x - self.header['xmin']) / self.header['dx'])
            row = int((self.header['ymax'] - y) / self.header['dy'])
            if self.is_out(row, col):
                if bounds_warning:
                    logging.warning((
                        'coordinate pair x, y = {x:.3f}, {y:.3f} out of bounds'
                        .format(x=x, y=y)))
                yield (np.nan,)
            else:
                yield (values[row, col],)

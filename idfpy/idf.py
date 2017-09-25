#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import numpy as np

from enum import Enum
import logging
import struct


class IdfFileHeaderFormat(object):
    '''Static class containing IDF file header definition'''
    fields = [
    ('lahey', 'i', 4),
    ('ncol', 'i', 4),
    ('nrow', 'i', 4),
    ('xmin', '7', 4),
    ('xmax', '7', 4),
    ('ymin', '7', 4),
    ('ymax', '7', 4),
    ('dmin', '7', 4),
    ('dmax', '7', 4),
    ('nodata', '7', 4),
    ('ieq', '?', 1),
    ('itb', '?', 1),
    ('mfct' 'x', 2),
    ]

    @property
    @staticmethod
    def names(self):
        return [n for n, f, l in self.fields]

    @property
    @staticmethod
    def format(self):
        return ''.join(f for n, f, l in self.fields)

    @property
    @staticmethod
    def length(self):
        return sum(l for n, f, l in self.fields)

    @property
    @staticmethod
    def multiplication_factors(self):
        return {
            1: 1e2,
            2: 1e-2,
            3: 1e3,
            4: 1e-3,
            5: 1e3,
            6: 1e-3
            }


class IdfFileMode(Enum):
    '''IDF file binary read or write mode'''
    rb = 0
    wb = 1


class IdfFile(object):
    '''iMOD IDF file read and write object'''
    def __init__(self, filepath, mode='rb', header=None):
        # set filepath as property
        self.filepath = filepath

        # set other default properties
        self.closed = True
        self.nodatavals = []
        self.endofheader = 0

        # get mode enum and set as property
        try:
            self.mode = IdfFileMode[mode]
        except KeyError:
            raise ValueError(
                "mode string must be one of 'rb' or 'wb', not {}".format(mode))

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

    def __enter__(self):
        '''enter with statement block'''
        self.open()
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
            raise IOError('cannot read closed IDF file')
        return True

    def read_header(self, is_checked=False):
        '''read header from IDF file'''
        if not is_checked:
            self.check_read()

        # read values according to headerformat and save in dict
        header_values = struct.unpack(
            IdfFileHeaderFormat.format,
            self.f.read(IdfFileHeaderFormat.length,
            ))
        header = {n: v
            for n, v in zip(IdfFileHeaderFormat.names, header_values)
            }

        # transform multiplication factors
        header['mfct'] = (IdfFileHeaderFormat
            .multiplication_factors.get(ord(header['mfct']), 1)
            )

        # read conditional values from header
        if not header['ieq']:
            header['dx'], header['dy'] = struct.unpack('2f',
                self.f.read(4*2))
        if header['itb']:
            header['top'], header['bot'] = struct.unpack('2f',
                self.f.read(4*2))
        if header['ieq']:
            header['dx(col)'] = struct.unpack('2f',
                self.f.read(4*header['ncol']))
            header['dy(row)'] = struct.unpack('2f',
                self.f.read(4*header['nrow']))

        # set nodata value and end of header position to self
        self.nodatavals = [self.header['nodata'], ]
        self.endofheader = self.f.tell()

        return header

    def read(self, masked=False):
        '''read values from IDF file and return data as (masked) array'''
        is_checked = self.check_read()
        if not self.header:
            self.header = self.read_header(is_checked=is_checked)

        # read values
        values = np.fromfile(self.f, np.float32,
            self.header['nrow'] * self.header['ncol'])
        self.f.seek(self.endofheader)

        # reshape values to array shape(nrow, ncol)
        values = values.reshape(self.header['nrow'], self.header['ncol'])

        # apply multiplication factors if present
        values *= self.header['mfct']
        if self.header['mfct'] > 4:
            if self.header['ieq']:
                cellsize = self.header['dx'] * self.header['dy']
                if self.header['mfct'] == 5:
                    values /= cellsize
                elif self.header['mfct'] == 6:
                    values *= cellsize
            else:
                cellsize = np.meshrid(self.header['dx(col)'],
                    self.header['dy(col)'])
                if self.header['mfct'] == 5:
                    values /= cellsize
                elif self.header['mfct'] == 6:
                    values *= cellsize
        if masked:
            return np.ma.masked_values(values, self.nodatavals[0])
        else:
            return values

    def check_write(self):
        '''check if write to file is ok'''
        if self.mode != IdfFileMode.wb:
            raise ValueError("cannot read in '{}' mode".format(self.mode.name))
        if self.closed:
            raise IOError('cannot write to closed IDF file')
        if not self.header:
            raise ValueError('cannot write when header is empty')
        return True

    def write_header(self, is_checked=False):
        '''write header to file'''
        if not is_checked:
            self.check_write()

        # write values according to headerformat
        header_values = [self.header[k] for k in IdfFileHeaderFormat.names]
        self.f.write(struct.pack(IdfFileHeaderFormat.format, header_values))

        # write conditional values
        if not self.header['ieq']:
            self.f.write(struct.pack('f', self.header['dx']))
            self.f.write(struct.pack('f', self.header['dy']))
        if self.header['itb']:
            self.f.write(struct.pack('f', self.header['top']))
            self.f.write(struct.pack('f', self.header['bot']))
        if self.header['ieq']:
            raise NotImplementedError('write method ieq=true not implemented')

    def write(self, array):
        '''write to header and values to file'''
        is_checked = self.check_write()

        # write header
        self.write_header(is_checked=is_checked)

        # write values
        flattened = array.flatten()
        self.f.write(struct.pack('f' * len(flattened), *flattened))

    def is_out(self, row, col):
        '''return True if row, col is out of bounds according to header'''
        return ((col < 0) or (col > self.header['ncol']) or
               (row < 0) or (row > self.header['nrow']))

    def sample(self, coords, bounds_warning=True):
        '''sample IDF for sequence of X,Y coordinates'''
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

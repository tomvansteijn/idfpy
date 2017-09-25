#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import idfpy

def main():
    samplefile = r'bxk1-d-ck.idf'
    # open Idf file handle -->
    with idfpy.open(samplefile) as src:
        print('opening {f:}'.format(f=samplefile))
        print(src)
        sample = src.read(masked=True)
        print(len(repr(src))*'-')
        # <-- close idf file handle

    print('sample Idf min: {:.2f}'.format(sample.min()))
    print('sample Idf max: {:.2f}'.format(sample.max()))
    print('sample Idf mean: {:.2f}'.format(sample.mean()))
    print('sample Idf coverage: {:.0f}%'.format(
       (1 - sample.mask.sum() / sample.mask.size) * 1e2
        ))

if __name__ == '__main__':
    main()

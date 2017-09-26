#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


def example_1():
    import idfpy
    with idfpy.open('kh.idf') as src:
        kh = src.read(masked=True)

    print('kh mean: {:.1f}'.format(kh.mean()))
    print('kh coverage: {:.1f}%'.format(
        kh.mask.sum() / kh.mask.count * 1e2
        ))

def example_2():
    import idfpy
    coords = [(250_000., 400_000.), ]
    with idfpy.open('kh.idf') as src:
        values = [v[0] for v in src.sample(coords)]

    print(values)

if __name__ == '__main__':
    example_1()
    example_2()

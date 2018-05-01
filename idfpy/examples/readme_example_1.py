#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


def example_1():
    import idfpy

    with idfpy.open('bxk1-d-ck.idf') as src:
        bxk1d = src.read(masked=True)

    print('bxk1d mean: {:.1f}'.format(bxk1d.mean()))
    print('bxk1d coverage: {:.1f}%'.format(
        (1 - bxk1d.mask.sum() / bxk1d.mask.size) * 1e2
        ))


if __name__ == '__main__':
    example_1()

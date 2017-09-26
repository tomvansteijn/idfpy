#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


def example_2():
    import idfpy
    coords = [(255_872., 485_430.), ]
    with idfpy.open('bxk1-d-ck.idf') as src:
        values = [v[0] for v in src.sample(coords)]

    print(values)

if __name__ == '__main__':
    example_2()

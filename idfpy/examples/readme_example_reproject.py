#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV


def example_reproject():
    import idfpy

    from matplotlib import pyplot as plt
    from rasterio import Affine
    from rasterio.crs import CRS
    from rasterio.warp import reproject, Resampling
    import numpy as np

    with idfpy.open('bxk1-d-ck.idf') as src:
        a = src.read(masked=True)
        nr, nc = src.header['nrow'], src.header['ncol']
        dx, dy = src.header['dx'], src.header['dy']
        src_transform = Affine.from_gdal(*src.geotransform)

    # define new grid transform (same extent, 10 times resolution)
    dst_transform = Affine.translation(src_transform.c, src_transform.f)
    dst_transform *= Affine.scale(dx / 10., -dy / 10.)

    # define coordinate system (here RD New)
    src_crs = CRS.from_epsg(28992)

    # initialize new data array
    b = np.empty((10*nr, 10*nc))

    # reproject using Rasterio
    reproject(
        source=a,
        destination=b,
        src_transform=src_transform,
        dst_transform=dst_transform,
        src_crs=src_crs,
        dst_crs=src_crs,
        resampling=Resampling.bilinear,
        )

    # result as masked array
    b = np.ma.masked_equal(b, a.fill_value)

    # plot images
    fig, axes = plt.subplots(nrows=2, ncols=1)
    axes[0].imshow(a.filled(np.nan))
    axes[0].set_title('bxk1 original')
    axes[1].imshow(b.filled(np.nan))
    axes[1].set_title('bxk1 resampled')
    plt.show()


if __name__ == '__main__':
    example_reproject()

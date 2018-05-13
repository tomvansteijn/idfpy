#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from idf import IdfFile

from rasterio import Affine
from rasterio.crs import CRS


class IdfRaster(IdfFile):
    def to_raster(self, fp=None, epsg=28992, driver='AAIGrid'):
        """export Idf to a geotiff"""
        self.check_read()
        self.update_header()

        if fp is None:
            fp = self.filepath.replace('.idf', '.geotiff')
            logging.warning('no filepath was given, exported to {fp}'.format(fp=fp))

        # set profile
        profile = {
            'width': self.header['ncol'],
            'height': self.header['nrow'],
            'transform': Affine.from_gdal(*self.geotransform),
            'nodata': self.header['nodata'],
            'count': 1,
            'dtype': rasterio.float64,
            'driver': driver,
            'crs': CRS.from_epsg(epsg),
        }

        logging.info('writing to {f:}'.format(f=fp))
        with rasterio.open(fp, 'w', **profile) as dst:
            dst.write(self.masked_data.astype(profile['dtype']), 1)
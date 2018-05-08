import idfpy

import rasterio
from rasterio.crs import CRS
from rasterio import Affine


def main():
    samplefile = r'bxk1-d-ck.idf'
    tiffile = samplefile.replace('.idf', '.geotiff')
    dtype = rasterio.float64
    driver = 'AAIGrid'
    crs = CRS.from_epsg(28992)

    # read data from idf file
    idffile = idfpy.IdfFile(filepath=samplefile, mode='rb')
    geotransform = idffile.geotransform
    height = idffile.header['nrow']
    width = idffile.header['ncol']
    nodata = idffile.header['nodata']
    transform = Affine.from_gdal(*geotransform)

    # write data from idf file to geotiff with rasterio
    profile = {
        'width': width,
        'height': height,
        'count': 1,
        'dtype': dtype,
        'driver': driver,
        'crs': crs,
        'transform': transform,
        'nodata': nodata,
    }

    # the default profile would be sufficient for the example, however the profile dict shows how to make the export
    # profile
    idffile.to_raster(tiffile, **profile)


if __name__ == '__main__':
    main()

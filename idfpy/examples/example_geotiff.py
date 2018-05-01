import idfpy
from osgeo import gdal, osr


def main():
    samplefile = r'bxk1-d-ck.idf'
    tiffile = samplefile.replace('.idf', '.geotiff')

    # read data from idf file
    idffile = idfpy.IdfFile(filepath=samplefile, mode='rb')
    data = idffile.masked_data
    geotransform = idffile.geotransform
    height, width = data.shape
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(28992)

    # write data from idf file to geotiff
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(tiffile, width, height, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(geotransform)
    ds.SetProjection(srs.ExportToWkt())
    ds.GetRasterBand(1).WriteArray(data.data)
    ds.GetRasterBand(1).SetNoDataValue(idffile.header['nodata'])


if __name__ == '__main__':
    main()

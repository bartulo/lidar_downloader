import pdal
import json
from osgeo import gdal, osr
import numpy as np

class HeightMap():
    def __init__( self, fichero, tipo, lng, lat ):
        self.tipos = {
                    'matorral': {
                        'height': '[0.2:4]',
                        'filename': 'matorral_{}_{}.tif'.format( lng, lat ),
                        },
                    'arbolado': {
                        'height': '[4:50]',
                        'filename': 'arbolado_{}_{}.tif'.format( lng, lat ),
                        }
                }

        self.bounds = ([int(lng) * 1000, (int(lng) + 1) * 1000], [(int(lat) - 1) * 1000, int(lat) * 1000])

        self.pdalPipeline = [
                fichero,
                {
                    'type': 'filters.hag_delaunay',
                    },
                {
                    'type': 'filters.range',
                    'limits': 'HeightAboveGround{}, Classification[3:5]'.format( self.tipos[tipo]['height'] )
                    },
                {
                    'type': 'writers.gdal',
                    'filename': self.tipos[tipo]['filename'],
                    'resolution': '2.5',
                    'dimension': 'HeightAboveGround',
                    'output_type': 'max',
                    'bounds': str(self.bounds)
                    }
                ]

    def create( self ):
        b = json.dumps(self.pdalPipeline)
        pipeline = pdal.Pipeline(b)
        count = pipeline.execute()

class FuelMap():
    def __init__( self, lng, lat ):
        self.ds_arb = gdal.Open( 'arbolado_{}_{}.tif'.format( lng, lat ) )
        self.array_arb = np.array(self.ds_arb.ReadAsArray())

        self.ds_mat = gdal.Open( 'matorral_{}_{}.tif'.format( lng, lat ) )
        self.array_mat = np.array(self.ds_mat.ReadAsArray())
    
        self.originX = self.ds_arb.GetGeoTransform()[0]
        self.originY = self.ds_arb.GetGeoTransform()[3]

        self.new_array = np.zeros([40, 40])

    def calculate( self ):
        for new_col in range(self.new_array.shape[0]):
            for new_row in range(self.new_array.shape[1]):
                arb = np.full(100, np.nan)
                mat = np.full(100, np.nan)
                amb = np.full(100, np.nan)
                coef_arb = 0
                coef_amb = 0
                coef_mat = 0
                for col in range(10):
                    for row in range(10):
                        data_arb = self.array_arb[new_col * 10 + col][new_row * 10 + row]
                        data_mat = self.array_mat[new_col * 10 + col][new_row * 10 + row]
                        if data_arb != -9999 and data_mat != -9999:
                            amb[col * 10 + row] = data_arb
                            coef_amb += 1
                        if data_mat != -9999 and data_arb == -9999:
                            mat[col * 10 + row] = data_mat
                            coef_mat += 1
                        if data_arb != -9999 and data_mat == -9999:
                            arb[col * 10 + row] = data_arb
                            coef_arb += 1

                if coef_arb + coef_mat + coef_amb > 66:
                    if coef_arb >= coef_amb and coef_arb >= coef_mat:
        #                 pto = getCoordinates(new_col, new_row)
        #                 sp1 = consulta(pto)
        #                 if sp1 == 21:
        #                     self.new_array[new_col, new_row] = 8
        #                 else:
        #                     self.new_array[new_col, new_row] = 9
                        self.new_array[new_col, new_row] = 8
                    elif coef_mat >= coef_amb and coef_mat >= coef_arb:
                        if np.nanmean(mat) < 0.8:
                            self.new_array[new_col, new_row] = 5
                        elif np.nanmean(mat) < 1.6:
                            self.new_array[new_col, new_row] = 6
                        else:
                            self.new_array[new_col, new_row] = 4
                    else:
                        self.new_array[new_col, new_row] = 7
                else:
        #             pto = getCoordinates(new_col, new_row)
        #             clas = consulta2(pto)
        #                 if clas == 300:
        #                     self.new_array[new_col, new_row] = 0
        #                 else:
        #                     if coef_mat + coef_arb + coef_amb < 33:
        #                         self.new_array[new_col, new_row] = 1
        #                     else:
        #                         self.new_array[new_col, new_row] = 2
                            if coef_mat + coef_arb + coef_amb < 33:
                                self.new_array[new_col, new_row] = 1
                            else:
                                self.new_array[new_col, new_row] = 2

    def create_image( self ):
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create('probando.tif', 80, 80, 1, gdal.GDT_Byte)
        outRaster.SetGeoTransform((self.originX, 25, 0, self.originY, 0, -25))
        outRaster.GetRasterBand(1).WriteArray(self.new_array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(25830)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outRaster.FlushCache()

import pandas as pd
import numpy as np
import datetime as dt
import typing as t
from arcgis.features import GeoAccessor, FeatureLayer
from arcgis.gis import GIS
import arcpy


def main():
    """ Main program """

    #pgis = GIS("pro")
    input_lyr = arcpy.GetParameter(0)
    #aprx = arcpy.mp.ArcGISProject("CURRENT")
    #active_map = aprx.activeMap

    service_url = input_lyr.connectionProperties["connection_info"]["url"]
    arcpy.AddMessage(f'Input: {input_lyr.connectionProperties}')

    featurelayer_url = service_url + "/" + input_lyr.connectionProperties["dataset"]
    featurelayer_source = FeatureLayer(featurelayer_url)
    
    spatial_df_hostedfeature = pd.DataFrame.spatial.from_layer(featurelayer_source)


import pandas as pd
import numpy as np
import datetime as dt
import typing as t
from arcgis.features import GeoAccessor, FeatureLayer
from arcgis.gis import GIS
import arcpy


def download_attachments(fl_hf, png_folder):
    '''
    Downloads all attachments from a feature layer and saves them in a folder
    '''
    items = fl_hf.query()
    arcpy.AddMessage(f'Dataframe: {items.sdf}')
    attachments = fl_hf.attachments.search()
    


def main():
    """ Main program """

    # pgis = GIS("pro")
    input_lyr = arcpy.GetParameter(0)
    # aprx = arcpy.mp.ArcGISProject("CURRENT")
    # active_map = aprx.activeMap
    
    service_url = input_lyr.connectionProperties["connection_info"]["url"]
    fl_url = service_url + "/" + input_lyr.connectionProperties["dataset"]
    fl_hf = FeatureLayer(fl_url)

    spatial_df_hostedfeature = pd.DataFrame.spatial.from_layer(
        featurelayer_source)


if __name__ == "__main__":
    main()

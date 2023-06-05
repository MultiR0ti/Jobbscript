#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################
# For dette scriptet trengs følgende pakker: 
# pip install pymupdf
# pip install opencv-python
# pip install pypdf
# pip install cv2
############################################

import arcgis_helper_functions as ahf
# Using functions in other modules
import sys
sys.path.append('../')

# For import excel from GS
import os
import pandas as pd
# For interacting with Arcgis
import arcpy
from arcgis.features import GeoAccessor
from arcgis.gis import GIS
#  For creating pngs from pdfs
from pathlib import Path
import numpy as np
from div_scripts.pdf2images_jdr import pdf2img



def main():
    """ Main program 
    This is a controller function which runs all the functions that we want to use from the arcgis_helper_functions module.
    """
    arcpy.env.overwriteOutput = True
    fc_name = arcpy.GetParameterAsText(0)
    ws = arcpy.GetParameterAsText(1)
    crs = arcpy.GetParameterAsText(2)
    xl_file = arcpy.GetParameterAsText(3)
    pdf_folder = arcpy.GetParameterAsText(4)
    params = arcpy.GetParameterInfo()

    # Create pngs from PDFs:
    arcpy.AddMessage(f'Creating pictures from PDF folder: {pdf_folder}')
    pdf2img(pdf_folder)
    
    fc_out = os.path.join(ws, arcpy.ValidateFieldName(fc_name))
    symbology_lyr = r'\\nsv2-nasuni-02\GIS\03_FO\Geo\01_Felles\LYRS\borepoints\DictSymbology_TwoLabelClassesCG.lyrx'
    cols = ['Borhull', 'X', 'Y', 'Z', 'Metode', 'Stopp', 'Løsm', 'Fjell']

    if xl_file.endswith('.xls'):
        df = pd.read_html(xl_file, decimal=',', thousands=None)[0][cols]
    else:
        df = pd.read_excel(xl_file, engine='openpyxl', usecols=cols)
    
    df['Borhull'] = df['Borhull'].astype("string")
    df['Tolket'] = df.apply(ahf.tolket, axis=1)
    df['Bergkote'] = df.apply(ahf.bergkote, axis=1)
    df['kommentar'] = df.apply(ahf.z_kom, axis=1)
    df['kvikkleire'] = '0' # df.apply(ahf.kvikkleire, axis=1) # update
    df['Bilde'] = df.apply(ahf.bilde, url=pdf_folder, axis=1)
    arcpy.AddMessage(f'Creating feature class with columns: {df.columns}')

    # Round relvant columns
    round_cols = ['Z','Løsm','Fjell']
    df[round_cols] = df[round_cols].round(1)

    # Check to see if there are any Prøveserier
    if ahf.check_if_proveserie_exists_in_image_folder(pdf_folder):
        df['Bilde_PR'] = df.apply(ahf.bildePR, url=pdf_folder, axis=1)

    sedf = pd.DataFrame.spatial.from_xy(df, 'Y', 'X', sr=crs)
    sedf['Metode'] = sedf['Metode'].apply(ahf.remove_word, word='Tolk')
    sedf.spatial.to_featureclass(location=fc_out)

    arcpy.AddMessage(f'Adding dictionary symbology from {symbology_lyr}.')
    out_lyr = arcpy.MakeFeatureLayer_management(fc_out, fc_name)
    params[5].symbology = symbology_lyr
    arcpy.SetParameterAsText(5, out_lyr)

    # Enable attachments:
    # The input feature class must first be GDB attachments enabled
    arcpy.EnableAttachments_management(fc_out)
    # Add sounding profile
    arcpy.AddMessage(f'Adding pictures as attachments...')
    ahf.add_picture(fc_out, 'OBJECTID', 'Bilde')
    
    if ahf.check_if_proveserie_exists_in_image_folder(pdf_folder):
        ahf.add_picture(fc_out, 'OBJECTID', 'Bilde_PR')

    arcpy.AddMessage(f'Adding domain to feature layer attribute kvikkleire')
    ahf.create_kvikkleire_domain(ws, fc_out)

if __name__ == "__main__":
    main()


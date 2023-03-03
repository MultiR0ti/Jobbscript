#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  For import execel from GS
import os
import arcpy
import pandas as pd
from arcgis.features import GeoAccessor
from arcgis.gis import GIS

#  For creating pngs from pdfs
import fitz  # pymupdf
from pathlib import Path
import cv2 # pip install opencv-python
import numpy as np

from arcgis.features import GeoAccessor, FeatureLayer
from arcgis.gis import GIS

#  Create pngs from PDFs: Two functions clip_image and pdf2img 
def clip_image(i, name):

    img = cv2.imread(i)  # Read in the image and convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = 255*(gray < 128).astype(np.uint8)  # To invert the text to white
    coords = cv2.findNonZero(gray)  # Find all non-zero points (text)
    x, y, w, h = cv2.boundingRect(coords)  # Find minimum spanning bounding box
    rect = img[y:y+h, x:x+w]  # Crop the image - note we do this on the original image
    print(f'Cropping image {name} x:{x}, y:{y}, w:{w}, h:{h}')
    cv2.imwrite(i, rect)  # Save the image


def pdf2img(pdf_path):
    """
    p: path of pdf directory
    requires 'clip_image' function
    """
    p_out = pdf_path + r'\images'
    Path(p_out).mkdir(parents=True, exist_ok=True)  # create the 'images' folder if it doesn't exist
    path = Path(pdf_path)
    l_pdfs = [f for f in path.glob('*.pdf')]
    for pdf in l_pdfs:
        print(f'Opening: {pdf}')
        doc = fitz.open(pdf)
        page = doc.load_page(0)
        zoom = 2
        zz = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=zz)
        f_out = os.path.join(p_out, pdf.stem + '.png')
        pix.save(f_out)
        print(f' rect {page.rect}')
        print(f' CB {page.cropbox}')

        try:
            clip_image(f_out, pdf.stem)
        except:
            arcpy.AddMessage(f'failed clip on {f_out}')


"""
Example: You have a folder of digital photographs of vacant homes; the photos
         are named according to the ParcelID of the house in the picture. You'll 
         add these photos to a parcel feature class as attachments.
"""


def add_picture(input_fc, inputField, pathField):
    # The input feature class must first be GDB attachments enabled
    arcpy.EnableAttachments_management(input_fc)
    # Use the match table with the Add Attachments tool
    arcpy.AddAttachments_management(input_fc, inputField, input_fc, inputField, 
                                    pathField, None)


def remove_word(sentence, word):
    """
        Input:
            sentence: string
            word: word to remove
        Output:
            returns sentence without word
    """
    if isinstance(sentence, str):
        return sentence.replace(word, '').strip()
    else:
        return None


def tolket(row):
    val = ''
    if isinstance(row['Metode'], str):        
        if 'Tolk' in row['Metode']:
            val = 'Tolk'
    return val


def bergkote(row):
    if row['Stopp'] in [93,94]:
        val = str(round(row['Z'] - row['Løsm'], 2))
    else:
        val = '~'
    return val


def z_kom(row):
    if row['Z'] == 0:
        val = 'Missing Z'
    else:
        val = ''
    return val


def bilde(row, url):
    val = url + r'\images' + "\\" + row['Borhull'] + '.png'
    arcpy.AddMessage(val)
    return val


def df_from_geosuite(xl_file: str, pdf_folder: str, crs: int) -> pd.DataFrame:
    cols = ['Borhull', 'X', 'Y', 'Z', 'Metode', 'Stopp', 'Løsm', 'Fjell']

    if xl_file.endswith('.xls'):
        df = pd.read_html(xl_file, decimal=',', thousands=None)[0][cols]
    else:
        df = pd.read_excel(xl_file, engine='openpyxl', usecols=cols)

    df['Borhull'] = df['Borhull'].astype("string")
    arcpy.AddMessage(df.dtypes)
    df['Tolket'] = df.apply(tolket, axis=1)
    sedf['Metode'] = sedf['Metode'].apply(remove_word, word='Tolk')
    df['Bergkote'] = df.apply(bergkote, axis=1)
    df['kommentar'] = df.apply(z_kom, axis=1)
    df['Bilde'] = df.apply(bilde, url=pdf_folder, axis=1)

    # Lower case columns:
    df.columns = [x.lower() for x in df.columns]


    # convert df to spatially enabled dataframe
    sedf = pd.DataFrame.spatial.from_xy(df, "y", "x", sr=crs)  
    # notice the X and Y positions


    return sedf


def main():
    """ Main program """
    arcpy.env.overwriteOutput = True
    fc_in = arcpy.GetParameterAsText(0)
    ws = arcpy.GetParameterAsText(1)
    
    arcpy.AddMessage(pdf_folder)
    params = arcpy.GetParameterInfo() 

    pgis = GIS("pro")
    input_lyr = arcpy.GetParameter(0)
    xl_file = arcpy.GetParameterAsText(1)
    xl_crs = arcpy.GetParameter(2)
    p_key = arcpy.GetParameterAsText(3)
    pdf_folder = arcpy.GetParameterAsText(4)


    aprx = arcpy.mp.ArcGISProject("CURRENT")
    active_map = aprx.activeMap

    service_url = input_lyr.connectionProperties["connection_info"]["url"]
    bp_url = service_url + "/" + input_lyr.connectionProperties["dataset"]
    bp_source = FeatureLayer(bp_url)
    sdf_hf = pd.DataFrame.spatial.from_layer(bp_source)

    # New features from updated excel:
    sdf_adds = df_from_geosuite(xl_file, pdf_folder, xl_crs)

    if sdf_adds.spatial.sr != sdf_hf.spatial.sr:
        arcpy.AddMessage(
            f"XL CRS {sdf_adds.spatial.sr} not equal to {sdf_hf.spatial.sr}"
        )
        sdf_adds["SHAPE"] = sdf_adds["SHAPE"].geom.project_as(sdf_hf.spatial.sr["wkid"])
        arcpy.AddMessage(
            f"Projected XL SDF to: {sdf_adds.loc[0]['SHAPE'].spatialReference}"
        )
    bp_source.edit_features(adds=sdf_adds)
    
    # Create pngs from PDFs:
    pdf2img(pdf_folder)
    
    #fc_out = os.path.join(ws, arcpy.ValidateFieldName(fc_name))


    # symbology_lyr = r'\\nsv2-nasuni-02\GIS\03_FO\Geo\01_Felles\LYRS\borepoints\ImportExcelFromGeosuite.lyrx'

    

    # out_lyr = arcpy.MakeFeatureLayer_management(fc_in)
    # params[5].symbology = symbology_lyr
    # arcpy.SetParameterAsText(5, out_lyr)

    add_picture(fc_in, 'OBJECTID', 'Bilde')



if __name__ == "__main__":
    main()




#Eksperimentelt:
    """
    # Lage til tuples
    alle_rader = list(df.itertuples(index=False, name=None))

    fields = [field.name for field in arcpy.ListFields(fc_in)]
    update_cursor = arcpy.da.InsertCursor(fc_in, fields[1:-1])
    search_cursor = arcpy.da.SearchCursor(fc_in, fields[1:-1])

    existing_rows = []
    for row in search_cursor:
        existing_rows.append(row)

    for row in alle_rader:
        if row not in existing_rows:
            update_cursor.insertRow(row)
    del update_cursor
    
    """
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


# Make a list of dict with file name and attachment
def img_folder_items(png_folder) -> list:
    '''
    Returns a list of dictionaries that contains which boreholde have new pictures
    '''
    item_name_and_attachment = []
    for item in os.listdir(png_folder):
        if item.split('.')[-1] == 'png':
            # Find file name
            file_name = item.split('.')[0]
            file_dict = {
                'file_name': file_name,
                'attachment': png_folder + '\\' + item
                }
            item_name_and_attachment.append(file_dict)
    return item_name_and_attachment

# Returns a list of dictionaries that contains the bp-name of bps with proveserieimage in png folder
def proveserie_img_teg_200(item_name_and_attachment):
    liste = [dict for dict in item_name_and_attachment if '200_' in dict.get('file_name')]
    for dict in liste:
        bp_name_and_teg_nr = dict.get('file_name').split('RIG-TEG-')[-1]
        bp_name = 'SB-' + bp_name_and_teg_nr.split('-')[1]
        teg_nr = bp_name_and_teg_nr.split('-')[2].split('_')[0]
        # Update name of prøveserie
        dict['file_name'] = bp_name
    return liste


# Returns a list of objectid of which bps that is going to be added and the attachments
def get_objectid(fl_hf, item_name_and_attachment):
    fl_features = fl_hf.query().features
    objectsandattachments = []
    for item in item_name_and_attachment:
        image_name, attachment = item.get('file_name'), item.get('attachment')
        # try:
        filtered_features = [f for f in fl_features if f.attributes['borhull'] == image_name]
        # except Exception as e:
            #print(f'Sammensvarer profil navn og nummer på bildet med linjenavnet i GIS? Bildet skal hete sonenr_sonenavn_profilnr, {type(e)}')
        if filtered_features:
            edit_feature = filtered_features[0]
        else:
            # handle the case where no matching feature was found
            edit_feature = None  # or some other default value

        if edit_feature is not None:
            oid = edit_feature.attributes.get('OBJECTID')

            objectsandattachmentdict = {
                'objectid': oid,
                'attachment': attachment
                            }
            objectsandattachments.append(objectsandattachmentdict)
    return objectsandattachments

def add_attachments(feature_layer, objectsandattachments):
    arcpy.ResetProgressor()
    arcpy.SetProgressor('step', 'Processing features...', 0, len(objectsandattachments), 1)
    a_counter = 0
    #print(objectids[0], objectids[1])
    arcpy.AddMessage(f'Feature layer: {feature_layer}')

    for odict in objectsandattachments:
        oid = odict.get('objectid')
        attachment = odict.get('attachment')
        attachment_exists_check = False
        bp_name = attachment.split('\\')[-1]
        try:
            existing_attachments = feature_layer.attachments.get_list(oid=oid)
            for picture in existing_attachments:
                if picture.get('name') == bp_name:
                    attachment_exists_check = True
        except Exception as e:
            arcpy.AddMessage(f'Could not access attachments. Error: {e}')
            attachment_exists_check = False
        if not attachment_exists_check:
            feature_layer.attachments.add(oid, attachment)
            arcpy.AddMessage(f'Added attachment {attachment} to bp {bp_name}')
            a_counter += 1
            arcpy.AddMessage(f'Attachments added: {a_counter}')
        else:
            arcpy.AddMessage(f'No new attachements added for id {oid} bp name {bp_name}')
            
        

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
    arcpy.AddMessage(f'Clipping image {i}')


def pdf2img(pdf_path):
    """
    p: path of pdf directory
    requires 'clip_image' function
    """
    p_out = pdf_path + r'\images'
    Path(p_out).mkdir(parents=True, exist_ok=True)  # create the 'images' folder if it doesn't exist
    path = Path(pdf_path)
    l_pdfs = [f for f in path.glob('*.pdf')]
    # Check if existing already
    existing_pngs = os.listdir(p_out)
    for pdf in l_pdfs:
        f_out = os.path.join(p_out, pdf.stem + '.png')
        if pdf.stem + '.png' in existing_pngs:
            arcpy.AddMessage(f'{pdf.stem} exists')
            continue
        print(f'Opening: {pdf}')
        doc = fitz.open(pdf)
        page = doc.load_page(0)
        zoom = 2
        zz = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=zz)
        pix.save(f_out)
        print(f' rect {page.rect}')
        print(f' CB {page.cropbox}')
        try:
            clip_image(f_out, pdf.stem)
            arcpy.AddMessage(f'Clipped {p_out}')
        except:
            arcpy.AddMessage(f'failed clip on {f_out}')



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
    #arcpy.AddMessage(val)
    return val


def df_from_geosuite(xl_file: str, pdf_folder: str, crs) -> pd.DataFrame:
    cols = ['Borhull', 'X', 'Y', 'Z', 'Metode', 'Stopp', 'Løsm', 'Fjell']

    if xl_file.endswith('.xls'):
        df = pd.read_html(xl_file, decimal=',', thousands=None)[0][cols]
    else:
        df = pd.read_excel(xl_file, engine='openpyxl', usecols=cols)

    df['Borhull'] = df['Borhull'].astype("string")
    arcpy.AddMessage(df.dtypes)
    df['Tolket'] = df.apply(tolket, axis=1)
    df['Metode'] = df['Metode'].apply(remove_word, word='Tolk')
    df['Bergkote'] = df.apply(bergkote, axis=1)
    df['kommentar'] = df.apply(z_kom, axis=1)
    df['Bilde'] = df.apply(bilde, url=pdf_folder, axis=1)
    df.columns = [x.lower() for x in df.columns]

    #print(df.head())

    # convert df to spatially enabled dataframe
    sedf = pd.DataFrame.spatial.from_xy(df, "y", "x", sr=crs)  
    # notice the X and Y positions
    return df #sedf




def main():
    """ Main program """

    pgis = GIS("pro")
    input_lyr = arcpy.GetParameter(0)
    xl_file = arcpy.GetParameterAsText(1)
    xl_crs = arcpy.GetParameter(2)
    p_key = arcpy.GetParameterAsText(3)
    pdf_folder = arcpy.GetParameterAsText(4)
    png_folder = pdf_folder + r'\images'

    # Labtegninger, spesifik for sarpsbru:
    lab_pdf = r'\\nsv2-nasuni-02\fredrikstad\Prosjekt\O10245\10245026-01\10245026-01-03_ARBEIDSOMRAADE\21_fagomraade\11_Geoteknikk\10245026-03-TEGNINGER\GeoLab'
    lab_png = r'\\nsv2-nasuni-02\fredrikstad\Prosjekt\O10245\10245026-01\10245026-01-03_ARBEIDSOMRAADE\21_fagomraade\11_Geoteknikk\10245026-03-TEGNINGER\GeoLab\images'
    # Create pngs from PDFs:
    pdf2img(pdf_folder)
    pdf2img(lab_pdf)


    aprx = arcpy.mp.ArcGISProject("CURRENT")
    active_map = aprx.activeMap

    service_url = input_lyr.connectionProperties["connection_info"]["url"]
    arcpy.AddMessage(f'Input: {input_lyr.connectionProperties}')

    featurelayer_url = service_url + "/" + input_lyr.connectionProperties["dataset"]
    featurelayer_source = FeatureLayer(featurelayer_url)
    spatial_df_hostedfeature = pd.DataFrame.spatial.from_layer(featurelayer_source)

    # New features from updated excel:
    sdf_adds = df_from_geosuite(xl_file, pdf_folder, xl_crs.factoryCode)
    if sdf_adds.spatial.sr != spatial_df_hostedfeature.spatial.sr:
        arcpy.AddMessage(
            f"XL CRS {sdf_adds.spatial.sr} not equal to {spatial_df_hostedfeature.spatial.sr}"
        )
        sdf_adds["SHAPE"] = sdf_adds["SHAPE"].geom.project_as(spatial_df_hostedfeature.spatial.sr["wkid"])
        arcpy.AddMessage(
            f"Projected XL SDF to: {sdf_adds.loc[0]['SHAPE'].spatialReference}"
        )
    
    df_common = sdf_adds.loc[sdf_adds[p_key].isin(spatial_df_hostedfeature[p_key])]
    common_bps = df_common[p_key].tolist()
    arcpy.AddMessage(f"Common borpunktnr:{common_bps}")
    sdf_to_add = sdf_adds.loc[~sdf_adds[p_key].isin(spatial_df_hostedfeature[p_key])].copy()
    add_bps = sdf_to_add[p_key].tolist()
    arcpy.AddMessage(f"Adding new borpunktnr:{add_bps}")
    if add_bps:
        featurelayer_source.edit_features(adds=sdf_to_add)



    # Add pictures to new items
    items = img_folder_items(png_folder)
    objectids = get_objectid(featurelayer_source, items)
    add_attachments(featurelayer_source, objectids)

    lab_name_and_attachment = img_folder_items(lab_png)
    teg_200 = proveserie_img_teg_200(lab_name_and_attachment)
    objectids_pr_200 = get_objectid(featurelayer_source, teg_200)
    add_attachments(featurelayer_source, objectids_pr_200)


if __name__ == "__main__":
    main()


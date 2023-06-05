#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################################
# For dette scriptet trengs følgende pakker:
# pip install pymupdf
# pip install opencv-python
# pip install pypdf
############################################

#  For import excel from GS
import os
import arcpy
import pandas as pd
from arcgis.features import GeoAccessor
from arcgis.gis import GIS

#  For creating pngs from pdfs
import fitz  # pymupdf
from pathlib import Path
import cv2
import numpy as np

# Split PDFs
from pypdf import PdfWriter, PdfReader


def splitpdfs(pdffolder):
    path = Path(pdffolder)
    list_pdfs = [str(f) for f in path.glob('*PR.pdf')]
    pdf_names = []
    max_i = 1 if len(list_pdfs) > 0 else 0
    for pdf in list_pdfs:
        pdfname = pdf.split("\\")[-1].split('.')[0]
        pdf_names.append(pdfname)
        inputpdf = PdfReader(open(pdf, "rb"))
        print(pdf)
        print(len(inputpdf.pages))
        for i in range(len(inputpdf.pages)):
            output = PdfWriter()
            output.add_page(inputpdf.pages[i])
            with open(pdffolder+"\\"+pdfname+"%s.pdf" % (i+1), "wb") as outputStream:
                output.write(outputStream)
            max_i = i+1 if i+1 > max_i else max_i 
    return max_i, pdf_names
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


def pdf2img(p):
    """
    p: path of pdf directory
    requires 'clip_image' function
    """
    p_out = p + r'\images'
    Path(p_out).mkdir(parents=True, exist_ok=True)  # create the 'images' folder if it doesn't exist
    path = Path(p)
    l_pdfs = [f for f in path.glob('*.pdf')]
    # Check if existing already
    existing_pngs = os.listdir(p_out)
    for pdf in l_pdfs:
        f_out = os.path.join(p_out, pdf.stem + '.png')
        if pdf.stem + '.png' in existing_pngs:
            print(f'{pdf.stem} alredy exists')
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
        except:
            print(f'failed clip on {f_out}')


def add_picture(input_fc, inputField, pathField):

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
        val = str(round(row['Z'] - row['Løsm'], 1))
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
    # arcpy.AddMessage(val)
    return val

def bildePR(row, url, nrPR, pr_pdfs):
    borhulls = [pr for pr in pr_pdfs if row['Borhull'] in pr]
    if borhulls: 
        val = url + r'\images' + "\\" + row['Borhull'] + '_PR' + str(nrPR) + '.png'
    else:
        val = ''
    arcpy.AddMessage(val)
    return val   

def kvikkleire(row):
    val = '0'
    return val

def create_kvikkleire_domain(gdb, in_features):
    # Process: Create the coded value domain
    domain_name = 'kvikkleire_script'
    in_field = 'kvikkleire'
    # arcpy.AddMessage(f'Geodatabase: {gdb}')
    try:
        arcpy.CreateDomain_management(gdb, domain_name, domain_name, "TEXT", "CODED")
        arcpy.AddMessage(f'Created domain {domain_name}')
    except:
        arcpy.AddMessage(f'Using domain {domain_name}')

    dom_dict = {
        '0': 'Ikke vurdert',
        '1': 'Påvist ikke kvikk',
        '2': 'Antatt ikke kvikk',
        '3': 'Antatt kvikk',
        '4': 'Påvist kvikk'
    }
    # Process: Add valid material types to the domain
    # use a for loop to cycle through all the domain codes in the dictionary
    for code in dom_dict:
        arcpy.AddCodedValueToDomain_management(gdb, domain_name, code, dom_dict[code])
    # Process: Constrain the material value of distribution mains
    arcpy.AssignDomainToField_management(in_features, in_field, domain_name)    

def main():
    """ Main program """
    arcpy.env.overwriteOutput = True

    fc_name = arcpy.GetParameterAsText(0)
    ws = arcpy.GetParameterAsText(1)
    crs = arcpy.GetParameterAsText(2)
    xl_file = arcpy.GetParameterAsText(3)
    pdf_folder = arcpy.GetParameterAsText(4)
    # arcpy.AddMessage(pdf_folder)
    params = arcpy.GetParameterInfo() 


    # Split pdfs into many pdfs
    max_nr_PRs, pr_pdfs = splitpdfs(pdf_folder)[0], splitpdfs(pdf_folder)[1]
    

    # Create pngs from PDFs:
    arcpy.AddMessage(f'Creating pictures from PDF folder: {pdf_folder}')
    pdf2img(pdf_folder)

    
    
    fc_out = os.path.join(ws, arcpy.ValidateFieldName(fc_name))
    symbology_lyr = r'\\nsv2-nasuni-02\GIS\03_FO\Geo\01_Felles\LYRS\borepoints\DictSymbology_TwoLabelClassesEU.lyrx'
    cols = ['Borhull', 'X', 'Y', 'Z', 'Metode', 'Stopp', 'Løsm', 'Fjell']

    if xl_file.endswith('.xls'):
        df = pd.read_html(xl_file, decimal=',', thousands=None)[0][cols]
    else:
        df = pd.read_excel(xl_file, engine='openpyxl', usecols=cols)
    
    df['Borhull'] = df['Borhull'].astype("string")
    # arcpy.AddMessage(df.dtypes)
    df['Tolket'] = df.apply(tolket, axis=1)
    df['Bergkote'] = df.apply(bergkote, axis=1)
    df['kommentar'] = df.apply(z_kom, axis=1)
    df['kvikkleire'] = df.apply(kvikkleire, axis=1)
    df['Bilde'] = df.apply(bilde, url=pdf_folder, axis=1)
    # Create a column for each prøveserie page
    if max_nr_PRs > 0:
        for i in range(max_nr_PRs):
            arcpy.AddMessage('RAD BildePR'+str(i+1))
            df['Bilde_PR'+str(i+1)] = df.apply(bildePR, url=pdf_folder, nrPR=(i+1), pr_pdfs=pr_pdfs, axis=1)
            #add_picture(fc_out, 'OBJECTID', 'Bilde_PR'+str(PR+1))

    arcpy.AddMessage(f'Creating feature class with columns: {df.columns}')


    # Round relvant columns
    round_cols = ['Z','Løsm','Fjell']
    df[round_cols] = df[round_cols].round(1)
    # Check to see if there are any Prøveserier
    # Filter out unrelevant borings
    filtered_df = df.loc[df['Løsm'] > 0.5]    

    sedf = pd.DataFrame.spatial.from_xy(filtered_df, 'Y', 'X', sr=crs)
    sedf['Metode'] = sedf['Metode'].apply(remove_word, word='Tolk')
    sedf.spatial.to_featureclass(location=fc_out)

    arcpy.AddMessage(f'Adding dictionary symbology from {symbology_lyr}.')
    out_lyr = arcpy.MakeFeatureLayer_management(fc_out, fc_name)
    params[5].symbology = symbology_lyr
    arcpy.SetParameterAsText(5, out_lyr)

    # Enable attachments:
    # The input feature class must first be GDB attachments enabled
    arcpy.EnableAttachments_management(fc_out)

    arcpy.AddMessage(f'Adding pictures as attachments...')
    # Add sounding profile
    add_picture(fc_out, 'OBJECTID', 'Bilde')
    
    if max_nr_PRs > 0:
        for PR in range(max_nr_PRs):
            add_picture(fc_out, 'OBJECTID', 'Bilde_PR'+str(PR+1))
    
    arcpy.AddMessage(f'Adding domain to feature layer attribute kvikkleire')
    create_kvikkleire_domain(ws, fc_out)

if __name__ == "__main__":
    main()


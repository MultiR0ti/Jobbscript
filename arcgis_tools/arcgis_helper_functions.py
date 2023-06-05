
import arcpy
import os
from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader
import cv2
import fitz # pymupdf
import numpy as np

# Helper functions 
def remove_word(sentence: str, word: str):
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
    """
    Adds message that the bedrock depth of the
    borepoint have been interpreted
    """
    val = ''
    if isinstance(row['Metode'], str):        
        if 'Tolk' in row['Metode']:
            val = 'Tolk'
    return val


def bergkote(row):
    """Calculates the elevation level of the bedrock and uses the sign ~ if
    bedrock has not been penetrated"""
    if row['Stopp'] in [93,94]:
        val = str(round(row['Z'] - row['Løsm'], 1))
    else:
        val = '~'
    return val


def z_kom(row):
    """Adds comments if Z-value does not exist"""
    if row['Z'] == 0:
        val = 'Missing Z'
    else:
        val = ''
    return val


def bilde(row, url: str) -> str:
    """Returns the path of the picture found for the boring. 
    Used for attaching the image with arcgis' Add Attachment function."""
    val = url + r'\images' + "\\" + row['Borhull'] + '.png'
    return val

def bildePR(row, url: str):
    """Returns the path of the picture found for the boring. 
    Used for attaching the image with arcgis' Add Attachment function."""
    val = url + r'\images' + "\\" + row['Borhull'] + '_PR' + '.png'
    return val   

def kvikkleire(row) -> str:
    """Returns a string representation of 0 for the domain function."""
    val = row['Kvikkleire'] + '0'
    return val

def create_kvikkleire_domain(gdb: str, in_features: str):
    """Creates a domain in arcgis and applies it to a field.
    Uses arcgis functions from the arcpy library."""
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


def add_picture(input_fc, inputField, pathField):

    # Use the match table with the Add Attachments tool
    arcpy.AddAttachments_management(input_fc, inputField, input_fc, inputField, 
                                    pathField, None)
    
def splitpdfs(pdffolder):
    path = Path(pdffolder)
    l_pdfs = [f for f in path.glob('*PR.pdf')]
    i0 = 0
    if len(l_pdfs) > 0:
        i0 = 1
    for pdf0 in l_pdfs:
        pdf = str(pdf0)
        pdfname = pdf.split("\\")[-1].split('.')[0]
        inputpdf = PdfReader(open(pdf, "rb"))
        for i in range(len(inputpdf.pages)):
            output = PdfWriter()
            output.add_page(inputpdf.pages[i])
            with open(pdffolder+"\\"+pdfname+"%s.pdf" % (i+1), "wb") as outputStream:
                output.write(outputStream)
            if i > i0:
                i0 = i+1
    return i0

def clip_image(image: str, name: str):
    """Clips the white spaces from the image"""
    img = cv2.imread(image)  # Read in the image and convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = 255*(gray < 128).astype(np.uint8)  # To invert the text to white
    coords = cv2.findNonZero(gray)  # Find all non-zero points (text)
    x, y, w, h = cv2.boundingRect(coords)  # Find minimum spanning bounding box
    rect = img[y:y+h, x:x+w]  # Crop the image - note we do this on the original image
    print(f'Cropping image {name} x:{x}, y:{y}, w:{w}, h:{h}')
    cv2.imwrite(image, rect)  # Save the image


def pdf2img(pdf_path: str):
    """
    pdf_path: path of pdf directory.
    Uses and requires 'clip_image' function.
    """
    img_path = pdf_path + r'\images'
    Path(img_path).mkdir(parents=True, exist_ok=True)  # create the 'images' folder if it doesn't exist
    path = Path(pdf_path)
    l_pdfs = [f for f in path.glob('*.pdf')]
    # Check if existing already
    existing_pngs = os.listdir(img_path)
    for pdf in l_pdfs:
        img = os.path.join(img_path, pdf.stem + '.png')
        if pdf.stem + '.png' in existing_pngs:
            print(f'{pdf.stem} alredy exists')
            continue
        print(f'Opening: {pdf}')
        doc = fitz.open(pdf)
        page = doc.load_page(0)
        zoom = 2
        zz = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=zz)
        pix.save(img)
        print(f' rect {page.rect}')
        print(f' CB {page.cropbox}')

        try:
            clip_image(img, pdf.stem)
        except:
            print(f'failed clip on {img}')

def check_if_proveserie_exists_in_image_folder(pdf_folder: str) -> bool:
    files = os.listdir(pdf_folder+"\\images")
    print(files)
    count =  sum(1 for file in files if "_PR" in file)
    if count > 0: return True
    else: return False
import os
import fitz  #pymupdf
from pathlib import Path
import cv2
import numpy as np

# path to pdf directory:
pth = r'\\nsv2-nasuni-01\Prosjekt\O10244\10244558-01\10244558-01-03 ARBEIDSOMRAADE\10244558-01 RIG\10244558-01-04 TEGNINGER\Kritiske profiler etter GRUS\PDF'
#pth = r'\\nsv2-nasuni-02\fredrikstad\Prosjekt\O10245\10245026-01\10245026-01-03_ARBEIDSOMRAADE\21_fagomraade\11_Geoteknikk\10245026-03-TEGNINGER\GeoLab'

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


pdf2img(pth)


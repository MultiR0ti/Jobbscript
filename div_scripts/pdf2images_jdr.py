import os
import fitz  # pip install pymupdf
from pathlib import Path
import cv2 # pip install opencv-python
import numpy as np

# path to pdf directory:
pth = r'\\nsv2-nasuni-01\Prosjekt\O10244\10244558-01\10244558-01-03 ARBEIDSOMRAADE\10244558-01 RIG\10244558-01-04 TEGNINGER\Kritiske profiler etter GRUS\PDF'
#pth = r'\\nsv2-nasuni-01\Prosjekt\O10244\10244558-01\10244558-01-03 ARBEIDSOMRAADE\10244558-01 RIG\10244558-01-10 GEOSUITE\GEOSUITE tidligere grunnundersøkelser\_Samlet\AUTOGRAF.RIT'

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


pdf2img(pth)


import PyPDF2 as ppdf
from fpdf import FPDF
from pdf2image import convert_from_path
import cv2
from pathlib import Path
import fitz
import os
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Users\jdr\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    )
# PDF file:
pdf_path = r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\Lay_totalsonderinger A4.pdf'
final_img_pth =  r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\images\\'


# Create images from a pdf file:
def pdf2img(pdf_path: str):
    """
    pdf_path: path of pdf directory.
    Uses and requires 'clip_image' function.
    """
    #img_path = pdf_path + r'\images'
    #Path(img_path).mkdir(parents=True, exist_ok=True)  # create the 'images' folder if it doesn't exist
    final_img_pth =  r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\images\\'
    Path(final_img_pth).mkdir(parents=True, exist_ok=True) 

    print(f'Opening: {pdf_path}')
    doc = fitz.open(pdf_path)
    for index, page in enumerate(doc.pages()):
        #thispage = page.load_page()
        zoom = 10
        zz = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=zz)
        pix.save(final_img_pth + str(index) + r'.png')
pdf2img(pdf_path)

path = Path(final_img_pth)
list_pngs = [f for f in path.glob('*.png')]
bp_names = []

for picture in list_pngs:
    img = os.path.join(final_img_pth, picture.stem + '.png')
    text = str(((pytesseract.image_to_string(Image.open(img)))))
    text.strip()
    bp_name = text.partition('\n')[0]
    bp_names.append(bp_name)



# def pdf_to_image(pdf_path, image_path):
#     # Convert the PDF to a list of PIL images
#     images = convert_from_path(pdf_path, poppler_path=r'C:\Users\jdr\OneDrive - Multiconsult\Dokumenter\poppler-0.68.0\bin')
 
#     # Loop through each image
#     for i, image in enumerate(images):
#         # Save the image
#         image.save(image_path + str(i) + '.png', "PNG")
 
# # Example usage
# pdf_to_image(pdf_path, pdf_path)

# Create images from a pdf file:
# '''def pdf2img(pdf_path: str):
#     """
#     pdf_path: path of pdf directory.
#     Uses and requires 'clip_image' function.
#     """
#     #img_path = pdf_path + r'\images'
#     #Path(img_path).mkdir(parents=True, exist_ok=True)  # create the 'images' folder if it doesn't exist
#     final_img_pth =  r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\\'

#     print(f'Opening: {pdf_path}')
#     doc = fitz.open(pdf_path)
#     for index, page in enumerate(doc.pages()):
#         #thispage = page.load_page()
#         zoom = 10
#         zz = fitz.Matrix(zoom, zoom)
#         pix = page.get_pixmap(matrix=zz)
#         pix.save(final_img_pth + str(index) + r'.png')




# pdf2img(pdf_path)'''

 


img_path = r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\0.png'
# Load the image
img = cv2.imread(img_path)
 
# Specify the coordinates for the redaction
top_left_x = 4444
top_left_y = 8050
bottom_right_x = 5450
bottom_right_y = 8170
x, y, width, height = 4444, 8050, (bottom_right_x - top_left_x), (bottom_right_y - top_left_y)
 
# Create a white rectangle to cover the desired portion of the image
white = (255, 255, 255)
img[y:y + height, x:x + width] = white
 
# # # Write text on the red rectangle using a white color
# # font = cv2.FONT_HERSHEY_SIMPLEX
# # org = (x + int(width / 4), y + int(height / 2))
# # fontScale = 1
# # color = (0, 0, 0)
# # thickness = 2
# # text = "RIG-TEG-SB-XXXX-010"
# # img = cv2.putText(img, text, org, font, fontScale, color, thickness, cv2.LINE_AA)
final_img_pth =  r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\rectpic.png'
# # # Save the resulting image
cv2.imwrite(final_img_pth, img)

img_path = final_img_pth
final_img_pth =  r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\final.png'

from PIL import Image, ImageDraw, ImageFont
def text(input_image_path, output_path):
    image = Image.open(input_image_path)
    draw = ImageDraw.Draw(image)
    font_dir = r'C:\Users\jdr\OneDrive - Multiconsult\Dokumenter\Fonts\isocpeur.ttf'
    colorblack = 'black'
    font = ImageFont.truetype(font_dir, size=110)
    text = "RIG-TEG-SB-2000-010"
    draw.text((4480, 8080), text, font=font, fill=colorblack)
    image.save(output_path)

text(img_path, final_img_pth)
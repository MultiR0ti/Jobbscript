# Import libraries
import platform
from tempfile import TemporaryDirectory
from pathlib import Path
 
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
 



# pdf_path = r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\Lay_totalsonderinger A4.pdf'
out_directory = r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger'

pic_path = r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\Totsonderinger\0.png'

# PDF_file = Path(pdf_path)

 # Store all the pages of the PDF in a variable
# image_file_list = []
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\jdr\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)
text = str(((pytesseract.image_to_string(Image.open(pic_path)))))
text.strip()
bp_name = text.partition('\n')[0]



print(bp_name)


text_file = out_directory / Path("out_text.txt")   

# with open(text_file, "a") as output_file:
#         # Open the file in append mode so that
#         # All contents of all images are added to the same file

#     text = str(((pytesseract.image_to_string(Image.open(pic_path)))))

#     # The recognized text is stored in variable text
#     # Any string processing may be applied on text
#     # Here, basic formatting has been done:
#     # In many PDFs, at line ending, if a word can't
#     # be written fully, a 'hyphen' is added.
#     # The rest of the word is written in the next line
#     # Eg: This is a sample text this word here GeeksF-
#     # orGeeks is half on first line, remaining on next.
#     # To remove this, we replace every '-\n' to ''.
#     text = text.replace("-\n", "")

#     # Finally, write the processed text to the file.
#     output_file.write(text)
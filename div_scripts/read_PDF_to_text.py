# import re
# from PyPDF2 import PdfReader

# def extract_text_from_pdf(pdf_path):
#     pdf_reader = PdfReader(pdf_path)
#     text = ''
#     for page in pdf_reader.pages:
#         page_text = page.extract_text()
#         match = re.search(r'Løsmasseprofil pkt\. (\d{2}-\d{1,2})', page_text)
#         if match:
#             text += match.group(1) + '\n'
    
#     return text

# # Usage
# pdf_path = r'\\nsv2-nasuni-01\Prosjekt\O10244\10244558-01\10244558-01-03 ARBEIDSOMRAADE\10244558-01 RIG\10244558-01-07 FELT- OG LABREGISTRERINGER\Prøveserier\ENDELIG\22647 Labresultater komplett.pdf'
# text = extract_text_from_pdf(pdf_path)
# print(text)

# from pdf2image import convert_from_path
# import pytesseract

# def extract_text_from_pdf_with_ocr(pdf_path):
#     pytesseract.pytesseract.tesseract_cmd = (
#     r"C:\Users\jdr\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
#     )
#     images = convert_from_path(pdf_path)
#     text = ''
#     for i in range(len(images)):
#         text += pytesseract.image_to_string(images[i], lang='eng')
#     return text

# # Usage
# pdf_path = r'\\nsv2-nasuni-01\Prosjekt\O10244\10244558-01\10244558-01-03 ARBEIDSOMRAADE\10244558-01 RIG\10244558-01-07 FELT- OG LABREGISTRERINGER\Prøveserier\ENDELIG\22647 Labresultater komplett.pdf'
# text = extract_text_from_pdf_with_ocr(pdf_path)
# print(text)


import re
from pdfminer.high_level import extract_text

def extract_text_from_pdf_with_pdfminer(pdf_path, pattern):
    text = extract_text(pdf_path)
    matches = re.findall(pattern, text)
    return matches

# Usage
pdf_path = r'\\nsv2-nasuni-01\Prosjekt\O10244\10244558-01\10244558-01-03 ARBEIDSOMRAADE\10244558-01 RIG\10244558-01-07 FELT- OG LABREGISTRERINGER\Prøveserier\ENDELIG\22647 Labresultater komplett.pdf'
pattern = r'(\d{2}-\d{1,2})'
matches = extract_text_from_pdf_with_pdfminer(pdf_path, pattern)
print(matches)
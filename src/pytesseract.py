import pytesseract
from PIL import Image

import xml.etree.ElementTree as ET

# Open image from path to image object
image = Image.open("/home/bruno/Uni/hOCR/assets/pdf_P-000.jpg")
#image = Image.open("/home/bruno/Uni/hOCR/assets/pdf_P-001.jpg")

# Display Image
#image.show()

# Image to string with lang option
#print(pytesseract.image_to_string(image, lang="por"))

# Multiple processing with a single file containing the list of multiple image file paths
#print(pytesseract.image_to_string('images.txt'))

# Get bounding box estimates
#print(pytesseract.image_to_boxes(image))

# Get verbose data including boxes, confidences, line and page numbers
# print(pytesseract.image_to_data(image))


# Get HOCR output
hocr = pytesseract.image_to_pdf_or_hocr(image, lang="por", extension='hocr')
with open('out.hocr', 'w+b') as f:
    f.write(hocr) 


# Get elemetTree object from xml
tree = ET.parse('out.hocr')
#print(tree)

root = tree.getroot()
par = root.findall('ocr_par','')
print(par)
#alll = list(tree.iter())
#for child in alll:
#    print(child.attrib, child.text)

#for neighbor in root.iter('neighbor'):
#    print(neighbor.attrib)









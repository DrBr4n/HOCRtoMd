import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

tree = ET.parse('out.hocr')

root = tree.getroot() #root[0] = <head>; root[1] = <body>

# advance root to the <body>
root = root[1]

# root[0] is now the first <div class='ocr_page'> 
# root[1] would be the second <div class='ocr_page'> ?

# prints all the <div class='ocr_carea'> == prints all the blocks
# for child in root[0]: print(child.tag, child.attrib)

page1 = root[0]

data = {}

# iterate by every child of page1 and extract paragraphs bbox coordinates every word to a dictionary indexed by paragraph id
for child in page1.iter():
     if child.get('class') == 'ocr_par':
             data[child.get('id')] = {'bbox':child.get('title').split()[1:],'text':""}
             last_par = child.get('id')
     if child.get('class') == 'ocrx_word':
             data[last_par]['text'] += child.text + " " #if x_wconf > k ?

# cleanup paragraphs of only whitespaces
for par in list(data.keys()):
    if data[par]['text'].isspace():
        del data[par]



image = Image.open("_.pdf_P-000.jpg")

for par in data:
    x, y, height, width = int(data[par]['bbox'][0]), int(data[par]['bbox'][1]), int(data[par]['bbox'][0]) + int(data[par]['bbox'][2]), int(data[par]['bbox'][0]) + int(data[par]['bbox'][3])
    ImageDraw.Draw(image).rectangle([x, y, height, width], fill=None, outline='green')

image.show()


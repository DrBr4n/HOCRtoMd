import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import sys 
import pytesseract

def parseArgv():
    # open image from argv[1]
    image = Image.open(sys.argv[1])

    # Create HOCR output in argv[2]
    hocr = pytesseract.image_to_pdf_or_hocr(image, lang="por", extension='hocr')
    with open(sys.argv[2], 'w+b') as f:
        f.write(hocr) 
    
    return image

def parseHocr():
    # Generate ElementTree from hocr in argv[2]
    tree = ET.parse(sys.argv[2])
    
    root = tree.getroot() #root[0] = <head>; root[1] = <body>

    # advance root to the <body>
    root = root[1]

    # root[0] is now the first <div class='ocr_page'> 
    # root[1] would be the second <div class='ocr_page'> ?

    # TODO : if there are other pages needs to iterate over them to parse
    # sets page1 to the firt page in root
    page1 = root[0]
    data = {}
    # iterate by every child of page1 and extract paragraphs bbox coordinates every word to a dictionary indexed by paragraph id
    for child in page1.iter():
        if child.get('class') == 'ocr_par':
            # get all attributes from title into a list and discard the first (bbox)
            data[child.get('id')] = {'bbox':child.get('title').split()[1:],'text':""}
            last_par = child.get('id')
        if child.get('class') == 'ocrx_word':
            data[last_par]['text'] += child.text + " " #if x_wconf > k ?

    return data 

# cleanup paragraphs of only whitespaces
#for par in list(data.keys()):
#    if data[par]['text'].isspace():
#        del data[par]

def drawBoxes(image, data):
    # draw paragraph boxes
    for par in data:
        
        x, y, height, width =  int(data[par]['bbox'][0]), int(data[par]['bbox'][1]), int(data[par]['bbox'][2]), int(data[par]['bbox'][3])
       
        ImageDraw.Draw(image).rectangle([x, y, height, width], fill=None, outline='green')

    image.show()

def main():
    image = parseArgv()
    data = parseHocr()
    breakpoint()

if __name__ == "__main__":
    main()

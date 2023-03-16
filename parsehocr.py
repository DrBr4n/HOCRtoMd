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

    # cleanup paragraphs of only whitespaces
    for par in list(data.keys()):
        if data[par]['text'].isspace():
            del data[par]
    
    return data 

def extractPhotos():
    # Generate ElementTree from hocr in argv[2]
    tree = ET.parse(sys.argv[2])
    root = tree.getroot() #root[0] = <head>; root[1] = <body>

    # TODO : if there are other pages needs to iterate over them to parse
    # sets page1 to the firt page in root
    page1 = root[1][0]
    
    # list that will hold the tupples(photo_id, [box coordinates])
    photos = []
    # iterate by every child of page1 and extract paragraphs bbox coordinates every word to a dictionary indexed by paragraph id
    for child in page1.iter():
        if child.get('class') == 'ocr_photo':
            photos.append((child.get('id'), child.get('title').split()[1:]))

    image = Image.open(sys.argv[1])
    for p in photos:
        tmpImage = image.crop((int(p[1][0]), int(p[1][1]), int(p[1][2]), int(p[1][3])))
        tmpImage.save("out/" + p[0] + ".jpg")
    
    return photos

def drawPhotosBoxes(image, photos):
    for p in photos:
        x, y, x2, y2 = int(p[1][0]), int(p[1][1]), int(p[1][2]), int(p[1][3])        
        ImageDraw.Draw(image).rectangle([x, y, x2, y2], fill=None, outline='red')

def drawParagraphBoxes(image, data):
    # draw paragraph boxes
    for par in data:    
        x, y, x2, y2 =  int(data[par]['bbox'][0]), int(data[par]['bbox'][1]), int(data[par]['bbox'][2]), int(data[par]['bbox'][3])
        ImageDraw.Draw(image).rectangle([x, y, x2, y2], fill=None, outline='green')

def drawBoxes(image, data, photos):
    drawPhotosBoxes(image, photos)    
    drawParagraphBoxes(image, data)
    image.show()

def main():
    image = parseArgv()
    data = parseHocr()
    photos = extractPhotos()
    drawBoxes(image, data, photos)

if __name__ == "__main__":
    main()

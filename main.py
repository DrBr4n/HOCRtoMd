import sys
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET
import pytesseract

class Page:
    def __init__(self, id):
        self.id = id
        self.careas = []
        self.careasIdx = -1
        self.photos = []
        self.photosIdx = -1

    def addCarea(self, c): 
        self.careasIdx += 1
        self.careas.append(c)

    def addPhoto(self, photo):
        self.photosIdx += 1
        self.photos.append(photo)

    def addPar(self, p): self.careas[self.careasIdx].addPar(p) 
    def addLine(self, l): self.careas[self.careasIdx].addLine(l) 
    def addWord(self, w): self.careas[self.careasIdx].addWord(w) 

class Photo:
    def __init__(self, id, bbox):
        self.id = id
        self.bbox = bbox

class Carea:
    def __init__(self, id, bbox):
        self.id = id
        self.bbox = bbox
        self.pars = []
        self.parsIdx = -1

    def addPar(self, p): 
        self.parsIdx += 1
        self.pars.append(p)

    def addLine(self, l): self.pars[self.parsIdx].addLine(l) 
    def addWord(self, w): self.pars[self.parsIdx].addWord(w) 

class Par:
    def __init__(self, id, bbox, lang):
        self.id = id
        self.bbox = bbox
        self.lang = lang 
        self.lines = [] 
        self.linesIdx = -1

    def addLine(self, l): 
        self.linesIdx += 1
        self.lines.append(l)

    def addWord(self, w): self.lines[self.linesIdx].addWord(w) 

class Line:
    def __init__(self, id, bbox, x_size):
        self.id = id
        self.bbox = bbox
        self.x_size = x_size
        self.words = [] 
        self.wordsIdx = -1

    def addWord(self, w): 
        self.wordsIdx += 1
        self.words.append(w)

class Word:
    def __init__(self, id, bbox, x_wconf, text):
        self.id = id
        self.bbox = bbox
        self.x_wconf = x_wconf
        self.text = text

class Photo:
    def __init__(self, id, bbox):
        self.id = id
        self.bbox = bbox
    def getId(self): return self.id
    def getBbox(self): return self.bbox

def parseArgv():
    # open image from argv[1]
    image = Image.open(sys.argv[1])

    # Create HOCR output in argv[2]
    hocr = pytesseract.image_to_pdf_or_hocr(image, config='--psm ' + sys.argv[3] , lang="por", extension='hocr')
    with open(sys.argv[2], 'w+b') as f:
        f.write(hocr) 
    
    return image

def parseHocr():
    # Generate ElementTree from hocr in argv[2]
    tree = ET.parse(sys.argv[2])
    root = tree.getroot()[1] #root[0] = <head>; root[1] = <body>
    
    page1 = root[0] # TODO : if there are other pages needs to iterate over them to parse #for page in root?

    p1 = Page(page1.get('id'))  
    for child in page1.iter():
        if child.get('class') == 'ocr_carea':
            p1.addCarea(Carea(child.get('id'), child.get('title').split()[1:5]))
        elif child.get('class') == 'ocr_par':
            p1.addPar(Par(child.get('id'), child.get('title').split()[1:5], child.get('lang')))
        elif child.get('class') == 'ocr_line' or child.get('class') == 'ocr_textfloat' or child.get('class') == 'ocr_header' or child.get('class') == 'ocr_caption':
            bbox = child.get('title').split()[1:5]
            bbox[3] = bbox[3][:-1] #clean ; in the last bbox coord
            p1.addLine(Line(child.get('id'), bbox, child.get('title').split()[9]))
        elif child.get('class') == 'ocrx_word':
            p1.addWord(Word(child.get('id'), child.get('title').split()[1:5], child.get('title').split()[6], child.text))
        elif child.get('class') == 'ocr_photo':
            p1.addPhoto(Photo(child.get('id'), child.get('title').split()[1:5]))

    return p1 

def drawCareaBoxes(image, pageObject):
    for carea in pageObject.careas:
        x, y, x2, y2 = int(carea.bbox[0]), int(carea.bbox[1]), int(carea.bbox[2]), int(carea.bbox[3])
        ImageDraw.Draw(image).rectangle([x, y, x2, y2], fill=None, outline='blue')

def drawParBoxes(image, pageObject):
    for carea in pageObject.careas:
        for paragraph in carea.pars:
            x, y, x2, y2 = int(paragraph.bbox[0]), int(paragraph.bbox[1]), int(paragraph.bbox[2]), int(paragraph.bbox[3])
            ImageDraw.Draw(image).rectangle([x, y, x2, y2], fill=None, outline='green')

def drawLinesBoxes(image, pageObject):
    for carea in pageObject.careas:
        for paragraph in carea.pars:
            for line in paragraph.lines:
                x, y, x2, y2 = int(line.bbox[0]), int(line.bbox[1]), int(line.bbox[2]), int(line.bbox[3])
                ImageDraw.Draw(image).rectangle([x, y, x2, y2], fill=None, outline='red')

def drawPhotosBoxes(image, pageObject):
    for photo in pageObject.photos:
         x, y, x2, y2 = int(photo.bbox[0]), int(photo.bbox[1]), int(photo.bbox[2]), int(photo.bbox[3])
         ImageDraw.Draw(image).rectangle([x, y, x2, y2], fill=None, outline='red')

def extractPhotos(image, pageObject):
    for photo in pageObject.photos:
        x, y, x2, y2 = int(photo.bbox[0]), int(photo.bbox[1]), int(photo.bbox[2]), int(photo.bbox[3])
        tmpImage = image.crop((x, y, x2, y2))
        tmpImage.save("out/" + photo.id + ".jpg")

def main():
    image = parseArgv()
    page1 = parseHocr()
    #drawCareaBoxes(image, page1)
    drawParBoxes(image, page1)
    #drawLinesBoxes(image, page1)
    drawPhotosBoxes(image, page1)
    extractPhotos(image, page1)
    image.show()

if __name__ == "__main__":
    main()



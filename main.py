import sys
import PIL.Image
import PIL.ImageDraw
import xml.etree.ElementTree as ET
import pytesseract
import copy


class Page:
    def __init__(self, id):
        self.id = id
        self.careas = []
        self.careasIdx = -1
        self.images = []
        self.imagesIdx = -1

    def addCarea(self, carea):
        self.careasIdx += 1
        self.careas.append(carea)

    def addImage(self, sourceImage):
        self.imagesIdx += 1
        self.images.append(sourceImage)

    def addPar(self, par): self.careas[self.careasIdx].addPar(par)
    def addLine(self, line): self.careas[self.careasIdx].addLine(line)
    def addWord(self, word): self.careas[self.careasIdx].addWord(word)


class Carea:
    def __init__(self, id, bbox):
        self.id = id
        self.bbox = bbox
        self.pars = []
        self.parsIdx = -1

    def addPar(self, par):
        self.parsIdx += 1
        self.pars.append(par)

    def addLine(self, line): self.pars[self.parsIdx].addLine(line)
    def addWord(self, word): self.pars[self.parsIdx].addWord(word)


class Par:
    def __init__(self, id, bbox, lang):
        self.id = id
        self.bbox = bbox
        self.lang = lang
        self.lines = []
        self.linesIdx = -1

    def addLine(self, line):
        self.linesIdx += 1
        self.lines.append(line)

    def addWord(self, word): self.lines[self.linesIdx].addWord(word)


class Line:
    def __init__(self, id, bbox, x_size):
        self.id = id
        self.bbox = bbox
        self.x_size = x_size
        self.words = []
        self.wordsIdx = -1

    def addWord(self, word):
        self.wordsIdx += 1
        self.words.append(word)


class Word:
    def __init__(self, id, bbox, x_wconf, text):
        self.id = id
        self.bbox = bbox
        self.x_wconf = x_wconf
        self.text = text


class My_Image:
    def __init__(self, id, bbox):
        self.id = id
        self.bbox = bbox


def parseHocr():
    # Generate ElementTree from hocr in argv[2]
    tree = ET.parse(sys.argv[2])
    root = tree.getroot()[1]    # root[0] = <head>; root[1] = <body>

    page1 = root[0]     # TODO : if there are other pages needs to iterate over them to parse #for page in root?

    p1 = Page(page1.get('id'))
    for child in page1.iter():
        ocr_class = child.get('class')
        title = child.get('title').split()

        for idx in range(len(title)):
            if title[idx] == 'bbox':
                bbox = [int(title[idx+1]), int(title[idx+2]), int(title[idx+3])]
                if title[idx+4][-1] == ';':
                    bbox.append(int(title[idx+4][:-1]))
                else:
                    bbox.append(int(title[idx+4]))
            if title[idx] == 'x_size':
                x_size = float(title[idx+1][:-1])
            if title[idx] == 'x_wconf':
                x_wconf = int(title[idx+1])

        match ocr_class:
            case 'ocr_carea':
                p1.addCarea(Carea(child.get('id'), bbox))
            case 'ocr_par':
                p1.addPar(Par(child.get('id'), bbox, child.get('lang')))
            case 'ocr_line' | 'ocr_textfloat' | 'ocr_header' | 'ocr_caption':
                p1.addLine(Line(child.get('id'), bbox, x_size))
            case 'ocrx_word':
                p1.addWord(Word(child.get('id'), bbox, x_wconf, child.text))
            case 'ocr_photo':
                p1.addImage(My_Image(child.get('id'), bbox))

    return p1


def drawCareaBoxes(sourceImage, pageObject):
    for carea in pageObject.careas:
        x, y = carea.bbox[0], carea.bbox[1]
        x2, y2 = carea.bbox[2], carea.bbox[3]
        PIL.ImageDraw.Draw(sourceImage).rectangle([x, y, x2, y2],
                                                  fill=None,
                                                  outline='red',
                                                  width=3)


def drawParBoxes(sourceImage, pageObject):
    for carea in pageObject.careas:
        for paragraph in carea.pars:
            x, y = paragraph.bbox[0], paragraph.bbox[1]
            x2, y2 = paragraph.bbox[2], paragraph.bbox[3]
            PIL.ImageDraw.Draw(sourceImage).rectangle([x, y, x2, y2],
                                                      fill=None,
                                                      outline='blue',
                                                      width=2)


def drawLinesBoxes(sourceImage, pageObject):
    for carea in pageObject.careas:
        for paragraph in carea.pars:
            for line in paragraph.lines:
                x, y = line.bbox[0], line.bbox[1]
                x2, y2 = line.bbox[2], line.bbox[3]
                PIL.ImageDraw.Draw(sourceImage).rectangle([x, y, x2, y2],
                                                          fill=None,
                                                          outline='green')


def drawImageBoxes(sourceImage, pageObject):
    for image in pageObject.images:
        x, y = image.bbox[0], image.bbox[1],
        x2, y2 = image.bbox[2], image.bbox[3]
        PIL.ImageDraw.Draw(sourceImage).rectangle([x, y, x2, y2],
                                                  fill=None,
                                                  outline='purple')


def drawArticlesBoxes(sourceImage, artigos):
    for artigo in artigos:
        x, y = artigo.bbox[0], artigo.bbox[1]
        x2, y2 = artigo.bbox[2], artigo.bbox[3]
        PIL.ImageDraw.Draw(sourceImage).rectangle([x, y, x2, y2],
                                                  fill=None,
                                                  outline='blue',
                                                  width=2)


def extractImages(sourceImage, pageObject):
    for image in pageObject.images:
        x, y = image.bbox[0], image.bbox[1]
        x2, y2 = image.bbox[2], image.bbox[3]
        tmpImage = sourceImage.crop((x, y, x2, y2))
        tmpImage.save("out/" + image.id + ".jpg")


def organizeArticles(articles):

    nAr = len(articles) - 1
    idx = 0
    lastIdx = 0
    while (idx < nAr):
        if articles[idx].pars[0].lines[0].x_size > articles[idx+1].pars[0].lines[0].x_size:
            # if articles[idx+1].bbox[3] - articles[idx].bbox[3] < 100:
            articles[idx].pars += articles[idx+1].pars
            del articles[idx+1]
            nAr -= 1
        else:
            idx += 1
            lastIdx += 1


    toRemove = []
    """
    for idx in range(len(articles) - 1):
        # if x_size1 > x_size2
        print(articles[idx].id, articles[idx].pars[0].lines[0].x_size, articles[idx].id, articles[idx+1].pars[0].lines[0].x_size)
        if articles[idx].pars[0].lines[0].x_size > articles[idx+1].pars[0].lines[0].x_size:
            print('toRemove')
            articles[idx].pars += articles[idx+1].pars
            toRemove.append(articles[idx+1].id)
            del articles[idx+1]
    """
        # if bbox1 is shorter than bbox2
        # if articles[idx].bbox[2] < articles[idx+1].bbox[2]:
        #    articles[idx].pars += articles[idx+1].pars
        #    toRemove.append(articles[idx+1].id)

    #for article in articles:
    #    if article.id in toRemove:
    #        articles.remove(article)

    return articles


def createMarkdown(articles):
    f = open("out/out.md", 'w')
    for article in articles:
        f.write("\n\n___\n\n")
        for par in article.pars:
            for line in par.lines:
                f.write(" ".join([word.text for word in line.words]) + "\\\n")
            f.write("\n")


def help():
    print("""
Page segmentation modes:
      0    Orientation and script detection (OSD) only.
      1    Automatic page segmentation with OSD.
      2    Automatic page segmentation, but no OSD, or OCR. (not implemented)
      3    Fully automatic page segmentation, but no OSD. (Default)
      4    Assume a single column of text of variable sizes.
      5    Assume a single uniform block of vertically aligned text.
      6    Assume a single uniform block of text.
      7    Treat the sourceImage as a single text line.
      8    Treat the sourceImage as a single word.
      9    Treat the sourceImage as a single word in a circle.
     10    Treat the sourceImage as a single character.
     11    Sparse text. Find as much text as possible in no particular order.
     12    Sparse text with OSD.
     13    Raw line. Treat the sourceImage as a single text line,
           bypassing hacks that are Tesseract-specific.

Other Features:
    c      Draw Careas limits and show sourceImage
    l      Draw Lines limits and show sourceImage
    i      Draw Images limits and show sourceImage
    a      Draw Articles limits and show sourceImage
    e      Extract Images into out/

Usage: python3 main.py relativePathToSourceImage relativePathToOutputFile PSM otherFeatures
Example: python3 main.py assets/assistenteAoEmigrante_0.png out/aoe0.hocr 3 cie\n""")


def main():
    # Print help menu
    if len(sys.argv) == 1 or "help" in sys.argv:
        help()
        quit()

    if len(sys.argv) >= 4:
        # Open sourceImage from argv[1]
        sourceImage = PIL.Image.open(sys.argv[1])

        # Create HOCR output in argv[2]
        hocr = pytesseract.image_to_pdf_or_hocr(sourceImage,
                                                config='--psm ' + sys.argv[3],
                                                lang="por", extension='hocr')
        with open(sys.argv[2], 'w+b') as f:
            f.write(hocr)

        page1 = parseHocr()

    articles = copy.deepcopy(page1.careas)
    # articles = organizeArticles(articles)
    createMarkdown(articles)

    if len(sys.argv) == 5:
        if "c" in sys.argv[4]:
            drawCareaBoxes(sourceImage, page1)
        if "p" in sys.argv[4]:
            drawParBoxes(sourceImage, page1)
        if "l" in sys.argv[4]:
            drawLinesBoxes(sourceImage, page1)
        if "i" in sys.argv[4]:
            drawImageBoxes(sourceImage, page1)
        if "a" in sys.argv[4]:
            drawArticlesBoxes(sourceImage, articles)
        if "e" in sys.argv[4]:
            extractImages(sourceImage, page1)

        sourceImage.show()


if __name__ == "__main__":
    main()

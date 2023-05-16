# HOCRtoMd

# Help
## Page segmentation modes:
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

## Other Features:
    c      Draw Careas limits and show sourceImage
    l      Draw Lines limits and show sourceImage
    i      Draw Images limits and show sourceImage
    a      Draw Articles limits and show sourceImage
    e      Extract Images into out/

Help: python3 main.py help\
Usage: python3 main.py relativePathToSourceImage relativePathToOutputFile PSM otherFeatures\
Example: python3 main.py assets/assistenteAoEmigrante_0.png out/aoe0.hocr 3 cie\


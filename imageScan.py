try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'/workspace/pytesseract'

x = pytesseract.image_to_string((Image.open('tst.png')), lang="eng")
print(x)
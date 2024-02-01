import easyocr

class ImgtoStr:
    def __init__(self, reader):
        self.reader = reader
    def get_string(self,img):
        # reader = easyocr.Reader(['ch_tra'], gpu = True)
        result = self.reader.readtext(img, detail = 0)
        return result
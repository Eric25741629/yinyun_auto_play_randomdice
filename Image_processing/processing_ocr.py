import easyocr
import cv2
import uiautomator2 as u2
import numpy as np
from PIL import Image
from typing import Union
class processing_img:
    def __init__(self,reader:easyocr.Reader,d:u2.Device) -> None:
        self.reader = reader
        self.d = d
    def get_screenshot(self, format='opencv') -> Union[np.ndarray, Image.Image]:
        img = None
        while img is None:
            img = self.d.screenshot(format=format)
        if format == 'opencv':
            img = np.array(img)
        return img # type: ignore
    def get_str(self, x1: int, x2: int, y1: int, y2: int) -> list:
        img = self.get_screenshot()
        img = img[y1:y2, x1:x2] # 裁切圖片 # type: ignore
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        result = self.reader.readtext(img, detail=0)
        if result:
            return result
        else:
            return []
    def check_result(self, x1:int, y1: int, x2: int, y2:int, result:list=[]):
        img_result = self.get_str(x1, y1, x2, y2)
        if not result and img_result:
            return True
        else:
            for item in result:
                if item in img_result:
                    return True
        return False
    def crop_image(self, img, top, bottom, left, right):
        return img[top:bottom, left:right]

import win32gui
import subprocess
import numpy as np
from Fast_Screenshot import fast_screenshot
from PIL import Image
import cv2
from Tools.adb_tool import get_screen_size

import uiautomator2 as u2



class img_tools(fast_screenshot.Fast_Screenshot):

    def __init__(self, handle, devices_ip,device:u2.Device):
        super().__init__(handle)
        self.devices_ip = devices_ip
        self.device_width, self.device_height = get_screen_size(devices_ip)
        self.device = device
        # 開啟一個新的線程，用來更新畫面

    def get_screenshot(self, format='opencv',type='adb'):
        if type == 'adb':
            return self.device.screenshot(format=format)
        # img = self.device.screenshot(format=format)
        # return img
        img = self.screenshot()
        # 縮放至螢幕大小
        img = img.resize((int(self.device_width), int(
            self.device_height)), Image.Resampling.LANCZOS)

        if format == 'opencv':
            return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

        elif format == 'pillow':
            return img

    def crop_image(self, img, x1, y1, x2, y2):
        return img[y1:y2, x1:x2]

    def find_small_image_in_large_image(self, large_image, small_image, threshold, img_result=False):
        '''在大图中找小图
        :param large_image: 大图
        :param small_image: 小图
        :param threshold: 阈值
        :param img_result: 是否返回图像
        :return: 是否找到，坐标或者图像
        '''
        small_image = cv2.cvtColor(np.array(small_image), cv2.COLOR_BGR2GRAY)
        large_image = cv2.cvtColor(np.array(large_image), cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(
            large_image, small_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > threshold:
            small_image_w, small_image_h = small_image.shape[::-1]
            top_left = max_loc
            bottom_right = (top_left[0] + small_image_w,
                            top_left[1] + small_image_h)

            if img_result:
                cv2.rectangle(large_image, top_left,
                              bottom_right, (0, 0, 255), 2)
                return True, (top_left, bottom_right, large_image)
            else:
                return True, (top_left, bottom_right)
        else:
            if img_result:
                return False, (None, None, large_image)
            else:
                return False, (None, None)

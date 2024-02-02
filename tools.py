import random
import numpy as np
from PIL import Image
import cv2
import time
from Tools.Img_tool import img_tools
from Tools.adb_tool import get_screen_size
import uiautomator2 as u2
class devices_info:
    def __init__(self, handle, devices_ip):
        self.devices_ip = devices_ip
        self.device_width, self.device_height = get_screen_size(devices_ip)
        self.handle = handle


class str_tool():
    def __init__(self, img_tool: img_tools, reader):
        self.img_tool = img_tool
        self.reader = reader
    def get_text(self, x1=None, x2=None, y1=None, y2=None) -> list:
        img = self.img_tool.get_screenshot()

        if x1 is not None and x2 is not None and y1 is not None and y2 is not None:
            img = img[y1:y2, x1:x2]

        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        result = self.reader.readtext(img, detail=0 if x1 is None else 1)
        print(result)
        return result if result else []


class click_tool():
    def __init__(self, d:u2.Device,reader, img_tool: img_tools):
        self.img_tool = img_tool
        self.width = self.img_tool.device_width
        self.height = self.img_tool.device_height
        self.d = d
        self.reader = reader
    def click_str(self, str1):
        img = self.img_tool.get_screenshot()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = self.reader.readtext(img)
        for i in result:
            print(i[1])
            if str1 in i[1]:
                print(i[0][0][0], i[0][0][1], i[0][2][0], i[0][2][1])
                try:
                    self.d.click(random.randint(int(i[0][0][0]), int(i[0][2][0])), random.randint(
                        int(i[0][0][1]), int(i[0][2][1])))
                except Exception as e:
                    print(e)

    def click_position(self, x, y):
        self.d.click(x/self.width, y/self.height)

    def close(self):
        img2 = cv2.imread('x.jpg')
        img1 = self.img_tool.get_screenshot()
        get, pos = self.img_tool.find_small_image_in_large_image(
            img1, img2, 0.8, True)
        if get:
            print(pos[0], pos[1])
            random_x = random.randint(pos[0][0], pos[1][0])
            random_y = random.randint(pos[0][1], pos[1][1])
            print(random_x, random_y)
            self.click_position(random_x, random_y)
            time.sleep(1)
        else:
            print('找不到')


# class watch_ad_to_openroom_tool(click_tool, str_tool, img_tools):
#     def __init__(self, d, reader):
#         super().__init__(d, reader)

#     def watch_ad_to_openroom(self):
#         '''NOW CAN'T USE'''
#         count = 1
#         while (1):
#             img = self.d.screenshot(format='opencv')
#             self.d.click(500, 706)
#             time.sleep(0.5)
#             text = reader.readtext(img, detail=0)
#             print(text)
#             if ('通知' in text and '正在載入廣告' in text and '請稍後重試' in text and '確認' in text):
#                 self.d.click(265, 592)
#                 count += 1
#             if (count > 3):
#                 print('商店補充失敗')
#                 self.d.app_stop("com.percent.royaldice")
#                 time.sleep(0.5)
#                 self.d.app_start("com.percent.royaldice",
#                                  use_monkey=True, stop=True)
#                 self.opengame()
#                 break
#             self.AD.watchvideo()
#             time.sleep(2)
#             if (Store_Refresh.Shop(self.d, self.reader).checkinshop()):
#                 print('商店補充成功')
#                 break
#             else:
#                 print('商店補充失敗')
#                 self.d.app_stop("com.percent.royaldice")
#                 time.sleep(0.5)
#                 self.d.app_start("com.percent.royaldice",
#                                  use_monkey=True, stop=True)
#                 self.opengame()
#                 break


# class upadta_game_tool(click_tool, str_tool, img_tool):
#     def __init__(self, d, reader):
#         super().__init__(d, reader)

#     def updata_game(self):
#         self.d.click(368, 590)
#         t = time.time()
#         while time.time() - t < 30:
#             # type: ignore
#             if self.d.xpath('//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[2]').exists:
#                 self.d.xpath(
#                     '//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[2]').click()
#                 break
#         while not self.d.xpath('//*[@content-desc="開始玩"]'):
#             print('start')
#         self.d.xpath('//*[@content-desc="開始玩"]').click()

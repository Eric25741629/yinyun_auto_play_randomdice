import random
import numpy as np
from PIL import Image
import cv2
import time


class img_tool:
    def __init__(self, d, reader):
        self.d = d
        self.reader = reader

    def get_screenshot(self, format='opencv') -> np.ndarray or Image.Image:
        img = None
        while img is None:
            img = self.d.screenshot(format=format)
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


class str_tool(img_tool):
    def __init__(self, d, reader):
        super().__init__(d, reader)

    def get_text(self, x1=None, x2=None, y1=None, y2=None) -> list:
        img = self.get_screenshot()

        if x1 is not None and x2 is not None and y1 is not None and y2 is not None:
            img = img[y1:y2, x1:x2]

        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        result = self.reader.readtext(img, detail=0 if x1 is None else 1)
        print(result)
        return result if result else []


class click_tool(img_tool):
    def __init__(self, d, reader, height=1280, width=720):
        super().__init__(d, reader)
        self.width = width
        self.height = height

    def click_str(self, str1):
        img = self.get_screenshot()
        result = self.reader.readtext(img)
        for i in result:
            if str1 in i[1]:
                self.d.click(random.randint(int(i[0][0][0]), int(i[0][2][0])), random.randint(
                    int(i[0][0][1]), int(i[0][2][1])))

    def click_position(self, x, y):
        self.d.click(x/self.width, y/self.height)

    def close(self):
        img2 = cv2.imread('x.jpg')
        img1 = self.get_screenshot()
        get, pos = self.find_small_image_in_large_image(
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


class watch_ad_to_openroom_tool(click_tool, str_tool, img_tool):
    def __init__(self, d, reader):
        super().__init__(d, reader)

    def watch_ad_to_openroom(self):
        '''NOW CAN'T USE'''
        count = 1
        while (1):
            img = self.d.screenshot(format='opencv')
            self.d.click(500, 706)
            time.sleep(0.5)
            text = reader.readtext(img, detail=0)
            print(text)
            if ('通知' in text and '正在載入廣告' in text and '請稍後重試' in text and '確認' in text):
                self.d.click(265, 592)
                count += 1
            if (count > 3):
                print('商店補充失敗')
                self.d.app_stop("com.percent.royaldice")
                time.sleep(0.5)
                self.d.app_start("com.percent.royaldice",
                                 use_monkey=True, stop=True)
                self.opengame()
                break
            self.AD.watchvideo()
            time.sleep(2)
            if (Store_Refresh.Shop(self.d, self.reader).checkinshop()):
                print('商店補充成功')
                break
            else:
                print('商店補充失敗')
                self.d.app_stop("com.percent.royaldice")
                time.sleep(0.5)
                self.d.app_start("com.percent.royaldice",
                                 use_monkey=True, stop=True)
                self.opengame()
                break


class upadta_game_tool(click_tool, str_tool, img_tool):
    def __init__(self, d, reader):
        super().__init__(d, reader)

    def updata_game(self):
        self.d.click(368, 590)
        t = time.time()
        while time.time() - t < 30:
            # type: ignore
            if self.d.xpath('//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[2]').exists:
                self.d.xpath(
                    '//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[2]').click()
                break
        while not self.d.xpath('//*[@content-desc="開始玩"]'):
            print('start')
        self.d.xpath('//*[@content-desc="開始玩"]').click()

from multiprocessing import Process, Queue
import random
import threading
import time
import cv2
import numpy as np
import uiautomator2 as u2
from adbutils import adb
import math
from model import Classifier, models
from pic_tranform import *
from torch import nn
from view import gameview
import tools


def calculate_random_arc_coordinates(center, radius, start_point, end_point, randomness):
    # 計算起始點和結束點之間的角度
    start_angle = math.atan2(
        start_point[1] - center[1], start_point[0] - center[0])
    end_angle = math.atan2(end_point[1] - center[1], end_point[0] - center[0])

    # 將角度轉換為0到2π的範圍
    start_angle = start_angle % (2 * math.pi)
    end_angle = end_angle % (2 * math.pi)

    # 計算起始角度到結束角度之間的角度差
    angle_diff = end_angle - start_angle

    # 確保角度差為正值
    if angle_diff <= 0:
        angle_diff += 2 * math.pi

    # 分割角度差並計算對應的弧形座標
    num_points = 100  # 弧形上的點數量
    angle_increment = angle_diff / (num_points - 1)
    arc_coordinates = []

    for i in range(num_points):
        angle = start_angle + i * angle_increment

        # 引入隨機性
        angle += random.uniform(-randomness, randomness)

        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        arc_coordinates.append((x, y))


global image_num, time_num
image_num = 200
time_num = time.time()


class play():
    def __init__(self, devices, dicemodel, reader, q: Queue, player, img_tool: tools.img_tool, str_tool: tools.str_tool, click_tool: tools.click_tool, wavemodel, model='cooperation'):
        self.d = devices
        self.reader = reader
        self.player = player
        self.playmode = model
        self.model = dicemodel
        self.q = q
        self.wave = 0
        self.wave_model = wavemodel
        # 一個3*5*2的矩陣
        self.place = np.full((3, 5, 2), -1)
        self.gameview = gameview(
            self.d, self.reader, img_tool=str_tool, str_tool=str_tool, click_tool=click_tool)
        self.wavename = ['wave', '1', '2', '3',
                         '4', '5', '6', '7', '8', '9', '0']

    def get_wave(self):
        try:
            img = self.gameview.img_tool.get_screenshot()
            img = img[15:50, 120:250]
            global image_num, time_num
            if (time.time()-time_num > 10):
                while (os.path.isfile(r"C:\python_project\yinyun_auto_play_randomdice\dice_img/{}.jpg".format(image_num))):
                    image_num += 1
                cv2.imwrite(
                    r"C:\python_project\yinyun_auto_play_randomdice\dice_img/{}.jpg".format(image_num), img)
                time_num = time.time()
            results = self.wave_model(img, classes=[
                                      1, 2, 3, 4, 5, 6, 7, 8, 9, 10], half=True, verbose=False)  # 返回 Results 对象列表
            sorted_indices = torch.argsort(results[0].boxes.data[:, 0])
            value = 0
            for sorted_index in sorted_indices:
                value = value * 10 + \
                    (int(results[0].boxes.cls[sorted_index].item()) % 10)
            return value
        except Exception as e:
            print(e)
            print('get_wave error Use old method')

            for i in range(0, 3):
                img = self.gameview.img_tool.get_screenshot()
                img = img[15:50, 120:250]
                # global image_num, time_num
                # if (time.time()-time_num > 10):
                #     while (os.path.isfile(r"C:\python_project\yinyun_auto_play_randomdice\dice_img/{}.jpg".format(image_num))):
                #         image_num += 1
                #     cv2.imwrite(
                #         r"C:\python_project\yinyun_auto_play_randomdice\dice_img/{}.jpg".format(image_num), img)
                #     time_num = time.time()
                ret, binary = cv2.threshold(
                    img, 127, 255, cv2.THRESH_BINARY)  # 二值化
                result = self.reader.readtext(binary)
                # print(result)
                if (result != []):
                    numbers = "".join([x for x in result[0][1] if x.isdigit()])
                    if numbers:
                        return int(numbers)
            return 0

    def get_place(self, who=None, path=None):
        # time.sleep(0.2)
        if who == 'test' and path is not None:
            img = Image.open(path)
        else:
            img = self.gameview.img_tool.get_screenshot('pillow')

        images = []  # 存儲待預測的圖像
        indices = []  # 存儲圖像的索引，以便在預測後進行結果的保存
        start_time = time.time()
        for i in range(0, 3):
            for j in range(0, 5):
                pointx = int(j * 62.7 + 144)
                pointy = i * 60 + 512
                img2 = img.crop((pointx - 30, pointy - 32,
                                pointx + 32, pointy + 30))
                # img2 = img2.convert('RGB')
                images.append(img2)
                indices.append((i, j))

        # 進行預測
        predictions = detect_dice(images, self.player, self.model)

        # 將預測結果保存到 self.place 中
        for pred, index in zip(predictions, indices):
            i, j = index
            self.place[i][j][0] = pred[0]  # 骰子類型
            self.place[i][j][1] = pred[1]  # 骰子數目
        endtime = time.time()
        print('get_place time:', endtime-start_time)

    def printboardtype(self):
        for i in range(0, 3):
            for j in range(0, 5):
                print(self.place[i][j][0], end=' ')
            print()

    def printboardnum(self):
        for i in range(0, 3):
            for j in range(0, 5):
                print(self.place[i][j][1], end=' ')
            print()

    def call_dice(self):
        for _ in range(random.randint(5, 10)):
            try:
                img = self.gameview.img_tool.get_screenshot()
                crop_img = img[750:830, 230:310]
                b, g, r = crop_img[50, 50]
                if 245 <= b <= 255 and 245 <= g <= 255 and 245 <= r <= 255:
                    x = 270 + random.randint(-5, 5)
                    y = 790 + random.randint(-5, 5)
                    self.d.click(x, y)
                else:
                    break
            except:
                x = 270 + random.randint(-5, 5)
                y = 790 + random.randint(-5, 5)
                self.d.click(x, y)

    def level_up(self, dices):
        times = 0
        while (1):
            level_list = []
            img = self.gameview.img_tool.get_screenshot()
            for i in dices:
                crop_img = img[900:945, 50+i*100:130+i*100]
                result = self.reader.readtext(crop_img)
                print(result)
                if (result != []):
                    level_list.append(i)
            if (level_list == []):
                times = times+1
                if (times > 2):
                    break
            for i in level_list:
                for _ in range(0, random.randint(3, 4)):
                    self.d.click(80+i*100+int(random.random()*10), 900)
                # d.click(80+i*100+int(random.random()*10), 900)
            time.sleep(2)

    # def click_dice_multiple_times(self, index):
    #     random_offset = random.randint(-5, 5)
    #     for _ in range(5, 9):
    #         click_x = 80 + index * 100 + random_offset
    #         self.d.click(click_x, 900)

    # 其他輔助函數

    def _check_dice(self, img, dice):
        crop_img = img[900:945, 50 + dice * 100:130 + dice * 100]
        result = self.reader.readtext(crop_img)
        print(result)  # 調試輸出
        return bool(result)

    def end_game(self):
        try:
            img = self.gameview.img_tool.get_screenshot()
            img = self.crop_image(img, 850, 890, 240, 320)
            result = self.reader.readtext(img)
            if result:
                for text in result:
                    if text[1] == '確認':
                        for _ in range(3):
                            self.d.click(270, 870)
                            time.sleep(2)
                        return True
            return False
        except:
            return False

    def crop_image(self, img, top, bottom, left, right):
        return img[top:bottom, left:right]

    def move_dice(self, row, column, target_x, target_y, touch_time):
        try:
            r = random.randint(25, 35)
            self.d.swipe(column * 62 + 120 + r, row * 60 + 480 + r,
                         target_y * 62 + 120 + r, target_x * 60 + 480 + r, touch_time)
        except Exception as e:
            print(e)
        # # Simulate pressing the dice

        # # Calculate touch time based on distance between current position and target position
        # touch_time = math.sqrt(
        #     (row - target_x) ** 2 + (column - target_y) ** 2)

        # # Add some randomness to the start and end positions
        # start_x = column * 62 + 120 + random.randint(25, 35)
        # start_y = row * 60 + 480 + random.randint(25, 35)
        # end_x = int(target_x) * 62 + 480 + random.randint(25, 35)
        # end_y = int(target_y) * 60 + 120 + random.randint(25, 35)

        # # Calculate arc coordinates with randomness
        # center = ((start_x + end_x) / 2, (start_y + end_y) / 2)
        # radius = math.sqrt((start_x - end_x) ** 2 +
        #                    (start_y - end_y) ** 2) / 2
        # start_point = (start_x, start_y)
        # end_point = (end_x, end_y)
        # randomness = 20  # Adjust the randomness value as needed

        # arc_coords = calculate_random_arc_coordinates(
        #     center, radius, start_point, end_point, randomness)

        # # Simulate the swipe action by following the arc coordinates
        # self.d.swipe_points(arc_coords, touch_time*0.05)

    def mergydice(self, use_type: int, use_num: int, target_type: int, target_num: int, use_all: bool, remove: bool, cache: list):
        use = np.where((self.place[:, :, 0] == use_type) & (
            self.place[:, :, 1] == use_num))
        use = np.transpose(use).tolist()
        target = np.where((self.place[:, :, 0] == target_type) & (
            self.place[:, :, 1] == target_num))
        target = np.transpose(target).tolist()

        if not use or not target:
            return 0

        if not cache:
            if use_all:
                self.move_all_dices(use, target, remove,
                                    use_type, use_num, target_type, target_num)
            else:
                self.move_single_dice(
                    use, target, remove, use_type, use_num, target_type, target_num)
        time.sleep(0.2)
        self.get_place()

    def move_all_dices(self, starting_point, target, remove, use_type, use_num, target_type, target_num):
        used = [0] * len(starting_point)
        use_target = [0] * len(target)
        random.shuffle(starting_point)
        for i in range(len(starting_point)):
            if use_target.count(1) == len(target) or used.count(1) == len(starting_point):
                # 如果目標全部用完或起始全部用完，就返回
                return

            if used[i] == 1:
                # 如果起始已經用過，就跳過
                continue

            for j in range(len(target)):
                if use_target[j] == 1 or target[j] == starting_point[i]:
                    # 如果目標已經用過，或者目標和起始相同，就跳過
                    continue

                if remove:
                    use_target[j] = 1

                if target[j] in starting_point and remove:
                    used[starting_point.index(target[j])] = 1

                if starting_point[i] in target and remove:
                    use_target[target.index(starting_point[i])] = 1
                print(starting_point[i], target[j])
                self.move_dice(
                    starting_point[i][0], starting_point[i][1], target[j][0], target[j][1], 0.05)
                time.sleep(0.1+random.random()*0.1)
                break

            if remove:
                used[i] = 1

    def move_single_dice(self, use, target, remove, use_type, use_num, target_type, target_num):
        chosen = random.choice(range(len(target)))
        selected = target.pop(chosen)
        self.move_dice(use[0][0], use[0][1], selected[0], selected[1], 0.05)
    dicelist = ['growning', 'yinyun', 'jocker', 'sup', 'broke_growning', ]

    def yinyun_attack(self):
        game_end = False
        know = 0
        while (not game_end):
            if self.wave - self.get_wave() < 10:
                self.wave = max(self.wave, self.get_wave())
            print('關卡:', int(self.wave))
            if (self.wave >= 20 and know == 0):
                self.q.put("暗殺")
                know = 1
            self.call_dice()
            self.get_place()
            for i in range(1, 2):
                self.mergydice(2, i, 0, i, True, False, [])  # 小丑複製成長
            for i in range(1, 8):
                self.mergydice(2, i, 1, i, True, False, [])  # 小丑複製陰陽
            for i in range(1, 8):
                self.mergydice(3, i, 1, i, True, True, [])  # 營養餵給陰陽

            yinyun_num = len(np.where(self.place[:, :, 0] == 1)[0])
            print(yinyun_num)
            if (yinyun_num == 15):
                self.q.put("暗殺")
                return 1
            game_end = self.end_game()
            if (game_end):
                self.q.put("end_game")
                return 0

    def sup_yinyun(self, wave):
        game_end = False
        chcektime = time.time()
        while (not game_end):
            if (chcektime-time.time() > 10):
                chcektime = time.time()
                # img = self.gameview.img_tool.get_screenshot()
                if (self.gameview.choose_game() == 'main'):
                    return 0
            if self.wave - self.get_wave() < 10:
                self.wave = max(self.wave, self.get_wave())
            print('關卡:', int(self.wave))
            if (self.wave < 20 or self.wave > 25):
                self.call_dice()
            if (self.wave >= wave):
                return 1
            self.get_place()
            for i in range(1, 8):
                self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
            for i in range(1, 8):
                self.mergydice(1, i, 2, i, True, False, [])  # 小丑複製暗殺
            for i in range(1, 8):
                self.mergydice(2, i, 0, i, True, True, [])  # 暗殺合成適應
            for i in range(1, 8):
                self.mergydice(2, i, 2, i, True, True, [])  # 暗殺合成暗殺
            for i in range(1, 8):
                self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
            for i in range(1, 8):
                self.mergydice(3, i, 0, i, True, True, [])  # 招喚合成適應
            for i in range(1, 8):
                know = np.where((self.place[:, :, 0] == 2) & (
                    self.place[:, :, 1] == i))
                if (len(know[0]) > 0):
                    continue
                know = np.where((self.place[:, :, 0] == 0) & (
                    self.place[:, :, 1] == i))
                if (len(know[0]) > 0):
                    continue
                know = np.where((self.place[:, :, 0] == 3) & (
                    self.place[:, :, 1] == i))
                if (len(know[0]) % 2 == 0):
                    continue
                self.mergydice(1, i, 3, i, False, False, [])  # 小丑複製招喚
            game_end = self.end_game()
            if (game_end):
                self.q.put("end_game")
                return 0

    def bubble_sup(self):
        game_end = False
        chcektime = time.time()
        while (not game_end):
            if (chcektime-time.time() > 10):
                chcektime = time.time()
                if (self.gameview.choose_game() == 'main'):
                    return 0
            if self.wave - self.get_wave() < 10:
                self.wave = max(self.wave, self.get_wave())
            print('關卡:', int(self.wave))
            self.call_dice()
            self.get_place()
            self.printboardtype()
            self.printboardnum()
            print('招喚合成招喚')
            for i in range(1, 8):
                self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
            for i in range(1, 8):
                self.mergydice(0, i, 3, i, True, False, [])  # 小丑複製暗殺
            print('小丑複製泡泡')
            for i in range(1, 8):
                self.mergydice(1, i, 4, i, True, False, [])  # 小丑複製泡泡
            print('小丑複製招喚')
            for i in range(1, 8):
                self.mergydice(1, i, 3, i, True, False, [])  # 小丑複製招喚
            print('招喚合成招喚')
            for i in range(1, 8):
                self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
            print('小丑複製泡泡')
            for i in range(1, 8):
                self.mergydice(1, i, 4, i, True, True, [])  # 小丑複製泡泡
            print('泡泡合成適應')
            for i in range(1, 8):
                self.mergydice(4, i, 0, i, True, True, [])  # 泡泡合成適應
            print('泡泡合成泡泡')
            for i in range(1, 8):
                self.mergydice(4, i, 4, i, True, True, [])  # 泡泡合成泡泡
            game_end = self.end_game()
            if (game_end):
                return 0


error = 0
dicenames = ['mimic', 'jocker', 'assassin', 'summon', 'bubble']

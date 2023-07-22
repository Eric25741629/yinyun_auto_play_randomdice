import ctypes
import os
from multiprocessing import Process, Queue
import random
import threading
import time
import cv2
import easyocr
import numpy as np
import torch
import uiautomator2 as u2
from adbutils import adb
import math
import Store_Refresh
import watchAd
from model import models
from pic_tranform import *
from Image_processing import processing_ocr
from torch import nn
from typing import Union
from Image_processing import Game_Ctrl as ctrl_game
from PIL import Image

from Image_processing import game_view

# 遊玩前置作業
from tools import tool

dicetype_num_model = models.mobilenet_v3_large(pretrained=True)
num_classes = 64
dicetype_num_model.classifier[-1] = nn.Linear(
    in_features=dicetype_num_model.classifier[-1].in_features, out_features=num_classes)
dicetype_num_model.load_state_dict(torch.load(r'V3model_epoch_8.pth'))
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
dicetype_num_model.eval().to(device)

reader = easyocr.Reader(['ch_tra'], gpu=True)


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


class play(game_view.gameview):
    def __init__(self, d: u2.Device,dicetype_num_model, reader: easyocr.Reader, q: Queue, player='att'):
        super().__init__(d, reader)
        self.player = player
        self.model = dicetype_num_model
        self.q = q
        self.wave = 0
        # 一個3*5*2的矩陣
        self.place = np.full((3, 5, 2), -1)

    def get_wave(self):
        for i in range(0, 3):
            img = self.get_screenshot()
            img = img[15:50, 120:250]
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
            img = self.get_screenshot('pillow')

        images = []  # 存储待预测的图像
        indices = []  # 存储图像的索引，以便在预测后进行结果的保存
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

        # 进行预测
        predictions = detect_dice(images, self.player, self.model)

        # 将预测结果保存到 self.place 中
        for pred, index in zip(predictions, indices):
            i, j = index
            self.place[i][j][0] = pred[0]  # 骰子类型
            self.place[i][j][1] = pred[1]  # 骰子数目
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
                img = self.get_screenshot()
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
            img = self.get_screenshot()
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
                #d.click(80+i*100+int(random.random()*10), 900)
            time.sleep(2)

    # def click_dice_multiple_times(self, index):
    #     random_offset = random.randint(-5, 5)
    #     for _ in range(5, 9):
    #         click_x = 80 + index * 100 + random_offset
    #         self.d.click(click_x, 900)

    # 其他辅助函数

    def _check_dice(self, img, dice):
        crop_img = img[900:945, 50 + dice * 100:130 + dice * 100]
        result = self.reader.readtext(crop_img)
        print(result)  # 调试输出
        return bool(result)

    def end_game(self):
        if self.check_result(850, 890, 240, 320, ['確認']):
            return True
        return False

    def move_dice(self, row, column, target_x, target_y, touch_time):
        try:
            # Simulate pressing the dice

            # Calculate touch time based on distance between current position and target position
            touch_time = math.sqrt(
                (row - target_x) ** 2 + (column - target_y) ** 2)

            # Add some randomness to the start and end positions
            start_x = column * 62 + 120 + random.randint(25, 35)
            start_y = row * 60 + 480 + random.randint(25, 35)
            end_x = int(target_x) * 62 + 480 + random.randint(25, 35)
            end_y = int(target_y) * 60 + 120 + random.randint(25, 35)

            # Calculate arc coordinates with randomness
            center = ((start_x + end_x) / 2, (start_y + end_y) / 2)
            radius = math.sqrt((start_x - end_x) ** 2 +
                               (start_y - end_y) ** 2) / 2
            start_point = (start_x, start_y)
            end_point = (end_x, end_y)
            randomness = 20  # Adjust the randomness value as needed

            arc_coords = calculate_random_arc_coordinates(
                center, radius, start_point, end_point, randomness)

            # Simulate the swipe action by following the arc coordinates
            self.d.swipe_points(arc_coords, touch_time*0.05)
        except Exception as err:
            print(err)
            pass

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
                # 如果目标全部用完或起始全部用完，就返回
                return

            if used[i] == 1:
                # 如果起始已经用过，就跳过
                continue

            for j in range(len(target)):
                if use_target[j] == 1 or target[j] == starting_point[i]:
                    # 如果目标已经用过，或者目标和起始相同，就跳过
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

    def check_exist_dice(self, dicetype, dicenum):
        know = np.where((self.place[:, :, 0] == dicetype) & (
            self.place[:, :, 1] == dicenum))
        if (len(know[0]) == 0):
            return False
        else:
            return True

    def yinyun_attack(self):
        game_end = False
        know = 0
        while (not game_end):
            self.wave = max(self.wave, self.get_wave())
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
                if (self.choose_game() == 'main'):
                    return 0
            self.wave = max(self.wave, self.get_wave())
            if (self.wave < 20 or self.wave > 25):
                self.call_dice()
            if (self.wave >= wave):
                return 0
            self.get_place()
            for i in range(1, 8):
                self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
            for i in range(1, 8):
                self.mergydice(1, i, 2, i, True, False, [])  # 小丑複製暗殺
            for i in range(1, 8):
                if (self.check_exist_dice(1, i)):
                    continue
                self.mergydice(2, i, 0, i, True, True, [])  # 暗殺合成適應
            for i in range(1, 8):
                if (self.check_exist_dice(1, i)):  # 如果有小丑就跳過
                    continue
                self.mergydice(2, i, 2, i, True, True, [])  # 暗殺合成暗殺
            for i in range(1, 8):
                self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
            for i in range(1, 8):
                self.mergydice(3, i, 0, i, True, True, [])  # 招喚合成適應
            for i in range(1, 8):
                if (self.check_exist_dice(2, i) or self.check_exist_dice(0, i)):
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
                if (self.choose_game() == 'main'):
                    return 0
            self.wave = max(self.wave, self.get_wave())
            print('關卡:', int(self.wave))
            self.call_dice()
            self.get_place()
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


def dicer_att(d: u2.Device, q: Queue):
    attctrl = ctrl_game.ctrl_game(d, reader, q)
    attctrl.switch_what_to_do()
    attctrl.begin_button()
    attctrl.click_position(250,700)
    q.put('start')
    start = time.time()
    attack_game_ctrl = play(d,dicetype_num_model, reader, q, player='att')
    while(not attctrl.check_ingame()  ):
        time.sleep(1)
        if (time.time()-start > 30):
            print('超過30秒')
            q.put('end_game')
            d.app_stop('com.percent.royaldice')
            return 0
        if not q.empty():
            start = q.get()
            d.app_stop('com.percent.royaldice')
            return 0
    check = attack_game_ctrl.yinyun_attack()
    if (check != 0):
        attack_game_ctrl.level_up([0])
    while (not attack_game_ctrl.end_game()):
        if (attack_game_ctrl.choose_game() == "main"):
            return
        time.sleep(5)


def dicer_sup(d: u2.Device, q: Queue, devices_ip: str):

    supctrl = ctrl_game.ctrl_game(d, reader, q, act='sup', devices_ip=devices_ip)
    supctrl.switch_what_to_do()
    start = q.get()
    if (start == 'start'):
        start = time.time()
        sup_game_ctrl = play(d,dicetype_num_model, reader, q, player='att')
        while(not supctrl.check_ingame()):
            time.sleep(1)
            if (time.time()-start > 35):
                print('超過35秒')
                q.put('end_game')
                d.app_stop('com.percent.royaldice')
                return 0
            if not q.empty():
                start = q.get()
                d.app_stop('com.percent.royaldice')
                return 0
        while(q.empty() and not sup_game_ctrl.end_game()):
            sup_game_ctrl.call_dice()
        q.get()    
        check = sup_game_ctrl.sup_yinyun(62)
        if (check == 0):
            sup_game_ctrl.level_up([4])
            sup_game_ctrl.bubble_sup()


    # num=q.put(1)
global image_num
image_num = 0

def sct(d):
    # time.sleep(10)
    # while(1):
    global image_num
    image = d.screenshot(format='opencv')
    # 如果圖片存在的話，image_num就會一直加1 直到圖片不存在
    while (os.path.isfile(r"D:\dice_py\123/{}.jpg".format(image_num))):
        image_num += 1
    cv2.imwrite(r"D:\dice_py\123/{}.jpg".format(image_num), image)
    # time.sleep(1)
    image_num += 1

reader = easyocr.Reader(['ch_tra'], gpu=True)

def reset():
    global count
    count = 0
    time.sleep(21500)
    count = 1


global count
count = 1
if __name__ == '__main__':
    os.system("adb devices")
    devices = ['emulator-5558', 'emulator-5560']
    attact_devices = u2.connect('emulator-5558')
    support_devices = u2.connect('emulator-5560')
    for i in range(30):
        try:
            f = open('D:\record.txt', "a+")
            localtime = time.localtime()
            result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime)
            f.write(result+'\n')
            f.close()
        except:
            f = open(r'D:\recorder.txt', "a+")
            localtime = time.localtime()
            result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime)
            f.write(result+'\n')
            f.close()
        queue = Queue(3)
        tatt = threading.Thread(
            target=dicer_att, args=(attact_devices, queue,))
        tsup = threading.Thread(
            target=dicer_sup, args=(support_devices, queue, devices[1]))

        tatt.start()
        tsup.start()
        try:
            tatt.join(2500)
            tsup.join(2500)
        # 強制終止線程
        except:
            if tsup.is_alive():
                # 如果你確定線程在 join() 方法上阻塞，可以考慮使用下面的代碼來強制終止線程
                tid = tsup.ident
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(tid), ctypes.py_object(SystemExit))
                if res > 1:
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
                    print('無法終止線程')
                else:
                    print('線程已終止')
                    d = u2.connect('emulator-5560')
                    d.app_stop('com.percent.royaldice')
                    d = u2.connect('emulator-5558')
                    d.app_stop('com.percent.royaldice')

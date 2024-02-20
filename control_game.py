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
from Tools.Img_tool import img_tools
import easyocr
import calculate
import load_models


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
    def __init__(self, devices: u2.Device, q: Queue, playermode, img_tool: img_tools, str_tool: tools.str_tool, click_tool: tools.click_tool, ai_model: load_models.AI_model, gamemodel='cooperation'):
        self.d = devices
        self.reader = ai_model.reader
        self.player = playermode
        self.playmode = gamemodel
        self.model = ai_model.dicemodel
        self.q = q
        self.img_tool = img_tool
        self.str_tool = str_tool
        self.click_tool = click_tool
        self.wave = 0
        self.wave_model = ai_model.wavemodel
        # 一個3*5*2的矩陣
        self.place = np.full((3, 5, 2), -1)
        self.gameview = gameview(str_tool=str_tool)
        self.wavename = ['wave', '1', '2', '3',
                         '4', '5', '6', '7', '8', '9', '0']
        if gamemodel == 'cooperation':
            self.OFFSET_Y = 482
            self.OFFSET_X = 144
        else:
            self.OFFSET_Y = 532
            self.OFFSET_X = 144
        self.not_to_save = []

    def get_wave(self):
        try:
            img = self.img_tool.get_screenshot()
            img = img[15:50, 120:250]
            cv2.imshow('wave', img)
            cv2.waitKey(10)
            global image_num, time_num
            if (time.time()-time_num > 10):
                if not os.path.exists('dice_img'):
                    os.mkdir('dice_img')

                while (os.path.isfile(r"dice_img/{}.jpg".format(image_num))):
                    image_num += 1
                cv2.imwrite(
                    r"dice_img/{}.jpg".format(image_num), img)
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
                img = self.img_tool.get_screenshot()
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

    def spilt_dice(self, img=None):
        if img == None:
            img = self.img_tool.get_screenshot('pillow')
        else:
            img = img
        image_list = []
        for i in range(0, 3):
            for j in range(0, 5):
                pointx = int(j * 62.7 + self.OFFSET_X)
                pointy = i * 60 + self.OFFSET_Y+30
                img2 = img.crop((pointx - 30, pointy - 32,
                                pointx + 32, pointy + 30))
                image_list.append(img2)
        return image_list

    def get_place(self, who=None, path=None, record=False):

        img = self.img_tool.get_screenshot('pillow', 'pywin32')
        images = self.spilt_dice(img)
        if self.player != 'sup':
            cv2.imshow('img', cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
            cv2.waitKey(1)
        predictions = detect_dice(images, self.player, self.model)
        # 轉換為NumPy陣列
        numpy_array = np.array(predictions)
        if (self.player == 'att'):
            dicenames1 = ['growning', 'yinyun',
                          'jocker', 'sup', 'broken_growning', ]
        else:
            dicenames1 = ['mimic', 'jocker', 'assassin', 'summon', 'bubble']
        # 將一維陣列轉換為3x5的二維陣列
        reshaped_array = numpy_array.reshape(3, 5, 2)
        # if record:
        #     for i in range(3):
        #         for j in range(5):
        #             # 檢查是否有./record/資料夾
        #             if not os.path.exists('./record3/'):
        #                 os.mkdir('./record3/')
        #             # 保存圖片 創建record資料夾 在record資料夾中創建以dicename+點數命名的資料夾
        #             if not os.path.exists('./record3/{}{}/'.format(dicenames1[reshaped_array[i][j][0]], reshaped_array[i][j][1])):
        #                 os.mkdir(
        #                     './record3/{}{}/'.format(dicenames1[reshaped_array[i][j][0]], reshaped_array[i][j][1]))
        #             if '{}{}'.format(dicenames1[reshaped_array[i][j][0]], reshaped_array[i][j][1]) in self.not_to_save and reshaped_array[i][j][0] == -1:
        #                 continue

        #             # 檢查數量 使用一個陣列保存查找到的數量
        #             if len(os.listdir('./record3/{}{}/'.format(dicenames1[reshaped_array[i][j][0]], reshaped_array[i][j][1]))) > 10000:
        #                 self.not_to_save.append('{}{}'.format(
        #                     dicenames1[reshaped_array[i][j][0]], reshaped_array[i][j][1]))
        #                 continue
        #             # 保存圖片
        #             if reshaped_array[i][j][0] == -1:  # background
        #                 if not os.path.exists('./record3/{}{}'.format('background', 0)):
        #                     os.mkdir('./record3/{}{}'.format('background', 0))
        #                 if '{}{}'.format('background', 0) in self.not_to_save:
        #                     continue
        #                 if len(os.listdir('./record3/{}{}/'.format('background', 0))) > 10000:
        #                     self.not_to_save.append(
        #                         '{}{}'.format('background', 0))
        #                     continue
        #                 images[i*5+j].save('./record3/{}{}/{}.jpg'.format(
        #                     'background', 0, time.time()))
        #             else:
        #                 if len(os.listdir('./record3/{}{}/'.format(dicenames1[reshaped_array[i][j][0]], reshaped_array[i][j][1]))) > 10000:
        #                     continue
        #                 images[i*5+j].save('./record3/{}{}/{}.jpg'.format(
        #                     dicenames1[reshaped_array[i][j][0]], reshaped_array[i][j][1], time.time()))

        self.place = reshaped_array
        # endtime = time.time()
        # print('get_place time:', endtime-start_time)

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
                img = self.img_tool.get_screenshot()
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
            img = self.img_tool.get_screenshot()
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
            img = self.img_tool.get_screenshot()
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
            print(
                f"Move dice from ({row}, {column}) to ({target_x}, {target_y})")
            self.d.swipe(column * 62 + 120 + r, row * 60 + self.OFFSET_Y + r,
                         target_y * 62 + 120 + r, target_x * 60 + self.OFFSET_Y + r, touch_time)
        except Exception as e:
            print('303', e)

    def mergydice(self, use_type: int, use_num: int, target_type: int, target_num: int, use_all: bool, remove: bool, cache: list):
        '''
        remove: 是否移除目標骰子
        '''
        try:
            self.get_place(record=True)
            if not use_all:
                tar_counts = np.where((self.place[:, :, 0] == target_type) & (
                    self.place[:, :, 1] == target_num))
                if (len(tar_counts[0]) % 2 == 0):
                    return 0
            use_result = calculate.find_elements(self.place, use_type,
                                                 use_num)
            if use_type == target_type and use_num == target_num:
                target_result = use_result
            else:
                target_result = calculate.find_elements(self.place, target_type,
                                                        target_num)
            if not use_result or not target_result:
                return 0
            if remove:
                connections = calculate.find_single_connections(
                    use_result, target_result)
            else:
                connections = calculate.find_mult_connections(
                    use_result, target_result)
            if not connections:
                return 0

            print(connections)

            for connection in connections:

                # print(
                #     f"Connect {connection[0]} to {connection[1]} with distance {connection[2]:.2f}")
                # 檢查類型是否為int
                # if not isinstance(connection[0][0], int) or not isinstance(connection[0][1], int) or not isinstance(connection[1][0], int) or not isinstance(connection[1][1], int):
                #     print('不是int')
                #     print(type(connection[0][0]), type(connection[0][1]), type(connection[1][0]), type(connection[1][1]))
                #     # 轉換為int
                move_time = 0.02+random.random()*0.01
                self.move_dice(int(connection[0][0]), int(connection[0][1]),
                               int(connection[1][0]), int(connection[1][1]), move_time)
                if not use_all:
                    tar_counts = np.where((self.place[:, :, 0] == target_type) & (
                        self.place[:, :, 1] == target_num))
                    if (len(tar_counts[0]) % 2 == 1):
                        break
            time.sleep(move_time+0.01)
            # self.get_place()
        except Exception as e:
            print('333', e)

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
    def count_dice_num(self, dice_type: int, dice_num: int):
        return len(np.where((self.place[:, :, 0] == dice_type) & (
            self.place[:, :, 1] == dice_num))[0])

    def find_dice(self, dice_type: int):
        result = np.where((self.place[:, :, 0] == dice_type))
        # 合併兩個array
        return np.vstack((result[0], result[1])).T

    def find_the_same(self, dice_code: int):
        summom_result = self.find_dice(dice_code)
        # print(summom_result)
        if len(summom_result) >= 1:
            print(summom_result)
            for i in summom_result:
                # print(place[i[0], i[1], 1])
                result = self.count_dice_num(
                    dice_code, self.place[i[0], i[1], 1])
                if result >= 2:
                    # print(3, place[i[0], i[1], 1])
                    return [dice_code, self.place[i[0], i[1], 1], dice_code, self.place[i[0], i[1], 1]]

    def find_the_diff(self, dice_code1: int, dice_code2: int):
        result1 = self.find_dice(dice_code1)
        result2 = self.find_dice(dice_code2)
        if not result1.any() or not result2.any():
            return None
        if len(result1) >= 1:
            print(result1)
            for i in result1:
                # print(place[i[0], i[1], 1])
                result = self.count_dice_num(
                    dice_code2, self.place[i[0], i[1], 1])
                if result >= 1:
                    # print(3, place[i[0], i[1], 1])
                    return [dice_code1, self.place[i[0], i[1], 1], dice_code2, self.place[i[0], i[1], 1]]
    def yinyun_attack(self):
        game_end = False
        know = 0
        while (not game_end):
            if abs(self.wave - self.get_wave()) < 10:
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
                self.get_place()

                yinyun_num = len(np.where(self.place[:, :, 0] == 1)[0])
                if yinyun_num == 15:
                    self.q.put("暗殺")
                    return 1
                else:
                    continue
            game_end = self.end_game()
            if (game_end):
                self.q.put("end_game")
                return 0

    def deside_status(self):
        result = self.find_the_same(3)
        if result is not None:
            return result
        result = self.find_the_diff(1, 2)
        if result is not None:
            return result
        result = self.find_the_diff(2, 0)
        if result is not None:
            return result
        result = self.find_the_same(2)
        if result is not None:
            return result
        result = self.find_the_diff(3, 0)
        if result is not None:
            return result
        return None

    def sup_yinyun(self, wave):
        game_end = False
        chcektime = time.time()
        try:
            wave = [self.get_wave(), self.get_wave(), self.get_wave()]
            #取3次做平均
            self.wave= int(wave[0]+wave[1]+wave[2]//3)
        except:
            '''此處若無問題 可以刪除'''
            print("get_wave error")
            wave=self.get_wave()
            self.wave=wave
        while (not game_end):
            # if (chcektime-time.time() > 10):
            # chcektime = time.time()
            # img = self.img_tool.get_screenshot()
            if (self.gameview.choose_game() == 'main'):
                return 0
            now_wave = self.get_wave()
            if abs(self.wave - now_wave) < 10:
                self.wave = max(self.wave, now_wave)
            print('關卡:', int(self.wave))
            if (self.wave < 20 or self.wave > 25):
                self.call_dice()
            if (self.wave >= wave):
                return 1
            start = time.time()
            self.get_place()
            print('get_place time:', time.time()-start)
            start = time.time()
            result = self.deside_status()
            print('deside_status time:', time.time()-start)
            start = time.time()
            if result is not None:
                if result[0] == 1 and result[2] == 2:  # 小丑複製暗殺
                    self.mergydice(result[0], result[1],
                                   result[2], result[3], True, False, [])
                else:
                    self.mergydice(result[0], result[1],
                                   result[2], result[3], True, True, [])
                print('mergydice time:', time.time()-start)
            # for i in range(1, 8):
            #     self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
            # for i in range(1, 8):
            #     self.mergydice(1, i, 2, i, True, False, [])  # 小丑複製暗殺
            # for i in range(1, 8):
            #     self.mergydice(2, i, 0, i, True, True, [])  # 暗殺合成適應
            # for i in range(1, 8):
            #     self.mergydice(2, i, 2, i, True, True, [])  # 暗殺合成暗殺
            # for i in range(1, 8):
            #     self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
            # for i in range(1, 8):
            #     self.mergydice(3, i, 0, i, True, True, [])  # 招喚合成適應
            else:
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
                print('mergydice time:', time.time()-start)
            game_end = self.end_game()
            if (game_end):
                self.q.put("end_game")
                return 0

    def bubble_sup(self):
        game_end = False
        chcektime = time.time()
        try:
            wave = [self.get_wave(), self.get_wave(), self.get_wave()]
            #取3次做平均
            self.wave= int(wave[0]+wave[1]+wave[2]//3)
        except:
            '''此處若無問題 可以刪除'''
            print("get_wave error")
            wave=self.get_wave()
            self.wave=wave
        while (not game_end):
            if (chcektime-time.time() > 10):
                chcektime = time.time()
                if (self.gameview.choose_game() == 'main'):
                    return 0
            if abs(self.wave - self.get_wave()) < 10:
                self.wave = max(self.wave, self.get_wave())
            print('關卡:', int(self.wave))
            self.call_dice()
            self.get_place()
            self.printboardtype()
            self.printboardnum()
            print('招喚合成招喚')
            for i in range(1, 8):
                self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
                continue
            for i in range(1, 8):
                self.mergydice(0, i, 3, i, True, False, [])  # 小丑複製暗殺
                continue

            print('小丑複製泡泡')
            for i in range(1, 8):
                self.mergydice(1, i, 4, i, True, False, [])  # 小丑複製泡泡
                continue

            print('小丑複製招喚')
            for i in range(1, 8):
                self.mergydice(1, i, 3, i, True, False, [])  # 小丑複製招喚
                continue

            print('招喚合成招喚')
            for i in range(1, 8):
                self.mergydice(3, i, 3, i, True, True, [])  # 招喚合成招喚
                continue

            print('小丑複製泡泡')
            for i in range(1, 8):
                self.mergydice(1, i, 4, i, True, True, [])  # 小丑複製泡泡
                continue

            print('泡泡合成適應')
            for i in range(1, 8):
                self.mergydice(4, i, 0, i, True, True, [])  # 泡泡合成適應
                continue

            print('泡泡合成泡泡')
            for i in range(1, 8):
                self.mergydice(4, i, 4, i, True, True, [])  # 泡泡合成泡泡
                continue

            game_end = self.end_game()
            if (game_end):
                return 0


error = 0
dicenames = ['mimic', 'jocker', 'assassin', 'summon', 'bubble']

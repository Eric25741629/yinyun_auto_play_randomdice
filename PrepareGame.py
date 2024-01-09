import tools
from multiprocessing import Process, Queue
import uiautomator2 as u2
from view import gameview
import time
import random
import os
import cv2
import numpy as np


class prepareGame():
    def __init__(self, devices_ip, reader, q: Queue, act="att"):
        self.d = u2.connect(devices_ip)  # 手機的IP
        self.devices_ip = devices_ip
        self.reader = reader
        self.q = q
        self.act = act
        self.height = 960
        self.width = 540
        self.img_tool = tools.img_tool(self.d, reader)
        self.str_tool = tools.str_tool(self.d, reader)
        self.click_tool = tools.click_tool(
            self.d, reader, self.height, self.width)
        self.gameview = gameview(
            self.d, self.reader, self.img_tool, self.str_tool, self.click_tool)
        self.action = {
            'main': lambda: self.gameview.click_tool.click_str('合作模式'),
            'news': lambda: self.click_tool.close(),
            'news1': lambda: self.click_tool.close(),
            'season': lambda: self.click_tool.close(),
            'cooperation_first': lambda: self.click_tool.click_position(random.randint(360, 486), random.randint(330, 375)),
            'cooperation_second': lambda: self.gameview.click_tool.click_str('與好友一起進行遊戲'),
            'cooperation_third': lambda: self.gameview.click_tool.click_str('創建房間'),
            'join_room': lambda: self.click_tool.click_position(random.randint(295, 460), random.randint(530, 588)),
            'cooperation_wait': lambda: self.wait_all_player(),
            'cooperation_join': lambda: self.input_the_room_num(),
            'wait': lambda: time.sleep(5),
            'wait1': lambda: time.sleep(4),
            'wait2': lambda: time.sleep(3),
            'wait3': lambda: time.sleep(2),
            'wait4': lambda: time.sleep(0.5),
            'No_times': lambda: self.buy_times(),
            'Known': lambda: self.gameview.click_tool.click_str('確認'),

        }

    def open_oproom(self):
        while True:
            state = self.gameview.choose_game()
            print(state)
            if state == 'break':
                self.q.put(1)
                break
            if state in self.action:
                if state == 'cooperation_third' and self.act != 'att':
                    state = 'join_room'
                self.action[state]()
                if state == 'cooperation_wait':
                    break
            time.sleep(1)

    def buy_times(self):
        self.click_tool.click_position(
            random.randint(306, 428), random.randint(554, 600))
        time.sleep(1)

    def get_from_q(self):
        start = time.time()
        while self.q.empty():
            time.sleep(1)
            if time.time() - start > 60:
                return None
        return self.q.get()

    def input_the_room_num(self, num=None):
        if num is None:
            num = self.get_from_q()
        if num is None:
            return
        self.d.click(260, 450)
        time.sleep(random.random()*0.5)
        os.system("adb connect " + self.devices_ip)
        time.sleep(random.random()*0.5)
        os.system("adb -s " + self.devices_ip + " shell input text %04d" % num)
        time.sleep(random.random()*0.5)
        self.d.click(270, 600)
        time.sleep(random.random()*0.5)
        self.d.click(270, 600)
        time.sleep(3)

    def get_str(self, x1: int, x2: int, y1: int, y2: int):
        img = self.gameview.img_tool.get_screenshot()
        img = img[y1:y2, x1:x2]
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        result = self.reader.readtext(img)
        if result:
            return result
        else:
            return []

    def in_the_game(self):
        currentApp = self.d.app_list_running()
        for i in currentApp:
            if i == 'com.percent.royaldice':
                return 1
        return 0

    def opengame(self):
        currentApp = self.d.app_list_running()
        if "com.percent.royaldice" not in currentApp:
            self.d.app_start("com.percent.royaldice",
                             use_monkey=True, stop=True)

    def check_result(self, x1, y1, x2, y2):
        result = self.gameview.str_tool.get_text(x1, y1, x2, y2)
        print(result)
        if result:
            return True
        return False

    def room_num(self):
        print('正在取得房間號碼')
        while (1):
            result = self.gameview.str_tool.get_text(190, 300, 320, 350)
            if (result != []):
                break
        return int(result[0][1])

    def check_ingame(self):
        result = self.gameview.str_tool.get_text(144, 225, 12, 49)
        if result:
            return True
        return False

    def wait_all_player(self):
        num = self.room_num()
        self.q.put(num)
        while (1):
            try:
                img = self.gameview.img_tool.get_screenshot()
                crop_img = img[670:750, 200:330]
                b, g, r = crop_img[10, 10]
                if (b <= 12 and b >= 8 and g >= 173 and g <= 174 and r >= 251 and r <= 255):
                    print('玩家皆進入房間')
                    break
            except:
                pass
        return 0

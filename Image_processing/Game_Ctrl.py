import time
import uiautomator2 as u2
import numpy as np
import os
import random
import easyocr
from multiprocessing import Process, Queue
from Image_processing import game_view
from tools import tool
class ctrl_game(game_view.gameview, tool.open_game):
    def __init__(self, d: u2.Device, reader: easyocr.Reader, q: Queue, act="att", devices_ip: str = "None"):
        super().__init__(d=d, reader=reader)  # 呼叫 GameView 的初始化方法並傳遞參數
        tool.open_game.__init__(self, d)  # 呼叫 Open_Game 的初始化方法並傳遞參數
        self.devices_ip = devices_ip
        self.q = q
        self.act = act
        self.height = 960
        self.width = 540

    def click_position(self, x, y):
        self.d.click(x/self.width, y/self.height)

    def switch_what_to_do(self):
        self.openapp('com.percent.royaldice')
        t = time.time()
        while (time.time() - t < 150):
            Status = self.choose_game()
            print(Status)
            actions = {
                'main': self.enter_main_page,
                'news': self.click_news,
                'season': self.play_season,
                'confirm': self.click_confirm,
                'no_times': self.handle_no_times,
                'cooperation_first': self.click_cooperation_first,
                'cooperation_second': self.click_cooperation_second,
                'cooperation_third': self.click_cooperation_third,
                'cooperation_join_ok': self.wait_and_input_room_num
            }
            action = actions.get(Status)
            if action:
                action()
                if Status == 'cooperation_third':
                    break
                if Status == 'cooperation_join_ok':
                    break
            else:
                print('未知的狀態:', Status)
            if self.Check_if_it_is_running('com.percent.royaldice') == False:
                print('啟動遊戲')
                return

    def enter_main_page(self):
        print('進入主頁')
        time.sleep(2)
        self.click_position(383, 750)

    def click_news(self):
        self.click_position(466, 135)

    def play_season(self):
        self.click_position(466, 135)
        time.sleep(2)
        self.d.press("back")

    def click_confirm(self):
        self.click_position(265, 666)

    def handle_no_times(self):
        self.click_position(450, 740)
        time.sleep(2 + random.random() * 5)
        self.click_position(0.742, 0.611)
        time.sleep(2 + random.random() * 5)
        self.click_position(320, 800)  # 確認
        time.sleep(2 + random.random() * 5)

    def click_cooperation_first(self):
        self.click_position(200, 850)  # 與好友一起遊戲 進入協同介面 選擇與好友或是路人
        time.sleep(2)

    def click_cooperation_second(self):
        if self.act == "att":
            self.click_position(200, 550)
        else:
            self.click_position(400, 550)

    def wait_and_input_room_num(self):
        while (1):
            if self.q.empty():
                time.sleep(1)
            else:
                break
        num = self.q.get()
        print(num)
        self.click_position(270, 460)
        os.system("adb -s "+self.devices_ip+" shell input text %04d" % num)
        self.click_position(270, 600)
        self.click_position(270, 600)

    def get_room_num(self):
        while (1):
            result = self.get_str(190, 300, 320, 350)
            if (result != []):
                break
        return int(result[0])  # type: ignore

    def click_cooperation_third(self):
        num = self.get_room_num()
        self.q.put(num)

    def check_ingame(self):
        result = self.get_str(144, 225, 12, 49)
        if result:
            return True
        return False

    def begin_button(self):
        while (1):
            try:
                img = self.get_screenshot()
                crop_img = img[670:750, 200:330]  # type: ignore
                b, g, r = crop_img[10, 10]
                if (b <= 12 and b >= 8 and g >= 173 and g <= 174 and r >= 251 and r <= 255):
                    print('玩家皆進入房間')
                    break
            except:
                pass
        return 1
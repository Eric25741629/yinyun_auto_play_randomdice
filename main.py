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

import Store_Refresh
import watchAd
from model import Classifier, models
from pic_tranform import *

from torch import nn


#遊玩前置作業
class ctrl_game():
    def __init__(self,devices_ip,reader,q,act="att"):
        self.d=u2.connect(devices_ip) # 手機的IP
        self.AD=watchAd.watchAD(self.d)
        self.devices_ip=devices_ip
        self.reader=reader
        self.q=q
        self.act=act
        self.height=960
        self.width=540
    def get_screenshot(self, format='opencv'):
        img = None
        while img is None:
            img = self.d.screenshot(format=format)
        return img
    def get_str(self, x1:int, x2:int, y1:int, y2:int):
        img = self.get_screenshot()
        img = img[y1:y2, x1:x2]
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)

        result = self.reader.readtext(img)
        if result:
            return result
        else:
            return []


    def updata_game(self):
        self.d.click(368,590)
        t=time.time()
        while time.time()-t<30:
            if self.d.xpath('//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[2]').exists: # type: ignore
                self.d.xpath('//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[2]').click()
                break
        while not self.d.xpath('//*[@content-desc="開始玩"]'):
            print('start') 
        self.d.xpath('//*[@content-desc="開始玩"]').click()
    def in_the_game(self):
        currentApp = self.d.app_list_running()
        for i in currentApp:
            #print(i)
            if i == 'com.percent.royaldice':
                return 1
        return 0
    def opengame(self):
        currentApp = self.d.app_list_running()
        if "com.percent.royaldice" not in currentApp:
            self.d.app_start("com.percent.royaldice", use_monkey=True, stop=True)
        t=time.time()
        count=0
        while 1:
            img=self.d.screenshot(format='opencv')
            text=self.reader.readtext(img,detail=0) # replace () with []
            if ('應用程式版本不同'in text):
                print('需要更新')
                self.updata_game()
            result=self.get_str(370,485,733,850)
            # print(result)
            if len(result)>0:
                result=self.get_str(370,485,733,850)
                for i in range(len(result)):
                    if result[i][1]=='合作模式' or result[i][1]=='30' or '0/' in result[i][1]:
                        return
            if time.time()-t>90:
                print("open game fail")
                self.d.press("back")
            time.sleep(0.5)
            if time.time()-t>120:
                print("open game fail")
                t=time.time()
                self.d.app_stop("com.percent.royaldice")
                time.sleep(0.5)
                self.d.app_start("com.percent.royaldice", use_monkey=True, stop=True)
            if count>10:
                while 1:
                    print('open game fail')
                    time.sleep(1)

        print('進入主頁')
    def check_result(self, x1, y1, x2, y2):
        result = self.get_str(x1, y1, x2, y2)
        print(result)
        if result:
            return True
        return False
    def with_friend_attack(self):
        while 1:
            self.d.click(200, 850)  #與好友一起遊戲
            time.sleep(0.5)
            try:
                img=self.d.screenshot(format='opencv')
            except:
                img=self.d.screenshot(format='opencv')
            crop_img = img[280:320,140:400]
            result = self.reader.readtext[crop_img] # replace () with []
            print(result)
            if result!=[]:
                if '與好友一起進行遊戲' in result[0][1]:
                    break
        self.d.click(200, 550) 
        return True
    def room_num(self):
        while(1):
            result=self.get_str(190,300,320,350)
            if(result!=[]):
                break
        return int(result[0][1])
    def input_the_room_num(self,num):
        print(num)
        self.d.click(270, 460) 
        os.system("adb -s "+self.devices_ip+" shell input text %04d"%num)
        self.d.click(270, 600)
        self.d.click(270, 600)
    def watch_ad_to_openroom(self):
        count=1
        while(1):
            img = self.d.screenshot(format='opencv')
            self.d.click(500,706)
            time.sleep(0.5)
            text=reader.readtext(img, detail=0)
            print(text)
            if ('通知'in text and  '正在載入廣告'in  text and  '請稍後重試'in text and  '確認'in text):
                self.d.click(265, 592)
                count+=1
            if(count>3):
                print('商店補充失敗')
                self.d.app_stop("com.percent.royaldice")
                time.sleep(0.5)
                self.d.app_start("com.percent.royaldice", use_monkey=True, stop=True)
                self.opengame()
                break 
            self.AD.watchvideo()
            time.sleep(2)
            if (Store_Refresh.Shop(self.d,self.reader).checkinshop()):
                print('商店補充成功')
                break
            else:
                print('商店補充失敗')
                self.d.app_stop("com.percent.royaldice")
                time.sleep(0.5)
                self.d.app_start("com.percent.royaldice", use_monkey=True, stop=True)
                self.opengame()
                break
    def open_room(self):
        while True:
            result = self.get_str(370, 485, 733, 850)
            # print(result)
            img=self.d.screenshot(format='opencv')
            text=self.reader.readtext(img, detail=0)
            # print(text)
            if ('任務'in text and '主要任務'in  text and  '每日任務'in  text):
                self.d.click(0.896, 0.072)
            if result and result[0][1] == '合作模式': 
                print('合作!!!')
                break
            elif '30' in str(result) or '0/'in str(result):
                print('沒次數,廣告補充')
                # self.watch_ad_to_openroom()
                # if not check:
                #     print('廣告失敗')
                #     while(1):
                #         time.sleep(1)
                # self.opengame()
                # self.open_room()
                self.d.click(450,740)
                time.sleep(2+random.random()*5)
                self.d.click(0.742, 0.611)
                time.sleep(2+random.random()*5)
                self.d.click(320, 800)  #確認
        while True:
            result = self.get_str(370, 485, 733, 800)
            print(result)
            if result and result[0][1] == '合作模式': 
                print('合作模式第一層')
                self.click_position(383, 750)
            else:
                break
        while True:
            if not self.check_result(196, 330, 97, 138):
                print('合作模式第一層')
                break        
            self.click_position(193, 871)
        while True:
            print(1)
            result=self.get_str(134, 404, 269, 321)
            if not result or result[0][1] != '與好友一起進行遊戲':
                break 
            if (self.act=="att"):
                self.click_position(150, 572)
            else:
                self.click_position(365, 572)    
            time.sleep(5)
    def click_position(self, x, y):
        self.d.click(x/self.width, y/self.height)
    def check_ingame(self):
        result = self.get_str(144, 225, 12, 49) 
        if  result:
            return True
        return False
    def crop_image(self,img, x1, y1, x2, y2):
        return img[y1:y2, x1:x2]
    def check_times(self):
        while(1):
            crop_img=self.crop_image(self.get_screenshot(), 290, 710, 510, 800)
            result = self.reader.readtext(crop_img)
            for i in range(0,len(result)):
                if '合作模式'in result[i][1]:
                    print('合作!!!')
                    return result[i+1][1].split("/")[0]
                elif '30' in result[i][1]:
                    print('沒次數,廣告補充')
                    #todo


                    # print('沒次數,鑽石補充')
                    # self.d.click(450,740)
                    # time.sleep(2+random.random()*5)
                    # self.d.click(320, 550)
                    # time.sleep(2+random.random()*5)
                    # self.d.click(320, 800)

    def begin_button(self):
        while(1):
            try:
                try:
                    img=self.d.screenshot(format='opencv')
                except:
                    img=self.d.screenshot(format='opencv')
                crop_img = img[670:750,200:330]
                b,g,r=crop_img[10,10]
                if (b<=12 and b>=8 and g>=173 and g<=174 and r>=251 and r<=255):
                    print('玩家皆進入房間')
                    break
            except:pass      
        return 0

dicetype_num_model = models.mobilenet_v3_large(pretrained=True)
num_classes = 64
dicetype_num_model.classifier[-1] = nn.Linear(in_features=dicetype_num_model.classifier[-1].in_features, out_features=num_classes)
dicetype_num_model.load_state_dict(torch.load(r'V3model_epoch_8.pth'))
dicetype_num_model.eval()

reader = easyocr.Reader(['ch_tra'], gpu = True)    
class play():
    def __init__(self,devices,reader,q:Queue,player='att'):
        self.d=devices
        self.reader=reader
        self.player=player
        self.model=dicetype_num_model
        self.q=q
        self.wave=0
        #一個3*5*2的矩陣
        self.place = np.full((3, 5, 2), -1)
    def get_screenshot(self, format='opencv'):
        img = None
        while img is None:
            img = self.d.screenshot(format=format)
        return img
    def get_wave(self):
        for i in range(0,3):
            img = self.get_screenshot()
            img=img[15:50,120:250]
            ret, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # 二值化
            result = self.reader.readtext(binary)
            #print(result)
            if(result!=[]):
                numbers ="".join([x for x in result[0][1] if x.isdigit()])
                if numbers:
                    print('關卡:',int(numbers))
                    return int(numbers)
        return 0


    def get_place(self, who=None, path=None):
        time.sleep(0.2)
        if who == 'test' and path is not None:
            img = cv2.imread(path)
        else:
            img = self.get_screenshot()
        for i in range(0, 3):
            for j in range(0, 5):
                self.process_dice_image(img, i, j)

    def process_dice_image(self, img, i, j):
        pointx = int(j * 62.7 + 144)
        pointy = i * 60 + 512
        img2 = img[pointy - 32:pointy + 30, pointx - 30:pointx + 32]
        # cv2.imshow('test', img2)
        # cv2.waitKey(0)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        img2 = Image.fromarray(img2)
        dicenum, dicetype = detect_single_dice(img2, self.player, self.model)
        self.place[i][j][0] = dicetype
        self.place[i][j][1] = dicenum

    def printboardtype(self):
        for i in range(0,3):
            for j in range(0,5):
                print(self.place[i][j][0],end=' ')
            print()
    def printboardnum(self):
        for i in range(0,3):
            for j in range(0,5):
                print(self.place[i][j][1],end=' ')
            print()
    def call_dice(self):
        for _ in range(5):
            try:
                img = self.get_screenshot()
                crop_img = img[750:830, 230:310]
                b, g, r = crop_img[50, 50]
                if 245 <= b <= 255 and 245 <= g <= 255 and 245 <= r <= 255:
                    x = 270 + random.randint(-5, 5)
                    y = 790 + random.randint(-5, 5)
                    self.d.click(x, y)
            except:
                x = 270 + random.randint(-5, 5)
                y = 790 + random.randint(-5, 5)
                self.d.click(x, y)
    def level_up(self, dices):
        times = 0
        img = self.get_screenshot()  # 进行一次屏幕截图
        while times <= 2:
            level_list = [i for i, dice in enumerate(dices) if self._check_dice(img, dice)]
            if not level_list:
                times += 1
            else:
                for index in level_list:
                    self.click_dice_multiple_times(index)
                    time.sleep(2)

    def click_dice_multiple_times(self, index):
        random_offset = random.randint(-5, 5)
        for _ in range(5, 9):
            click_x = 80 + index * 100 + random_offset
            self.d.click(click_x, 900)


    # 其他辅助函数
    def _check_dice(self, img, dice):
        crop_img = img[900:945, 50 + dice * 100:130 + dice * 100]
        result = self.reader.readtext(crop_img)
        print(result)  # 调试输出
        return bool(result)

    def end_game(self):
        try:
            img = self.get_screenshot()
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
            # Simulate pressing the dice
            # print(row, column, target_x, target_y)
            start_x = column * 62 + 120 + random.randint(25, 40)
            start_y = row * 60 + 470 + random.randint(25, 40)
            end_x = int(target_x) * 62 + 480 + random.randint(25, 40)
            end_y = int(target_y) * 60 + 120 + random.randint(25, 40)
            # print(start_x, start_y, end_y, end_x)
            self.d.swipe(start_x, start_y, end_y, end_x, 0.05)
        except Exception as err:
            print(err)
            pass

    def mergydice(self, use_type: int, use_num: int, target_type: int, target_num: int, use_all: bool, remove: bool, cache: list):
        use = np.where((self.place[:, :, 0] == use_type) & (self.place[:, :, 1] == use_num))
        use = np.transpose(use).tolist()
        target = np.where((self.place[:, :, 0] == target_type) & (self.place[:, :, 1] == target_num))
        target = np.transpose(target).tolist()

        if not use or not target:
            return 0

        if not cache:
            if use_all:
                self.move_all_dices(use, target, remove)
            else:
                self.move_single_dice(use, target, remove)
        self.get_place()
    def move_all_dices(self, use, target, remove):
        for i in use:
            if not target:
                break
            chosen = random.choice(range(len(target)))
            selected = target.pop(chosen) if remove else target[chosen]
            if i[0]==selected[0] and i[1]==selected[1] and len(target)!=0:
                continue
            self.move_dice(i[0], i[1], selected[0], selected[1], 0.05)

    def move_single_dice(self, use, target, remove):
        chosen = random.choice(range(len(target)))
        selected = target.pop(chosen)
        self.move_dice(use[0][0], use[0][1], selected[0], selected[1], 0.05)
    dicelist = ['growning', 'yinyun', 'jocker', 'sup', 'broke_growning', ]
    def yinyun_attack(self):
        game_end = False
        know=0
        while(not game_end):
            self.wave=max(self.wave,self.get_wave())
            if(self.wave>=20 and know==0):
                self.q.put("暗殺")
                know=1
            self.call_dice()
            self.get_place()
            for i in range(1,7):
                self.mergydice(2,i,0,i,True,False,[])#小丑複製成長
            for i in range(1,8):
                self.mergydice(2,i,1,i,True,False,[])#小丑複製陰陽
            for i in range(1,8):
                self.mergydice(3,i,1,i,True,True,[])#營養餵給陰陽

            yinyun_num = len(np.where(self.place[:, :, 0] == 1)[0])
            print(yinyun_num)
            if (yinyun_num == 15):
                self.q.put("暗殺")
                return 1
            game_end=self.end_game()
            if(game_end):
                self.q.put("end_game")
                return 0
    def sup_yinyun(self,wave):
        game_end = False
        while(not game_end):
            self.wave=max(self.wave,self.get_wave())
            if (self.wave <20 or self.wave>25):
                self.call_dice()       
            if(self.wave>=wave):
                return    
            self.get_place()
            for i in range(1,8):
                self.mergydice(3,i, 3,i, True, True, [])#招喚合成招喚
            for i in range(1,8):
                self.mergydice(1,i, 2,i, True, False, [])#小丑複製暗殺
           
            for i in range(1,8):
                self.mergydice(2,i, 0,i, True, True, [])#暗殺合成適應

            for i in range(1,8):
                self.mergydice(2,i, 2,i, True, True, [])#暗殺合成暗殺
            for i in range(1,8):
                self.mergydice(3,i, 3,i, True, True, [])#招喚合成招喚
            for i in range(1,8):
                self.mergydice(3,i, 0,i, True, True, [])#招喚合成適應
            
            game_end=self.end_game()
            if(game_end):
                self.q.put("end_game")
                return 0
    def bubble_sup(self):
        game_end = False
        while(not game_end):
            self.wave=max(self.wave,self.get_wave())  
            self.get_place()
            for i in range(1,8):
                self.mergydice(3,i, 3,i, True, True, [])#招喚合成招喚
            for i in range(1,8):
                self.mergydice(1,i, 4,i, True, False, [])#小丑複製泡泡
            for i in range(1,8):
                self.mergydice(1,i, 3,i, True, False, [])#小丑複製招喚
            for i in range(1,8):
                self.mergydice(3,i, 3,i, True, False, []) #招喚合成招喚
            for i in range(1,8):
                self.mergydice(1,i, 4,i, True, False, [])#小丑複製泡泡
            for i in range(1,8):
                self.mergydice(4,i, 0,i, True, True, [])#泡泡合成適應
            for i in range(1,8):
                self.mergydice(4,i, 4,i, True, False, [])#泡泡合成泡泡
            game_end=self.end_game()
            if(game_end):
                self.q.put("end_game")
                return 0
error=0
dicenames = ['mimic','jocker','assassin','summon', 'bubble']





def dicer_att(adb_devices,q:Queue):
    attctrl=ctrl_game(adb_devices,reader,q) 
    while(attctrl.check_ingame()):pass
    d = attctrl.d
    global count
    attctrl.opengame()
    attctrl.open_room()
    roomnum=attctrl.room_num()
    print(roomnum)
    q.put(roomnum)
    attctrl.begin_button()
    d.click(250, 700)  
    start_time=time.time()
    while(not attctrl.check_ingame()):
        print(time.time()-start_time)
        if (time.time()-start_time>120):
            q.put('房間開啟失敗')
            d.app_stop('com.percent.royaldice')
            return 
        time.sleep(1)
    q.put('房間開啟成功')
    attack_game_ctrl=play(d,reader,q,player='att')
    check=attack_game_ctrl.yinyun_attack()
    if(check!=0):
        attack_game_ctrl.level_up([0])

    while(not attack_game_ctrl.end_game()):
        # dice_number(d,'atta',place)
        time.sleep(5)
        


def dicer_sup(adb_devices,q:Queue):
    supctrl=ctrl_game(adb_devices,reader,q,act='sup') 
    d =supctrl.d
    supctrl.opengame()
    supctrl.open_room()
    while(q.empty()):
        time.sleep(0.2)
    roomnum=q.get()
    sup_game_ctrl=play(d,reader,q,player='sup')

    time.sleep(5)
    supctrl.input_the_room_num(roomnum)
    start_time=time.time()
    while(not supctrl.check_ingame()):
        # while(not attctrl.check_ingame()):
        print(time.time()-start_time)
        if (time.time()-start_time>120):
            d.app_stop('com.percent.royaldice')
            break
        time.sleep(1)
    if (q.get()=="房間開啟成功"):pass
    elif(q.get()=="房間開啟失敗"):
            d.app_stop('com.percent.royaldice')
            return
    while(q.empty()):
        #sct(d)
        sup_game_ctrl.call_dice()
        time.sleep(1)
    time.sleep(3)
    check=sup_game_ctrl.sup_yinyun(62)
    if(check==0):
        sup_game_ctrl.level_up([4])
        sup_game_ctrl.bubble_sup()
    #num=q.put(1)
global image_num
image_num=0
def sct(d):
    #time.sleep(10)
    # while(1):
    global image_num
    image = d.screenshot(format='opencv')
    #如果圖片存在的話，image_num就會一直加1 直到圖片不存在
    while(os.path.isfile(r"D:\dice_py\123/{}.jpg".format(image_num))):
        image_num+=1
    cv2.imwrite(r"D:\dice_py\123/{}.jpg".format(image_num),image)
    #time.sleep(1)
    image_num+=1
      
reader = easyocr.Reader(['ch_tra'], gpu = True)     

def reset():
    global count
    count=0
    time.sleep(21500)
    count=1
global count
count=1
import ctypes
if __name__ == '__main__':
    os.system("adb devices")
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
        tsup = threading.Thread( target=dicer_sup, args=( 'emulator-5556',queue) )
        tatt = threading.Thread( target=dicer_att, args=( 'emulator-5554',queue) )
        tatt.start()
        tsup.start()
        tatt.join(2000)
        tsup.join(2000)
        # 強制終止線程
        if tsup.is_alive():
            # 如果你確定線程在 join() 方法上阻塞，可以考慮使用下面的代碼來強制終止線程
            tid = tsup.ident
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(SystemExit))
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
                print('無法終止線程')
            else:
                print('線程已終止')
                d=u2.connect('emulator-5556')
                d.app_stop('com.percent.royaldice')
                d=u2.connect('emulator-5554')
                d.app_stop('com.percent.royaldice')
        
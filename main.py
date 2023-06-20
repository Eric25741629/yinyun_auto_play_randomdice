import os
import random
import threading
import time
from cmath import sqrt
from multiprocessing import Process, Queue

import cv2
# 連接手機
import easyocr
import numpy as np
import torch
import uiautomator2 as u2
from adbutils import adb

import Store_Refresh
import watchAd
from pic_tranform import *
from model import Classifier
from model import models
from torch import nn

dicetype_num_model = models.mobilenet_v3_large(pretrained=True)
num_classes = 64
dicetype_num_model.classifier[-1] = nn.Linear(in_features=dicetype_num_model.classifier[-1].in_features, out_features=num_classes)
dicetype_num_model.load_state_dict(torch.load(r'V3model_epoch_8.pth'))
dicetype_num_model.eval()
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
    def get_str(self,x1,x2,y1,y2):
        while 1:
            img=get_screenshot(self.d)# self.d.screenshot(format='opencv')
            img=cv2.cvtColor(img[y1:y2,x1:x2],cv2.COLOR_BGR2GRAY)
            break
        result=self.reader.readtext(img) # replace () with []
        if len(result)>0:
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
        self.d.xpath('//*[@content-desc="開始玩"]')()
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
    def check_times(self):
        while(1):
            crop_img=crop_image(get_screenshot(self.d), 290, 710, 510, 800)
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
#遊玩中控制類
class play():
    def __init__(self,d,reader,act,model):
        self.d=d
        self.reader=reader
        self.width, self.height = self.d.window_size()
        self.act=act
        self.model=model
        #一個3*5*2的矩陣
        self.place=np.array(3,5,2)
        self.place=np.zeros((3,5,2)).fill(-1)
    def get_dice_type_and_num(self, who=None,path=None):
        time.sleep(0.2)
        if who == 'test' and path is not None:
            image=cv2.imread(path)
        else:
            while(1):
                image = self.d.screenshot(format='opencv')
                if image is not None:
                    break
        self.place.fill(-1) 
    def printboardnum(self):
        for i in range(0,3):
            for j in range(0,5):
                print(self.place[i][j][0],end=' ')
            print()
        
#class game
def color(img,x,y):
    print(img[x,y])
def get_screenshot(d, format='opencv'):
    img = None
    while img is None:
        img = d.screenshot(format=format)
    return img

def crop_image(img, x1, y1, x2, y2):
    return img[y1:y2, x1:x2]
def call_dice(d):
    for _ in range(0,5):
        try:
            img=get_screenshot(d)
            crop_img = img[750:830,230:310]
            b,g,r=crop_img[50,50]
            if(b in range(245,256) and g in range(245,256) and r in range(245,256)):
                d.double_click(270+int(random.random()*30), 790+int(random.randint(-5,5)))  
        except :
            d.click(270+int(random.random()*30), 790+int(random.randint(-5,5))) 

def level_up(d,dices):
    times=0
    while(1):
        level_list=[]
        img=get_screenshot(d)
        for i in dices:
            crop_img = img[900:945,50+i*100:130+i*100]
            result = reader.readtext(crop_img)
            print(result)
            if(result!=[]):
                level_list.append(i)
        if(level_list==[]):
            times=times+1
            if(times>2):
                break
        for i in level_list:
            for _ in range(0,random.randint(3,4)):
                d.click(80+i*100+int(random.random()*10), 900)
            #d.click(80+i*100+int(random.random()*10), 900) 
        time.sleep(2)
        

def check_into_game(d):
    while(1):
        #img=cv2.imread(r'E:/Screenshot_20220819-005635.png')
        img=get_screenshot(d)
            
        img=img[733:800,370:485]
        ret, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # 二值化
        dst = 255 - binary
        result = reader.readtext(dst)
        if(result!=[]):
            if(int(result[0][1])>=1):
                print('已進入遊戲')
                break


def object_detection(img, model):
    results = model(img)
    results = results.pandas().xyxy[0].to_dict(orient="records")
    return results

def get_dice_value(x, y):
    return int((x - 115) / 60), int((y - 475) / 60)

def placedicedector(place, d, i=-1, j=-1, mode='None'):
    time.sleep(0.2)
    img = get_screenshot(d)
    results = object_detection(img, mode)
    for result in results:
        cs = result['class']
        x1 = int(result['xmin'])
        y1 = int(result['ymin'])
        x, y = get_dice_value(x1, y1)
        if not (0 <= x <= 4 and 0 <= y <= 2):
            continue
        place[y][x][1] = cs
        if y == i and j == x:
            return cs

def Stage(d):
    for i in range(0,3):
        img = get_screenshot(d)
        img=img[15:50,120:250]
        ret, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # 二值化
        result = reader.readtext(binary)
        #print(result)
        if(result!=[]):
            numbers ="".join([x for x in result[0][1] if x.isdigit()])
            if numbers:
                print('關卡:',int(numbers))
                return int(numbers)
    return 0

def end_game(d):
    try:
        img = get_screenshot(d)
        img=img[850:890,240:320]   
        result = reader.readtext(img)       
        print(result) 
        if(result!=[]):
            if(result[0][1]=='確認'):
                for i in range(3):
                    d.click(250,870)
                    time.sleep(2)
                return 1
        else:
            return 0    
    except:
        pass
error=0
def dice_number(d,mode,place):
    global error
    try:
        image = get_screenshot(d)
        for i in range(0, 3):
            for j in range(0, 5):
                pointx = j * 62 + 120
                pointy = i * 60 + 482
                img1 = image[pointy + 15:pointy +           
                            50, pointx + 5:pointx + 48]
                pointx = int(j * 62.7 + 144)
                pointy = i * 60 + 512
                img2 = image[pointy -32:pointy + 30, pointx - 30:pointx + 31]
                img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                img2 = Image.fromarray(img2)
                if mode=='sup':
                    dicenum, dicetype,error = dice_num(img1,img2,mode,error, int(place[i][j][1]),dicetype_num_model)
                else:
                    dicenum, dicetype,error = dice_num(img1,img2,mode,error, int(place[i][j][1]),dicetype_num_model)
                #print(x, y)
                try:
                    place[i][j][0] = dicenum
                    place[i][j][1] = dicetype
                except:
                    pass
    except:
        pass
    print("dice_number:")
    for i in range(0, 3):
        for j in range(0, 5):
            if place[i][j][0] == -1:
                print("{:>5}".format('none'), end=' ')
            else:
                print("{:>5}".format(place[i][j][0]), end=' ')
        print()
    print()
def dice(d,place, want_to_use, dicelists,model,delt='none'):
    moving = 0
    can_list = []

    for dicelist in dicelists:
        for i in range(0, 3):
            for j in range(0, 5):
                if place[i,j,1]==dicelist:
                    can_list.append([i,j,place[i,j,0],place[i,j,1]])
    #print(can_list)
    for i in range(0, 3):
        for j in range(0, 5):
            if place[i,j,1]==want_to_use:
                for k in range(0,len(can_list)):
                    if can_list[k][0]==i and can_list[k][1]==j:
                            continue
                    if place[i,j,0]==can_list[k][2]:
                        dice = placedicedector(
                                place,d, i, j, mode=model)
                        if(dice!=place[i,j,1]):
                            #print('錯誤')
                            break
                        '''dice = placedicedector(
                                place,d, can_list[k][0],can_list[k][1], mode=model)
                        if(dice!=can_list[k][3]):
                            print('錯誤')
                            break'''
                        print('起點'+str(i)+" "+str(j)+'目標'+str(can_list[k]))
                        pointx = int(can_list[k][1])*62+120+ random.randint(25,40)
                        pointy = int(can_list[k][0])*60+480+ random.randint(25,40)
                        #print(i,j,can_list[k][1],can_list[k][1])
                        touchtime = (
                                sqrt(pow(j*62+150-pointx, 2)+pow(i*60+510-pointy, 2))*0.001)
                        #move_dice(d,x1=j*62+150,y1=i*60+500,x2=pointx,y2=pointy,duringtime=touchtime.real)
                        move_dice(d, i, j,  int(can_list[k][1]), int(can_list[k][0]), touchtime)
                        dice = placedicedector(
                                place,d, i, j, mode=model)
                        if dice != want_to_use:
                            #print('確認使用成功')
                            moving = moving+1
                            if delt=='none':
                                can_list.pop(k)
                                for _ in range(0,len(can_list)):
                                    try:
                                        if can_list[_][0]==i and can_list[_][1]==j:
                                            can_list.pop(_)
                                            break
                                    except Exception as err:
                                        print(err)
                                        pass
                                place[i,j,0]=-1
                                place[i,j,1]=-1
                                d.click(270, 830) 
                                break
                            else:
                                break    
    return moving
import random

def move_dice(d, i, j, pointx, pointy, touchtime):
    try:
        # 模擬按下骰子
        x0 = j * 62 + 120 + random.randint(25, 40)
        y0 = i * 60 + 470 + random.randint(25, 40)
        
        d.touch.down(x=x0, y=y0)
        x1 = int(pointx) * 62 + 120 + 30
        y1 = int(pointy) * 60 + 480 + 30
        # 403 559 21354 30510
        print(x0, y0, x1, y1)
        #計算最短距離並移動
        #將距離切成四個點
        #計算每個點的距離
        #加上隨機值
        for _ in range(0,6):
            x2 = x0+(_*(x1-x0)/6)+random.randint(-5,5)
            y2 = y0+(_*(y1-y0)/6)+random.randint(-5,5)
            d.touch.move(x=x2, y=y2)
            # time.sleep(touchtime.real/8)
        # time.sleep(touchtime.real/2)
        # d.touch.move(x=(x1+x0)//2, y=(y1+y0)//2)
        # time.sleep(touchtime.real/2)
        d.touch.up(x=x1 + random.randint(-5, 5), y=y1 + random.randint(-5, 5))
        # 計算抛骰子的軌跡
        # 計算弧形軌跡的控制點
        # cx = (x0 + x1) / 2 + random.randint(-10, 10)
        # cy = (y0 + y1) / 2 + abs(x1 - x0) / 2 + random.randint(-10, 10)
        # for t in range(5):
        #     if t < 1:
        #         # 起始部分：貝茲曲線
        #         u = t / 10
        #     elif t < 3:
        #         # 中間部分：貝茲曲線
        #         u = (t - 1) / 20
        #     else:
        #         # 結束部分：貝茲曲線
        #         u = (t - 3) / 10
        #     x = int((1 - u) ** 2 * x0 + 2 * u * (1 - u) * cx + u ** 2 * x1)
        #     y = int((1 - u) ** 2 * y0 + 2 * u * (1 - u) * cy + u ** 2 * y1)
        #     # 模擬移動骰子
        #     d.touch.move(x=x + random.randint(-5, 5), y=y + random.randint(-5, 5))
        # # 模擬放開骰子
    except Exception as err:
        print(err)
        pass    
def no_check_dice(d,place, want_to_use, dicelists,model,delt='none'):
    moving = 0
    can_list = []
    for dicelist in dicelists:
        for i in range(0, 3):
            for j in range(0, 5):
                if place[i,j,1]==dicelist:
                    can_list.append([i,j,place[i,j,0],place[i,j,1]])
    #print(can_list)
    for i in range(0, 3):
        for j in range(0, 5):
            if place[i,j,1] != want_to_use:continue
            for k in range(0,len(can_list)):
                if can_list[k][0]==i and can_list[k][1]==j:
                        continue
                if place[i,j,0]==can_list[k][2]:
                    dice = placedicedector(
                            place,d, i, j, mode=model)
                    if(dice!=place[i,j,1]):
                        #print('錯誤')
                        break
                    '''dice = placedicedector(
                            place,d, can_list[k][0],can_list[k][1], mode=model)
                    if(dice!=can_list[k][3]):
                        print('錯誤')
                        break'''
                    #print('起點'+str(place[i,j])+'目標'+str(can_list[k]))
                    pointx = int(can_list[k][1])*62+120+ random.randint(25,40)
                    pointy = int(can_list[k][0])*60+480+ random.randint(25,40)
                    touchtime = (
                            sqrt(pow(j*62+150-pointx, 2)+pow(i*60+510-pointy, 2))*0.0001)
                    move_dice(d, i, j,  int(can_list[k][1]), int(can_list[k][0]), touchtime)
                    #dice = placedicedector(
                    #        place,d, i, j, mode=model)
                    #if dice != want_to_use:
                    #    print('確認使用成功')
                    #    moving = moving+1
                    if delt=='none':
                        can_list.pop(k)
                        for _ in range(0,len(can_list)):
                            try:
                                if can_list[_][0]==i and can_list[_][1]==j:
                                    can_list.pop(_)
                                    break
                            except Exception as err:
                                print(err)
                                pass
                        place[i,j,0]=-2
                        place[i,j,1]=-2
                        d.click(270, 830) 
                        break
                    else:
                        break    
    return moving
dicelist = ['growning', 'yinyun', 'jocker', 'sup', 'broke_growning', ]
def attack_dice(d,place,model):
    #待改
    for i in range(0, 3):
        for j in range(0, 5):
            if int (place[i][j][1]) != 2:continue
            try:
                yinyuns = np.where(place[:, :, 1] == 1)
                print(yinyuns)
                if not yinyuns:
                    break
                listOfIndices = list(zip(yinyuns[0], yinyuns[1]))
                lenth = len(listOfIndices)
                # 目標
                for times in range(0, lenth):
                    pointx = int(
                        listOfIndices[times][1]) *62+150
                    pointy = int(
                        listOfIndices[times][0]) *60+510
                    
                    print(str(j*62+150)+" "+str(i*60+510)+'to->'+str(pointx)+" "+str(pointy))
                    dice = placedicedector( place,d, i, j, mode=model)
                    if dice != 2:
                        print('確認複製成功')
                        break
                    else:
                        touchtime = (
                            sqrt(pow(j * 60 + 150 - pointx, 2) + pow(i * 60 + 510 - pointy, 2)) * 0.001)
                        print(listOfIndices[times][1], listOfIndices[times][0])
                        move_dice(d, i, j,  listOfIndices[times][1],  listOfIndices[times][0], touchtime)
                        # print(touchtime)
                        # d.touch.down(
                        #     x=j*62+150, y=i*60+510)  # 模拟按下
                        # down 和 move 之间的延迟，自己控制

                        # time.sleep(touchtime.real)
                        # d.touch.move(x=pointx, y=pointy)  # 模拟移动
                        # time.sleep(touchtime.real)
                        # d.touch.up(x=pointx, y=pointy)
                        # time.sleep(1)
                        #d.swipe_points(
                        #    [(j * 60 + 150, i * 60 + 550), (pointx, pointy)], touchtime.real)
                        #print(str(j*62+150)+" "+str(i*60+490)+'to->'+str(pointx)+" "+str(pointy)+str(touchtime))
                    time.sleep(1)
            except Exception as err:
                print(err)
                pass   
    for i in range(0, 3):
        for j in range(0, 5):
            if int (place[i][j][1]) != 3:continue
              
            try:
                yinyuns = np.where(place[:, :, 1] == 1)
                if not yinyuns:
                    break
                listOfIndices = list(zip(yinyuns[0], yinyuns[1]))
                lenth = len(listOfIndices)
                # 目標
                for times in range(0, lenth):
                    pointx = int(
                        listOfIndices[times][1]) * 62 + 120 + random.randint(25,40)
                    pointy = int(
                        listOfIndices[times][0]) * 62 + 470 + random.randint(25,40)
                    #print(str(j*62+150)+" "+str(i*60+490)+'to->'+str(pointx)+" "+str(pointy))
                    print(listOfIndices[times][1], listOfIndices[times][0])
                    dice = placedicedector(
                        place,d, i, j, mode=model)
                    if dice != 3:
                        #print('確認複製成功')
                        break
                    else:
                        touchtime = (
                            sqrt(pow(j * 60 + 150 - pointx, 2) + pow(i * 60 + 550 - pointy, 2)) * 0.0001)
                        move_dice(d, i, j,  listOfIndices[times][1], listOfIndices[times][0], touchtime)
                        # print(touchtime)
                        # d.touch.down(
                        #     x=j*62+150, y=i*60+500)  # 模拟按下
                        # # down 和 move 之间的延迟，自己控制
                        # time.sleep(touchtime.real)
                        # d.touch.move(x=pointx, y=pointy)  # 模拟移动
                        # time.sleep(touchtime.real)
                        # d.touch.up(x=pointx, y=pointy)
                        time.sleep(0.5)
                        #print(str(j*62+150)+" "+str(i*60+490)+'to->'+str(pointx)+" "+str(pointy)+str(touchtime))
                    time.sleep(0.5)
            except Exception as err:
                print(err)
                pass   
dicelist = ['growning', 'yinyun', 'jocker', 'sup', 'broke_growning', ]
def attack(d,model,q):
    i = 1
    column, row, height = 3, 5, 2
    place = np.empty((column, row, height))
    place = np.full((column, row, height), -1)
    stage=0
    put=0
    check=0
    while (1):
        
        stage=max(Stage(d),stage)
        #sct(d)
        if(stage>20 and put==0):
            q.put(1)
            put=1
        moving=0
        call_dice(d)
        placedicedector(place,d=d, mode=model)
        dices_num = len([b for a in place for b in a if b[1]>=0])
        if (dices_num >= 0):
            dice_number(d,'attack',place)
        #dices_num = len([b for a in place for b in a if b[0]>=0])
        print(dices_num)
        print('骰子種類')
        for i in range(0, 3):
            for j in range(0, 5):
                # 空2格對齊
                print("{:2d} ".format(place[i,j,1]), end="")
            print()
        '''print('骰子點數')
        for i in range(0, 3):
            for j in range(0, 5):
                print(place[i,j,0],end="")
            print()'''    
        if (dices_num >= 5):
            moving+=dice(d,place, 2, [1],model)
        placedicedector(place,d=d, mode=model)
        dice_number(d,'attack',place)
        if (dices_num >= 10):
            moving+=dice(d,place, 3, [1],model)
        placedicedector(place,d=d, mode=model)
        dice_number(d,'attack',place)
        if(moving==0 and ((np.sum(place[:, :, 1]==0)+np.sum(place[:, :, 1]==4)==0))and dices_num >= 13) :
            if(np.sum(place[:, :, 1]==2)>2):
                #attack_dice(d,place,model)
                moving+=dice(d,place, 2, [2],model)
        placedicedector(place,d=d, mode=model)
        dice_number(d,'attack',place)        
        if(moving==0 and ((np.sum(place[:, :, 1]==0)+np.sum(place[:, :, 1]==4)==0))and dices_num >= 13) : 
            print('偵錯')             
            attack_dice(d,place,model)  
        yinyun_num = np.sum(place[:, :,1] == 1)
        if (yinyun_num == 15):
            print('滿版陰陽')
            check+=1
            if(check==3):
                return 1
        i=end_game(d)
        if(i==1):
            return 0
def sup(d,reconciliation,model):
    column, row, height = 3, 5, 2
    place = np.empty((column, row, height))
    place = np.full((column, row, height), -1)
    while (1):
        check=in_the_game(d)
        if(check==0):
            break
        stage=Stage(d)
        #sct(d)
        if(stage>reconciliation):
            return 0
        #sct(d)
        if check>=20 and check<=25:pass #修改邏輯 不被獅子吼 所以不叫骰子 
        else:
            call_dice(d)
        # placedicedector(place,d, -1, -1, model)
        moving = 0
        location = len(place[place >= 0])
        # if (location >= 8):
        dice_number(d,'sup',place)
        moving += dice(d,place, 1, [2],model,'del')
        place = np.full((column, row, height), -1)
        for _ in range(4):
            # placedicedector(place, d=d, mode=model)
            dice_number(d, 'sup', place)
            if _ == 0:
                moving += dice(d, place, 3, [3], model)
            elif _ == 1:
                moving += dice(d, place, 1, [2], model, 'del')
            elif _ == 2:
                moving += dice(d, place, 2, [0, 2], model)
            elif _ == 3:
                moving += dice(d, place, 3, [3, 0], model)
            place = np.full((column, row, height), -1)

        if (moving == 0):
            moving += dice(d,place, 1, [3],model)
            if (moving == 0):
                #place要是滿的才能用
                location = len(place[place >= 0])
                if location == 15:  # 檢查 place 中元素的數量是否為 15
                    dice(d,place, 0, [0],model)
        print('moving'+str(moving))
        place = np.full((column, row, height), -1)
        i=end_game(d)
        if(i==1):
            return 1
dicenames = ['mimic',
                 'jocker',
                 'assassin',
                 'summon',
                 'bubble'
                 ]
def in_the_game(d):
    currentApp = d.app_list_running()
    for i in currentApp:
        #print(i)
        if i == 'com.percent.royaldice':
            return 1
    return 0
def bubble_sup(d,reconciliation,model):
    column, row, height = 3, 5, 2
    place = np.empty((column, row, height))
    place = np.full((column, row, height), -1)
    while (1):
        # placedicedector(place,-1,-1,supmodel)
        check=in_the_game(d)
        if(check==0):
            break
        #sct(d)
        stage=Stage(d)
        #sct(d)
        call_dice(d)
        if(stage>reconciliation):
            break
        placedicedector(place,d, -1, -1, model)
        moving = 0
        location = len(place[place >= 0])
        # print(location)
        if (location >= 8):
            #placedicedector(place,d=d, mode=model)
            dice_number(d,'sup',place)
        '''for i in range(0, 3):
            for j in range(0, 5):
                try:
                    print(place[i][j][0], dicenames[int(
                        place[i][j][1])], end="  ")
                except:
                    pass
            print()
        print()'''
        moving += dice(d,place, 3, [3],model)
        placedicedector(place,d=d, mode=model)
        dice_number(d,'sup',place)
        moving += dice(d,place, 1, [4, 3],model,'del')
        placedicedector(place,d=d, mode=model)
        dice_number(d,'sup',place)
        moving += dice(d,place, 3, [3],model)
        placedicedector(place,d=d, mode=model)
        dice_number(d,'sup',place)
        moving += dice(d,place, 4, [0, 4],model)
        placedicedector(place,d=d, mode=model)
        dice_number(d,'sup',place)
        moving += dice(d,place, 3, [3, 0],model)
        place = np.full((column, row, height), -1)
        i=end_game(d)
        if(i==1):
            break

def dicer_att(adb_devices,q):

    attctrl=ctrl_game(adb_devices,reader,q) 
    while(attctrl.check_ingame()):pass
    d = attctrl.d
    global count
    attctrl.opengame()
    # if (count==1):
        # shop=Store_Refresh.Shop(d,reader=reader)
        # if(shop.buy_and_fresh()):
        #     threading.Thread(target=reset).start()
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
            # attctrl.begin_button()
            # start_time=time.time()
            #結束此執行序
            q.put(-10)
            d.app_stop('com.percent.royaldice')
            return 
        time.sleep(1)
    check=attack(d,attackmodel,q)
    if(check!=0):
        level_up(d,[0])
        # d.app_stop('com.percent.royaldice')
        q.put(1)
    else:
        q.put(0)
    place=np.full((3,5,2),-1)
    while(not end_game(d)):
        dice_number(d,'atta',place)
        time.sleep(5)
        


def dicer_sup(adb_devices,q):
    supctrl=ctrl_game(adb_devices,reader,q,act='sup') 
    d =supctrl.d
    supctrl.opengame()
    supctrl.open_room()
    
    while(q.empty()):pass
    roomnum=q.get()
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
    if q.empty():pass    
    else:
        if(q.get()==-10):
            d.app_stop('com.percent.royaldice')
            return
    while(q.empty()):
        #sct(d)
        call_dice(d)
        
        time.sleep(1)
    time.sleep(3)
    check=sup(d,62,supmodel)
    if(check==0):
        level_up(d,[4])
        bubble_sup(d,1000,supmodel)
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
supmodel = torch.hub.load('ultralytics/yolov5',
    'custom', path=r'best_sup.pt')
attackmodel = torch.hub.load(
        'ultralytics/yolov5', 'custom', path=r'best(2).pt')
attackmodel.conf = 0.5
supmodel.conf = 0.6

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
        tsup = threading.Thread( target=dicer_sup, args=( 'emulator-5560',queue) )
        tatt = threading.Thread( target=dicer_att, args=( 'emulator-5558',queue) )
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
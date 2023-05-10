import os
import random
import shutil
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

from pic_tranform import *
class ctrl_game():
    def __init__(self,devices_ip,reader,q,act="att"):
        self.d=u2.connect(devices_ip) # 手機的IP
        self.devices_ip=devices_ip
        self.reader=reader
        self.q=q
        self.act=act
        self.height=960
        self.width=540
    def get_str(self,x1,x2,y1,y2):
        while(1):
            img=self.d.screenshot(format='opencv')
            img=cv2.cvtColor(img[y1:y2,x1:x2],cv2.COLOR_BGR2GRAY)
            break
        result=self.reader.readtext(img)
        if len(result)>0:
            return result
        else:
            return []

    def opengame(self):
        currentApp = self.d.app_list_running()
        if "com.percent.royaldice" not in currentApp:
            self.d.app_start("com.percent.royaldice", use_monkey=True, stop=True)
        while(1):
            result=self.get_str(370,485,733,800)
            
            if len(result)>0:
                if result[0][1]=='合作模式' or result[0][1]=='30' or result[0][1]=='0/10':
                        break
        print('進入主頁')
    def check_result(self, x1, y1, x2, y2):
        result = self.get_str(x1, y1, x2, y2)
        print(result)
        if result:
            return True
        return False
    def with_friend_attack(self):
        while(1):
            self.d.click(200, 850)  #與好友一起遊戲
            time.sleep(0.5)
            try:
                img=self.d.screenshot(format='opencv')
            except:
                img=self.d.screenshot(format='opencv')
            crop_img = img[280:320,140:400]
            result = self.reader.readtext(crop_img)
            print(result)
            if(result!=[]):
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
    def open_room(self):
        while True:
            result = self.get_str(370, 485, 733, 800)
            print(result)
            if result and result[0][1] == '合作模式': 
                print('合作!!!')
                break
            elif '30' in str(result) or '0/10'in str(result):
                print('沒次數,鑽石補充')
                self.d.click(450,740)
                time.sleep(1+random.random()*5)
                self.d.click(320, 550)
                time.sleep(1+random.random()*5)
                self.d.click(320, 800)  #確認
        while True:
            result = self.get_str(370, 485, 733, 800)
            if result and result[0][1] == '合作模式': 
                print('合作模式第一層')
                self.click_position(383, 750)
            else:
                break

        while True:
            if not self.check_result(196, 330, 97, 138):
                print('合作模式第一層')
                break        
            self.click_position(158, 808)
        while True:
            print(1)
            result=self.get_str(134, 404, 269, 321)
            if not result or result[0][1] != '與好友一起進行遊戲':
                break 
            if (self.act=="att"):
                self.click_position(150, 572)
            else:
                self.click_position(365, 572)    
    def click_position(self, x, y):
        self.d.click(x/self.width, y/self.height)
    def check_result(self, x1, y1, x2, y2):
        result = self.get_str(x1, y1, x2, y2)
        if not result:
            return False
        return True
    def check_ingame(self):
        result = self.get_str(144, 225, 12, 49) 
        if  result:
            return True
        return False
    def check_times(self):
        while(1):
            try:
                img= self.d.screenshot(format='opencv')
            except:
                img = self.d.screenshot(format='opencv')
            crop_img = img[710:800,290:510]
            result = reader.readtext(crop_img)
            for i in range(0,len(result)):
                #print(result[i][1])
                if '合作模式'in result[i][1]:
                    print('合作!!!')
                    return result[i+1][1].split("/")[0]
                elif '30' in result[i][1]:
                    print('沒次數,鑽石補充')
                    self.d.click(450,740)
                    time.sleep(1+random.random()*5)
                    self.d.click(320, 550)
                    time.sleep(1+random.random()*5)
                    self.d.click(320, 800)
#reader = easyocr.Reader(['ch_tra'], gpu = True)     

    
    # bubble_sup()
    #sup()
def color(img,x,y):
    print(img[x,y])



def into_mode(d):
    
    while(1):
        d.click(450, 750) #第一個開啟
        time.sleep(0.5)
        try:
            img=d.screenshot(format='opencv')
        except:
            img=d.screenshot(format='opencv')
        crop_img = img[100:140,150:350]
        #cv2.imshow("Image", crop_img)
        #cv2.waitKey(0)
        result = reader.readtext(crop_img)
        print(result)
        if(result!=[]):
            if '合作模式' in result[0][1]:
                break
        time.sleep(0.5)

def begin_button(d):
    while(1):
        try:
            try:
                img=d.screenshot(format='opencv')
            except:
                img=d.screenshot(format='opencv')
            crop_img = img[670:750,200:330]
            #color(crop_img,10,10)
            b,g,r=crop_img[10,10]
            #print(b,g,r)
            if (b<=12 and b>=8 and g>=173 and g<=174 and r>=251 and r<=255):
                print('玩家皆進入房間')
                break
        except:pass      
    return 0
def call_dice(d):
    for i in range(0,5):
        try:
            try:
                img=d.screenshot(format='opencv')
            except:
                img=d.screenshot(format='opencv')
            crop_img = img[750:830,230:310]
            b,g,r=crop_img[50,50]
            if(b in range(245,256) and g in range(245,256) and r in range(245,256)):
                d.double_click(270+int(random.random()*30), 830+int(random.random()*15))  
        except :
            d.click(270+int(random.random()*30), 830+int(random.random()*20)) 

def level_up(d,dices):
    times=0
    while(1):
        level_list=[]
        try:
            img=d.screenshot(format='opencv')
        except:
            img=d.screenshot(format='opencv')
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
            d.click(80+i*100+int(random.random()*10), 900) 
        time.sleep(2)
        
def input_the_room_num(d,num):
    print(num)
    d.click(270, 460) 
    os.system("adb -s emulator-5560 shell input text %04d"%num)
    time.sleep(0.3)
    d.click(270, 600)
def check_into_game(d):
    while(1):
        #img=cv2.imread(r'E:/Screenshot_20220819-005635.png')
        try:
            img=d.screenshot(format='opencv')
        except:
            img=d.screenshot(format='opencv')
            
        img=img[733:800,370:485]
        ret, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # 二值化
        dst = 255 - binary
        result = reader.readtext(dst)
        if(result!=[]):
            if(int(result[0][1])>=1):
                print('已進入遊戲')
                break

def get_screenshot(d):
    try:
        img = d.screenshot(format='pillow')
    except:
        img = d.screenshot(format='pillow')
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

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
        #break
        #time.sleep(0.3)


def Stage(d):
    times=0
    while(1):
        img=d.screenshot(format='opencv')
        img=img[15:50,120:250]
        ret, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # 二值化
        result = reader.readtext(binary)
        print(result)
        
        if(result!=[]):
            numbers ="".join([x for x in result[0][1] if x.isdigit()])
            #print((numbers))
            try:
                if(int(numbers)>15):
                    return int(numbers)
                else:
                    return -1
            except:
                return -1
        times=times+1
        if(times>3):
            return -1
def end_game(d):
    try:
        img=d.screenshot(format='opencv')
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
def dice_number(d,mode,place):
    try:
        image = d.screenshot(format='opencv')
        for i in range(0, 3):
            for j in range(0, 5):
                pointx = j * 62 + 120
                pointy = i * 60 + 480
                img = image[pointy + 13:pointy +
                            50, pointx + 5:pointx + 48]
                x, y = dice_num(img,mode, int(place[i][j][1]))
                #print(x, y)
                try:
                    place[i][j][1] = y
                    place[i][j][0] = x
                except:
                    pass
    except:
        pass
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
                        #print('起點'+str(place[i,j])+'目標'+str(can_list[k]))
                        pointx = int(can_list[k][1])*62+120+ random.randint(25,40)
                        pointy = int(can_list[k][0])*60+480+ random.randint(25,40)
                        #print(i,j,can_list[k][1],can_list[k][1])
                        touchtime = (
                                sqrt(pow(j*62+150-pointx, 2)+pow(i*60+510-pointy, 2))*0.0001)
                        d.touch.down(
                                x=j*62+120+ random.randint(25,40), y=i*60+470+ random.randint(25,40))  # 模拟按下        
                        time.sleep(touchtime.real)
                        d.touch.move(x=int((pointx+j*62+120+ random.randint(25,40))/2), y=int((pointy+i*60+470 + random.randint(25,40))/2))  # 模拟移动
                        time.sleep(touchtime.real)
                        d.touch.move(x=pointx, y=pointy)
                        time.sleep(touchtime.real)
                        d.touch.up(x=pointx, y=pointy)
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
                        #print('起點'+str(place[i,j])+'目標'+str(can_list[k]))
                        pointx = int(can_list[k][1])*62+120+30
                        pointy = int(can_list[k][0])*60+480+30
                        #print(i,j,can_list[k][1],can_list[k][1])
                        touchtime = (
                                sqrt(pow(j*62+150-pointx, 2)+pow(i*60+510-pointy, 2))*0.0001)
                        d.touch.down(
                                x=j*62+150, y=i*60+500)  # 模拟按下        
                        time.sleep(touchtime.real)
                        d.touch.move(x=int((pointx+j*62+150)/2), y=int((pointy+i*60+500)/2))  # 模拟移动
                        time.sleep(touchtime.real)
                        d.touch.move(x=pointx, y=pointy)
                        time.sleep(touchtime.real)
                        d.touch.up(x=pointx, y=pointy)
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
def attack_dice(d,place,model):
    for i in range(0, 3):
        for j in range(0, 5):
            if (int(place[i][j][1]) == 2):
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
                            listOfIndices[times][1]) * 60 + 120 + 30
                        pointy = int(
                            listOfIndices[times][0]) * 60 + 480 + 30
                        #print(str(j*62+150)+" "+str(i*60+490)+'to->'+str(pointx)+" "+str(pointy))
                        dice = placedicedector(
                            place,d, i, j, mode=model)
                        if dice != 2:
                            #print('確認複製成功')
                            break
                        else:
                            touchtime = (
                                sqrt(pow(j * 60 + 150 - pointx, 2) + pow(i * 60 + 510 - pointy, 2)) * 0.0001)
                            # print(touchtime)
                            d.touch.down(
                                x=j*62+150, y=i*60+510)  # 模拟按下
                            # down 和 move 之间的延迟，自己控制
                            time.sleep(touchtime.real)
                            d.touch.move(x=pointx, y=pointy)  # 模拟移动
                            time.sleep(touchtime.real)
                            d.touch.up(x=pointx, y=pointy)
                            time.sleep(1)

                            #d.swipe_points(
                            #    [(j * 60 + 150, i * 60 + 550), (pointx, pointy)], touchtime.real)
                            #print(str(j*62+150)+" "+str(i*60+490)+'to->'+str(pointx)+" "+str(pointy)+str(touchtime))
                        time.sleep(1)
                except Exception as err:
                    print(err)
                    pass   
    for i in range(0, 3):
        for j in range(0, 5):
            if (int(place[i][j][1]) == 3):         
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
                        dice = placedicedector(
                            place,d, i, j, mode=model)
                        if dice != 3:
                            #print('確認複製成功')
                            break
                        else:
                            touchtime = (
                                sqrt(pow(j * 60 + 150 - pointx, 2) + pow(i * 60 + 550 - pointy, 2)) * 0.0001)
                            # print(touchtime)
                            d.touch.down(
                                x=j*62+150, y=i*60+500)  # 模拟按下
                            # down 和 move 之间的延迟，自己控制
                            time.sleep(touchtime.real)
                            d.touch.move(x=pointx, y=pointy)  # 模拟移动
                            time.sleep(touchtime.real)
                            d.touch.up(x=pointx, y=pointy)
                            time.sleep(1)
                            #print(str(j*62+150)+" "+str(i*60+490)+'to->'+str(pointx)+" "+str(pointy)+str(touchtime))
                        time.sleep(1)
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
    while (1):
        
        stage=max(Stage(d),stage)
        sct(d)
        if(stage>20 and put==0):
            q.put(1)
            put=1
        moving=0
        call_dice(d)
        placedicedector(place,d=d, mode=model)
        #dices_num = np.count_nonzero(place)
        dices_num = len([b for a in place for b in a if b[1]>=0])
        #dices_num = len(place[place >= 0])
        if (dices_num >= 0):
            dice_number(d,'attack',place)
        #dices_num = len([b for a in place for b in a if b[0]>=0])
        '''print(dices_num)
        print('骰子種類')
        for i in range(0, 3):
            for j in range(0, 5):
                print(place[i,j,1],end="")
            print()
        print('骰子點數')
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
            attack_dice(d,place,model)  
        yinyun_num = np.sum(place[:, :,1] == 1)
        if (yinyun_num == 15):
            print('滿版陰陽')
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
        sct(d)
        if(stage>reconciliation):
            return 0
        call_dice(d)
        placedicedector(place,d, -1, -1, model)
        moving = 0
        location = len(place[place >= 0])
        if (location >= 8):
            dice_number(d,'sup',place)
        moving += dice(d,place, 1, [2, 3],model,'del')
        placedicedector(place,d=d, mode=model)
        dice_number(d,'sup',place)
        moving += dice(d,place, 3, [3],model)
        placedicedector(place,d=d, mode=model)
        dice_number(d,'sup',place)
        moving += dice(d,place, 2, [0, 2],model)
        placedicedector(place,d=d, mode=model)
        dice_number(d,'sup',place)
        moving += dice(d,place, 3, [3, 0],model)
        if (moving == 0):
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
        sct(d)
        stage=Stage(d)
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
def update(d):
    while(1):
        if d.xpath('//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[2]/android.view.View[3]').wait():
            break
    d.xpath('//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[2]/android.view.View[3]').click()
    while(1):
        if d(text="開始玩").wait(timeout=20):
            d.app_stop('com.android.vending')
            d.app_start("com.percent.royaldice", use_monkey=True)
            break    
def open_the_game(d):
    currentApp = d.app_list_running()
    test=0
    for i in currentApp:
        #print(i)
        if i == 'com.percent.royaldice':
            test=1
            break
    if(test==0):
        d.app_start("com.percent.royaldice", use_monkey=True)
    start_time=time.time()
    while(1):
        try:
            now=time.time()
            if(now-start_time>180):
                start_time=time.time()
                d.app_stop('com.percent.royaldice')
                time.sleep(1)
                d.app_start("com.percent.royaldice", use_monkey=True)
            image=d.screenshot(format='opencv')
            result = reader.readtext(image)
            print(result)
            if(result!=[]):
                if(result[0][1]=='通知' and result[1][1]=='應用程式版本不同'):
                    print('版本更新')
                    d.click(380, 592)
                    update(d)
                if('商店' in str(result) and '娛柴' in str(result)):
                    print('進入主頁')
                    break
                if('公告'in str(result)):
                    d.click(480, 95)
                    time.sleep(1)
        except:
            pass
def dicer_att(adb_devices,q):
    attctrl=ctrl_game(adb_devices,reader,q) 
    while(attctrl.check_ingame()):pass
    d = attctrl.d
    attctrl.opengame()
    attctrl.open_room()
    roomnum=attctrl.room_num()
    print(roomnum)
    q.put(roomnum)
    begin_button(d)
    d.click(250, 700)  
    while(not attctrl.check_ingame()):pass
    check=attack(d,attackmodel,q)
    if(check!=0):
        level_up(d,[0])
        d.app_stop('com.percent.royaldice')
        q.put(1)
    else:
        q.put(0)

def dicer_sup(adb_devices,q):
    supctrl=ctrl_game(adb_devices,reader,q,act='sup') 
    d =supctrl.d
    supctrl.opengame()
    supctrl.open_room()
    while(queue.empty()):pass
    roomnum=queue.get()
    supctrl.input_the_room_num(roomnum)
    while(not supctrl.check_ingame()):pass
    while(q.empty()):
        call_dice(d)
    time.sleep(3)
    check=sup(d,52,supmodel)
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
    cv2.imwrite(str(image_num)+'.jpg',image)
    #time.sleep(1)
    image_num+=1
      
reader = easyocr.Reader(['ch_tra'], gpu = True)     
supmodel = torch.hub.load('ultralytics/yolov5',
    'custom', path=r'D:\dice_py/best_sup.pt')
attackmodel = torch.hub.load(
        'ultralytics/yolov5', 'custom', path=r'D:\dice_py/best(2).pt')
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
        tatt = threading.Thread( target=dicer_att, args=( 'emulator-5558',queue) )
        tatt.start()
        tsup.start()
        tatt.join()
        tsup.join()


    
   
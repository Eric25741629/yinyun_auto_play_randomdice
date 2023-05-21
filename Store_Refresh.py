import cv2
import numpy as np
import time
class Shop():
    def __init__(self,d,reader):
        self.d=d
        self.reader=reader

    def gotoshop(self):
        self.d.click(65,904)
        time.sleep(1)
        self.d.swipe(0.5,0.2,0.5,0.4)
        time.sleep(2)
        self.d.swipe(0.5,0.4,0.5,0.2)
        time.sleep(2)
    def if_legend(self):
        #img=cv2.imread(r'C:\Users\eric\Documents\XuanZhi9\Pictures\Screenshots\Screenshot_20230520-232514.png')
        img=self.d.screenshot(format='opencv')
        #印出顏色
        img=img[450:644,370:500]
        text=(self.reader.readtext(img,detail=0))
        if ('40000'in text):
            print('40000')
            return 1
        return 0

    def buy_legenddice(self):
        self.d.click(426,513)#點擊最左下角
        time.sleep(2)
        self.d.click(293,620)#確認購買
        time.sleep(2)
        self.d.click(287,669)#確定 

    def thesamecolor(self,img,x,y,b,g,r,thresold):
        # 获取像素值
        pixel_value = img[x, y]
        # 给定的值
        given_value = np.array([b,g,r])
        # 计算像素值之间的差异
        difference = np.abs(pixel_value - given_value)
        
        # 判断像素值是否接近
        if np.all(difference <= thresold):
            return 1
        else:
            return 0    
    def checkrefresh(self):
        img=self.d.screenshot(format='opencv')
        img=img[767:803,323:400]
        # print(img[20,10])
        if(self.thesamecolor(img,20,10,18,119,213,20)):
            print('yes')
            return 1
        else:
            return 0
    def refresh(self):
        self.d.click(356,786)
        img=self.d.screenshot(format='opencv')
        text=(self.reader.readtext(img,detail=0))
        if('重置商店'in text or '確定要更新每日特別商品清單嗎'):
            self.d.click(267,588)

    def watchvideo(self):
        time.sleep(5)
        start=time.time()
        while(time.time()-start<40):
            #print(d.info['currentPackageName'])
            currentApp = self.d.app_list_running()
            for i in currentApp:
                # print(i)
                if i=='com.android.vending':
                    self.d.app_stop(i)
            if(self.d(resourceId="com.android.vending:id/0_resource_name_obfuscated", description="Close").exists):        
                self.d(resourceId="com.android.vending:id/0_resource_name_obfuscated", description="Close").click()        
            if(self.checkinshop()):
                return 1
        return 0

    def checkinshop(self):
        img=self.d.screenshot(format='opencv')[880:960,:]
        text=(self.reader.readtext(img,detail=0))
        count=0
        for i in text:
            if ('商店'== i or'背包'== i or '娛樂'== i or '社交'== i):
                count+=1
        if(count>=3):
            print('yes')       
            return 1
        return 0        
    def buy_and_fresh(self):
        a=0
        self.gotoshop()
        if(self.if_legend()):
            self.buy_legenddice()
            time.sleep(1)
            if(not self.checkinshop()):
                self.d.press('back')
        if(self.checkrefresh()):
            self.refresh()
            if(self.watchvideo()):
                self.d.click(102,218)
                if(self.if_legend()):
                    self.buy_legenddice()
            a=1
        self.d.click(300,900)
        return a
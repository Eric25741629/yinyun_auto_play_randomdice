import cv2
import numpy as np

import cv2
dicenames = ['mimic',
             'jocker',
             'assassin',
             'summon',
             'bubble'
             ]



def HoughCircles_Count_dice_num(img):
    img = cv2.resize(img, (240, 240))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 轉為灰度
    ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)  # 二值化

    Canny = cv2.Canny(binary, threshold1=30, threshold2=255)  # 描邊

    circles = []
    circles = cv2.HoughCircles(Canny, cv2.HOUGH_GRADIENT, 2, 50, param1=30, param2=70, minRadius=10, maxRadius=-1)  # 找圓
    try:
        circles = np.uint16(np.around(circles))
        '''for i in circles[0, :]:
           # draw the outer circle
            cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
        '''
        # cv2.imshow("ji",img)
        # cv2.waitKey(0)
        # print(len(circles[0]))
        return len(circles[0])
    except:
        return -1


def Area_Count_dice_num(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    #binary=cv2.GaussianBlur(binary,(7, 7),5 )
    #binary = cv2.GaussianBlur(binary, (5, 5), 0)
    #cv2.imshow("x", binary)
    binary = cv2.Canny(binary, threshold1=30, threshold2=255)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 輪廓檢測函數
    count = 0
    for cont in contours:
        ares = cv2.contourArea(cont)  # 計算包圍性狀的面積
        if ares < 34:  # 過濾面積小於34的形狀
            continue
        count += 1  # 總體計數加1
    #print("dice_num   "+str(count))
    return count




def yinyun_num(img):
    binary = cv2.GaussianBlur(img, (3, 3), 0)
    kernel = np.ones((3, 3), np.uint8)
    dilation = cv2.dilate(img, kernel, iterations=1)
    erosion = cv2.erode(dilation, kernel, iterations=1)
    hsv = cv2.cvtColor(erosion, cv2.COLOR_BGR2HSV)
    l_g = np.array([101, 42, 0])  # lower green value
    u_g = np.array([222, 255, 174])
    mask = cv2.inRange(hsv, l_g, u_g)
    res = cv2.bitwise_and(erosion, erosion, mask=mask)
    binary = cv2.Canny(res, threshold1=5, threshold2=40)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 輪廓檢測函數
    count = 0
    for cont in contours:
        ares = cv2.contourArea(cont)  # 計算包圍性狀的面積
        if ares < 35 or ares > 100:  # 過濾面積小於10的形狀
            continue
        count += 1  # 總體計數加1
    # print(count)
    # cv2.imshow("img", binary)
    # cv2.imshow("ori", img)
    # cv2.waitKey(0)
    return count


def dector_summon_or_bubble(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    l_g = np.array([66, 111, 46])  # lower green value
    u_g = np.array([77, 255, 255])
    mask = cv2.inRange(hsv, l_g, u_g)
    res = cv2.bitwise_and(img, img, mask=mask)
    binary = cv2.Canny(res, threshold1=5, threshold2=40)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 輪廓檢測函數
    count = 0
    for cont in contours:
        ares = cv2.contourArea(cont)  # 計算包圍性狀的面積
        # print(ares)
        if ares < 35 or ares > 100:  # 過濾面積小於10的形狀
            continue
        count += 1  # 總體計數加1
    if (count > 0):
        return 6
    else:
        return 8


def jocker_num(img):
    try:
        can = cv2.resize(img, (240, 240))
        can = cv2.Canny(can, threshold1=0, threshold2=240)
        kernel = np.ones((9, 9), np.uint8)
        can = cv2.dilate(can, kernel, iterations=1)
        kernel = np.ones((5, 5), np.uint8)
        erosion = cv2.erode(can, kernel, iterations=1)
        # cv2.imshow('123',erosion)
        # cv2.waitKey(0)
        circles = cv2.HoughCircles(erosion, cv2.HOUGH_GRADIENT, 1, 50, param1=2, param2=8, minRadius=20, maxRadius=30)
        circles = np.uint16(np.around(circles))
        #print(len(circles[0]))
        return len(circles[0])
    except:
        pass

def mimic_num(img):
    #cv2.imshow("ori", img)
    can = cv2.resize(img, (240, 240))
    can = cv2.Canny(can, threshold1=0, threshold2=120)
    kernel = np.ones((7, 7), np.uint8)
    dilation = cv2.dilate(can, kernel, iterations=1)
    
    circles = cv2.HoughCircles(dilation, cv2.HOUGH_GRADIENT, 4, 50, param1=80, param2=80, minRadius=30, maxRadius=80)
    circles = np.uint16(np.around(circles))

    return len(circles[0])


# joker_and_mimic_num(img)
'''for i in range(0,3):
    for j in range(0,5):
        pointx=j*62+120
        pointy=i*60+530 
        #img_src = cv2.imread(pic, cv2.IMREAD_GRAYSCALE)
        img = cv2.imread(pic)[pointy+13:pointy+50,pointx+5:pointx+48] 
        #jocker_num(img)
        #mimic_num(img)
        dice_num(img)'''
# yinyun_num(img)
# dector_summon_or_bubble(img)

# yinyun_num(img)
dicenames = ['mimic',
                 'jocker',
                 'assassin',
                 'summon',
                 'bubble'
                 ]
       
def dice_num(img,mode, type=-1):
    if(mode=='sup'):
        try:
            if (type == 0 or type == 1 ):
                #print('jocker')
                count = jocker_num(img)
            else :
                count = Area_Count_dice_num(img)
            

                #count_HoughCircles = HoughCircles_Count_dice_num(img)
                #if (count_area == count_HoughCircles):
                #    count = count_area
                #else:
                #    count = count_HoughCircles
            #print(count)
            return count, type
        except Exception as err:
            print(err)
            return -1, type
    else:
        try:
            if (type == 2):
                count = jocker_num(img)
            elif(type==1):
                count = yinyun_num(img)
            else :
                count = Area_Count_dice_num(img)
                #count_HoughCircles = HoughCircles_Count_dice_num(img)
                #if (count_area == count_HoughCircles):
                #    count = count_area
                #else:
                #    count = count_HoughCircles
            #print(count)
            return count, type
        except Exception as err:
            print(err)
            return -1, type

def morphology_operations(img):
    morph_operator = 2
    morph_size = 1
    morph_elem = cv2.MORPH_RECT
    val_type = 1
    element = cv2.getStructuringElement(morph_elem, (2*morph_size + 1, 2*morph_size+1), (morph_size, morph_size))
    morph_op_dic = {0: cv2.MORPH_OPEN, 1: cv2.MORPH_CLOSE, 2: cv2.MORPH_GRADIENT, 3: cv2.MORPH_TOPHAT, 4: cv2.MORPH_BLACKHAT}
    operation = morph_op_dic[morph_operator]
    dst = cv2.morphologyEx(img, operation, element)
    #grayImg = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(dst, 110, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow('123', binary)
if __name__ == '__main__':
    pic = r'D:\dice_py\train\1111.jpg'
    for i in range(0, 3):
        for j in range(0, 5):
            pointx = j * 62 + 120
            pointy = int(i * 61 )+ 482
            img = cv2.imread(pic)[pointy + 13:pointy + 49, pointx + 5:pointx + 48]
            morphology_operations(img)
            #dice_num(img,'sup',0)
            #print(dice_num(img,'sup',3), end='  ')
            img=cv2.resize(img, (240, 240))
            cv2.imshow('3',img)
            cv2.waitKey(0)
        print()


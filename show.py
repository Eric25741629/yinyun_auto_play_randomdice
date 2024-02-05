import cv2
import numpy as np
class show():
    def __init__(self):
        pass
    
    def run(self, list1):
        # 合併圖片
        # 創建一個空白圖片
        # list1為一個opencv的二維陣列
        img_row_list = []
        for i in range(len(list1)):
            img = list1[i][0]
            for j in range(1, len(list1[i])):
                # 連接圖片
                img = np.hstack((img, list1[i][j]))
            # 將每一行的圖片添加到列表中
            img_row_list.append(img)
        # 圖片換行
        origin_img = img_row_list[0]
        for i in range(1, len(img_row_list)):
            origin_img = np.vstack((origin_img, img_row_list[i]))
        cv2.imshow('img', origin_img)
        cv2.waitKey(1)
        return origin_img
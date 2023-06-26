import os
import time

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image

from model import Classifier

dicenames1 = ['growning', 'yinyun', 'jocker', 'sup', 'broken_growning', ]

dicenames2 = ['mimic','jocker','assassin','summon','bubble']
label_name = ['assassin1', 'assassin2', 'assassin3', 'assassin4', 'assassin5', 'assassin6', 'assassin7', 'background', 'broken_growning1', 'broken_growning2', 
'broken_growning3', 'broken_growning4', 'broken_growning5', 'broken_growning6', 'broken_growning7', 'bubble1', 'bubble2', 'bubble3', 'bubble4', 'bubble5', 'bubble6', 'bubble7', 'growning1', 'growning2', 'growning3', 'growning4', 'growning5', 'growning6', 'growning7', 'jocker1', 'jocker2', 'jocker3', 'jocker4', 'jocker5', 'jocker6', 'jocker7', 'mimic1', 'mimic2', 'mimic3', 'mimic4', 'mimic5', 'mimic6', 'mimic7', 'summon1', 'summon2', 'summon3', 'summon4', 'summon5', 'summon6', 'summon7', 'sup1', 'sup2', 'sup3', 'sup4', 'sup5', 'sup6', 'sup7', 'yinyun1', 'yinyun2', 'yinyun3', 'yinyun4', 'yinyun5', 'yinyun6', 'yinyun7']

def predict_single_image(img,model):
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    
    img = transform(img)
    img = img.unsqueeze(0)
    
    with torch.no_grad():
        num = model(img)
        _, predicted_index = torch.max(num, 1)
        #如果準確率大於0.9，就返回預測結果，否則返回-1
        if torch.max(num)>0.9:
            return predicted_index.item()
        else:
            return -1



def detect_single_dice(img2,mode, model):
    if model:
        try:
            predictedtype_num=predict_single_image(img2,model)
            # print(predictedtype_num)
            #儲存圖片至data資料夾的預測結果資料夾中
            #檢查路徑是否存在，不存在則創建
            if predictedtype_num!=-1:
                if (predictedtype_num==7):
                    return 999 ,999
                else: 
                    try:
                        if mode == 'sup':
                            dice_num = int(label_name[predictedtype_num][-1])
                            dicetype = dicenames2.index(label_name[predictedtype_num][:-1])
                        else:
                            dice_num = int(label_name[predictedtype_num][-1])
                            dicetype = dicenames1.index(label_name[predictedtype_num][:-1])
                        # return 999 ,999
                        return dice_num, dicetype
                    except Exception as e:
                        print(e)
                        return 999 ,999

        except Exception as e:
            # pass
            print(e)
            return 999 ,999
                # if (dice//7==5):


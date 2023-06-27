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

def predict_images(images, model):
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    
    batch = torch.stack([transform(img) for img in images])
    
    with torch.no_grad():
        batch = batch.to('cuda')
        output = model(batch)
        _, predicted_indices = torch.max(output, 1)
        probabilities = torch.softmax(output, 1)
        predicted_indices = predicted_indices.cpu().tolist()
        probabilities = probabilities.cpu().tolist()
    
    predictions = []
    for i, index in enumerate(predicted_indices):
        if torch.max(torch.tensor(probabilities[i])) > 0.9:
            predictions.append(index)
        else:
            predictions.append(-1)
    
    return predictions




def detect_dice(images, mode, model):
    if model:
        try:
            predictions = predict_images(images, model)
            
            results = []
            for prediction in predictions:
                if prediction != -1:
                    if prediction == 7:
                        results.append((999, 999))
                    else:
                        try:
                            if mode == 'sup':
                                dice_num = int(label_name[prediction][-1])
                                dicetype = dicenames2.index(label_name[prediction][:-1])
                            else:
                                dice_num = int(label_name[prediction][-1])
                                dicetype = dicenames1.index(label_name[prediction][:-1])
                            
                            results.append((dice_num, dicetype))
                        except Exception as e:
                            print(e)
                            results.append((999, 999))
                
            return results
        except Exception as e:
            print(e)
    
    return []



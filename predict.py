import torch
import torchvision.transforms as transforms
import os

dicenames1 = ['growning', 'yinyun', 'jocker', 'sup', 'broken_growning', ]

dicenames2 = ['mimic', 'jocker', 'assassin', 'summon', 'bubble']
label_name = ['assassin1', 'assassin2', 'assassin3', 'assassin4', 'assassin5', 'assassin6', 'assassin7', 'background', 'broken_growning1', 'broken_growning2',
              'broken_growning3', 'broken_growning4', 'broken_growning5', 'broken_growning6', 'broken_growning7', 'bubble1', 'bubble2', 'bubble3', 'bubble4', 'bubble5', 'bubble6', 'bubble7', 'growning1', 'growning2', 'growning3', 'growning4', 'growning5', 'growning6', 'growning7', 'jocker1', 'jocker2', 'jocker3', 'jocker4', 'jocker5', 'jocker6', 'jocker7', 'mimic1', 'mimic2', 'mimic3', 'mimic4', 'mimic5', 'mimic6', 'mimic7', 'summon1', 'summon2', 'summon3', 'summon4', 'summon5', 'summon6', 'summon7', 'sup1', 'sup2', 'sup3', 'sup4', 'sup5', 'sup6', 'sup7', 'yinyun1', 'yinyun2', 'yinyun3', 'yinyun4', 'yinyun5', 'yinyun6', 'yinyun7']
def readfiles_recursive(path):
    image_files = []
    
    # 遍历当前目录下的所有文件和文件夹
    for root, dirs, files in os.walk(path):
        for file in files:
            # 判断文件是否以 .jpg 结尾
            if file.endswith('.jpg'):
                # 获取文件的绝对路径，并添加到列表
                file_path = os.path.join(root, file)
                image_files.append(file_path)
    
    return image_files

def predict_images(images, model):
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])

    batch = torch.stack([transform(img) for img in images])

    with torch.no_grad():
        if torch.cuda.is_available():
            batch = batch.to('cuda')
        output = model(batch)
        _, predicted_indices = torch.max(output, 1)
        probabilities = torch.softmax(output, 1)
        if torch.cuda.is_available():
            predicted_indices = predicted_indices.cpu().tolist()
            probabilities = probabilities.cpu().tolist()
        # else:
        # predicted_indices = predicted_indices.tolist()
        # probabilities = probabilities.tolist()
        # predicted_indices = predicted_indices.cpu().tolist()
        # probabilities = probabilities.cpu().tolist()
    predictions = []
    for i, index in enumerate(predicted_indices):
        if torch.max(torch.tensor(probabilities[i])) > 0.99:
            predictions.append(index)
        else:
            predictions.append(-1)

    return predictions
import cv2
from PIL import Image
def move(path,newpath,label):
    if not os.path.exists(newpath+'/'+label):
        os.makedirs(newpath+'/'+label)
    
    try:
        # print(path,newpath+'/'+label+'/'+path.split('/')[-1])
        os.rename(path,newpath+'/'+label+'/'+path.split('\\')[-1])
    except Exception as err:
        print(err)
        pass
def predict_batch(image_paths, model, newpath):
    images = []
    try:
        for path in image_paths:
            img = cv2.imread(path)
            img = cv2.resize(img, (62, 62))
            img = Image.fromarray(img)
            images.append(img)
    except Exception as err:
        print(err)
        print(path)
    results = predict_images(images, model)

    for i, result in enumerate(results):
        try:
            if result == -1:
                move(image_paths[i], newpath, 'error')
            else:
                move(image_paths[i], newpath, label_name[result])
        except Exception as err:
            print(err)
            continue

def predict(path, model, newpath):
    image_dir = readfiles_recursive(path)
    
    # 处理100张图片为一批次
    batch_size = 1000
    for i in range(0, len(image_dir), batch_size):
        batch_paths = image_dir[i:i+batch_size]
        predict_batch(batch_paths, model, newpath)
import torchvision.models as models
import torch.nn as nn
if "__main__" == __name__:
    dicemodel = models.mobilenet_v3_large()
    num_classes = 64
    dicemodel.classifier[-1] = nn.Linear(
        in_features=dicemodel.classifier[-1].in_features, out_features=num_classes)
    state_dict = torch.load(r'V3model_epoch_8.pth',
                            map_location=torch.device('cuda'))
    dicemodel.load_state_dict(state_dict)
    dicemodel.eval().cuda()
    predict(r'C:\python_dev\yinyun_auto_play_randomdice\NEW_RECORD\new/',dicemodel,r'C:\python_dev\yinyun_auto_play_randomdice\NEW_RECORD/99%/')
import torch
import torch.nn as nn
import torchvision.models as models
from ultralytics import YOLO


def load_model():
    # dicetype_num_model = models.mobilenet_v3_large(
    #     weights=True, progress=True)
    dicetype_num_model = models.mobilenet_v3_large()
    num_classes = 64
    dicetype_num_model.classifier[-1] = nn.Linear(
        in_features=dicetype_num_model.classifier[-1].in_features, out_features=num_classes)
    state_dict = torch.load(r'V3model_epoch_8.pth',
                            map_location=torch.device('cpu'))
    dicetype_num_model.load_state_dict(state_dict)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dicetype_num_model = dicetype_num_model.to(device)
    dicetype_num_model.eval()
    model = YOLO(
        r'C:\Users\eric\Downloads\Compressed\yolov8\runs\detect\train\weights\best.pt')

    return dicetype_num_model, model

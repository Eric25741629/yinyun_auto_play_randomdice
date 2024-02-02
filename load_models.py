import torch
import torch.nn as nn
import torchvision.models as models
from ultralytics import YOLO
import easyocr
class AI_model():
    def __init__(self):
        self.dicemodel=None
        self.wavemodel=None
        self.reader=None
        self.load_model()
    def load_model(self):
        # dicemodel = models.mobilenet_v3_large(
        #     weights=True, progress=True)
        self.dicemodel = models.mobilenet_v3_large()
        num_classes = 64
        self.dicemodel.classifier[-1] = nn.Linear(
            in_features=self.dicemodel.classifier[-1].in_features, out_features=num_classes)
        state_dict = torch.load(r'V3model_epoch_8.pth',
                                map_location=torch.device('cpu'))
        self.dicemodel.load_state_dict(state_dict)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.dicemodel = self.dicemodel.to(device)
        self.dicemodel.eval()
        self.wavemodel = YOLO(
            r"wave.pt")
        self.reader = easyocr.Reader(['ch_tra'], gpu=True)
        

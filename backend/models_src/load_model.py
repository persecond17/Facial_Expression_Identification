import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from skimage.io import imread
from PIL import Image, ImageOps
from skimage.transform import resize


def read_img_url(url):
    """
    Reads the image url and convert to a gray-scale matrix representation of the image.
    """
    image = Image.open(url)
    image = ImageOps.grayscale(image)

    # Resize the image to 50% of its original size
    resized_image = image.resize((48, 48))
    resized_image_mat = torch.from_numpy(np.array(resized_image.getdata()).reshape((48, 48))).type(torch.float32)

    assert resized_image_mat.shape == (48, 48)

    return resized_image_mat


def predict_core(imgs, model_path, ModelClass, idx_to_label):
    """
    Predicts class of facial expression of the images given the deep learning model.
    """
    model = ModelClass()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    imgs = imgs.view(-1, 1, 48, 48)
    pred = model(imgs)
    _, pred_label = torch.max(pred, 1)

    return np.array([idx_to_label[idx] for idx in pred_label])


class FER_CNN(nn.Module):
    def __init__(self):
        super(FER_CNN, self).__init__()

        # Conv block 1
        self.conv1 = nn.Conv2d(in_channels=1, 
                               out_channels=64, 
                               kernel_size=(3,3), 
                               padding='same')
        self.bn1 = nn.BatchNorm2d(num_features=64)
        
        # Conv block 2
        self.conv2 = nn.Conv2d(in_channels=64, 
                               out_channels=128, 
                               kernel_size=(5,5), 
                               padding='same')
        self.bn2 = nn.BatchNorm2d(num_features=128)
        
        # Conv block 3
        self.conv3 = nn.Conv2d(in_channels=128, 
                               out_channels=512, 
                               kernel_size=(3,3), 
                               padding='same')
        self.bn3 = nn.BatchNorm2d(num_features=512)
        
        # Conv block 4
        self.conv4 = nn.Conv2d(in_channels=512, 
                               out_channels=512, 
                               kernel_size=(3,3), 
                               padding='same')
        self.bn4 = nn.BatchNorm2d(num_features=512)
        
        # fully connected layer 1
        self.fc1 = nn.Linear(in_features=512*3*3, out_features=256)
        self.bn_fc1 = nn.BatchNorm1d(num_features=256)

        # fully connected layer 2
        self.fc2 = nn.Linear(in_features=256, out_features=512)
        self.bn_fc2 = nn.BatchNorm1d(num_features=512)

        # fully connected layer 3
        self.fc3 = nn.Linear(in_features=512, out_features=7)

        # max pooling layer
        self.max_pool = nn.MaxPool2d(kernel_size=(2,2))

        # activation
        self.relu = nn.ReLU()

        # dropout
        self.dropout = nn.Dropout(p=0.25)

    def forward(self, x):
        # conv1
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.max_pool(x)
        x = self.dropout(x)

        # conv2
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.max_pool(x)
        x = self.dropout(x)

        # conv3
        x = self.conv3(x)
        x = self.bn3(x)
        x = self.relu(x)
        x = self.max_pool(x)
        x = self.dropout(x)

        # conv4
        x = self.conv4(x)
        x = self.bn4(x)
        x = self.relu(x)
        x = self.max_pool(x)
        x = self.dropout(x)

        # flatten x
        x = x.view(-1, 512*3*3)

        # fc1
        x = self.fc1(x)
        x = self.bn_fc1(x)
        x = self.relu(x)
        x = self.dropout(x)

        # fc2
        x = self.fc2(x)
        x = self.bn_fc2(x)
        x = self.relu(x)
        x = self.dropout(x)

        # fc3
        x = self.fc3(x)

        return x
        
        
def predict(model_path, url):
    img_tensor = read_img_url(url)
    ModelClass = FER_CNN
    idx_to_label = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    result = predict_core(img_tensor, model_path, ModelClass, idx_to_label)[0]
    return result
    


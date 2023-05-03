import numpy as np
import pandas as pd
import os
import torch
import torch.nn as nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from skimage.io import imread

from config import *


# load training set
train = []

for root, dirs, files in os.walk(TRAINING_DIR):
    for name in files:
        if not (name.endswith('.jpg') or name.endswith('.png')):
            continue
        class_ = root.split('/')[-1]
        img_path = os.path.join(root, name)
        train.append([img_path, class_])

# load validation and test set
val = []
test = []

for root, dirs, files in os.walk(VAL_TEST_DIR):
    for name in files:
        if not (name.endswith('.jpg') or name.endswith('.png')):
            continue
        class_ = root.split('/')[-1]
        img_path = os.path.join(root, name)

        if name.startswith('PrivateTest'):
            val.append([img_path, class_])
        elif name.startswith('PublicTest'):
            test.append([img_path, class_])

# batching
batch_size = 50
train_loader = DataLoader(dataset=train, shuffle=True, batch_size=batch_size)
val_loader = DataLoader(dataset=val, shuffle=True, batch_size=batch_size)
test_loader = DataLoader(dataset=test, shuffle=True, batch_size=batch_size)

# build model architecture
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

# training loop
model = FER_CNN()

lr = 0.001
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=lr)

idx_to_label = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
num_batches = len(train_loader)
num_epochs = 80

model.train()

for epoch in range(num_epochs):
    for i, (img_path_batch, label_batch) in enumerate(train_loader):
        imgs = np.array([imread(path) for path in img_path_batch]).reshape(len(img_path_batch), 1, 48, 48)
        imgs = torch.from_numpy(imgs).type(torch.float32)
        try:
            labels = np.array([idx_to_label.index(class_) for class_ in label_batch])
        except ValueError as e:
            print('Invalid class label detected.')
            break
        labels = torch.from_numpy(labels).type(torch.int64)

        # print(imgs.shape, labels.shape)
        # break
        
        pred = model(imgs)
        loss = criterion(pred, labels)

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if (i + 1) % int(num_batches / 5) == 0:
            print(f'epoch {epoch + 1}/{num_epochs} step {i + 1}/{num_batches}: loss = {loss}')

torch.save(model.state_dict(), MODEL_PATH_v03)

# evaluate training accuracy
model.eval()
with torch.no_grad():
    n_correct = 0
    n_samples = 0
    n_class_correct = [0 for i in range(7)]
    n_class_samples = [0 for i in range(7)]
    for img_path_batch, label_batch in train_loader:
        imgs = np.array([imread(path) for path in img_path_batch]).reshape(len(img_path_batch), 1, 48, 48)
        imgs = torch.from_numpy(imgs).type(torch.float32)
        try:
            labels = np.array([idx_to_label.index(class_) for class_ in label_batch])
        except ValueError as e:
            print('Invalid class label detected.')
            break
        labels = torch.from_numpy(labels).type(torch.int64)

        pred = model(imgs)
        _, pred_label = torch.max(pred, 1)
        n_samples += labels.size(0)
        n_correct += (pred_label == labels).sum().item()

        for i in range(len(img_path_batch)):
            label = labels[i]
            pred = pred_label[i]
            if (label == pred):
                n_class_correct[label] += 1
            n_class_samples[label] += 1
    
    acc = 100.0 * n_correct / n_samples
    print('Training data:')
    print(f'Overall Accuracy: {acc} %')

    for i in range(7):
        acc = 100.0 * n_class_correct[i] / n_class_samples[i]
        print(f'Accuracy of {idx_to_label[i]}: {acc} %')

# evaluate validation accuracy
with torch.no_grad():
    n_correct = 0
    n_samples = 0
    n_class_correct = [0 for i in range(7)]
    n_class_samples = [0 for i in range(7)]
    for img_path_batch, label_batch in val_loader:
        imgs = np.array([imread(path) for path in img_path_batch]).reshape(len(img_path_batch), 1, 48, 48)
        imgs = torch.from_numpy(imgs).type(torch.float32)
        try:
            labels = np.array([idx_to_label.index(class_) for class_ in label_batch])
        except ValueError as e:
            print('Invalid class label detected.')
            break
        labels = torch.from_numpy(labels).type(torch.int64)

        pred = model(imgs)
        _, pred_label = torch.max(pred, 1)
        n_samples += labels.size(0)
        n_correct += (pred_label == labels).sum().item()

        for i in range(len(img_path_batch)):
            label = labels[i]
            pred = pred_label[i]
            if (label == pred):
                n_class_correct[label] += 1
            n_class_samples[label] += 1
    
    acc = 100.0 * n_correct / n_samples
    print('Validation data:')
    print(f'Overall Accuracy: {acc} %')

    for i in range(7):
        acc = 100.0 * n_class_correct[i] / n_class_samples[i]
        print(f'Accuracy of {idx_to_label[i]}: {acc} %')

# evaluate test accuracy
with torch.no_grad():
    n_correct = 0
    n_samples = 0
    n_class_correct = [0 for i in range(7)]
    n_class_samples = [0 for i in range(7)]
    for img_path_batch, label_batch in test_loader:
        imgs = np.array([imread(path) for path in img_path_batch]).reshape(len(img_path_batch), 1, 48, 48)
        imgs = torch.from_numpy(imgs).type(torch.float32)
        try:
            labels = np.array([idx_to_label.index(class_) for class_ in label_batch])
        except ValueError as e:
            print('Invalid class label detected.')
            break
        labels = torch.from_numpy(labels).type(torch.int64)

        pred = model(imgs)
        _, pred_label = torch.max(pred, 1)
        n_samples += labels.size(0)
        n_correct += (pred_label == labels).sum().item()

        for i in range(len(img_path_batch)):
            label = labels[i]
            pred = pred_label[i]
            if (label == pred):
                n_class_correct[label] += 1
            n_class_samples[label] += 1
    
    acc = 100.0 * n_correct / n_samples
    print('Test data:')
    print(f'Overall Accuracy: {acc} %')

    for i in range(7):
        acc = 100.0 * n_class_correct[i] / n_class_samples[i]
        print(f'Accuracy of {idx_to_label[i]}: {acc} %')
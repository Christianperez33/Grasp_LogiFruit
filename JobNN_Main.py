import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import os
import torchvision
from torchvision import datasets
from torch.nn.modules.utils import _pair, _quadruple
from prettytable import PrettyTable
from JobSchedule_NN import JBNN, count_parameters, JBNN_ADD

path_conv_tr="./TrainingJBNN/train_conv.npy"
path_data_tr="./TrainingJBNN/train_data.npy"
path_label_tr="./TrainingJBNN/train_label.npy"
batch=1844

#TrainDataset image part
train_conv_dataset = TensorDataset(torch.from_numpy(np.load(path_conv_tr)))
trainloader_conv = torch.utils.data.DataLoader(train_conv_dataset, batch_size=batch,shuffle=False, num_workers=2)
#TrainDataset tensor appended to fullyconnected part
train_data_dataset = TensorDataset(torch.from_numpy(np.load(path_data_tr)))
trainloader_data = torch.utils.data.DataLoader(train_data_dataset, batch_size=batch,shuffle=False, num_workers=2)
#TrainDataset labels part
train_label_dataset = TensorDataset(torch.from_numpy(np.load(path_label_tr)))
trainloader_label = torch.utils.data.DataLoader(train_label_dataset, batch_size=batch,shuffle=False, num_workers=2)

#x1=torch.randn(5,14,16,16)
#x2=torch.randint(0,2,(5,14))
#target=torch.randint(0,14,(5,))

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = JBNN_ADD(in_channels=14, num_classes=14)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

#print(model(x1,x2).shape)
#count_parameters(model)

#running_loss = 0.0
#optimizer.zero_grad()
#outputs = model(x1,x2)
#loss = criterion(outputs, target)
#loss.backward()
#optimizer.step()


#running_loss += loss.item()
#print('loss: %.3f' %
#    (running_loss))
#running_loss = 0.0

for epoch in range(2):

    running_loss = 0.0
    for conv_t,data_t,label_t in zip(enumerate(trainloader_conv,0),enumerate(trainloader_data,0),enumerate(trainloader_label,0)):
        optimizer.zero_grad()
        
        t,conv=conv_t
        t,data=data_t
        t,label=label_t

        outputs = model(conv[0],data[0])
        loss = criterion(outputs, label[0])
        loss.backward()
        optimizer.step()

        running_loss+=loss.item()
        print('[epoch:%2d, num_batch:%2d] loss: %.3f' % (epoch + 1, t + 1, running_loss))
        running_loss = 0.0
    #print("Epoch: "+str(epoch)+" Loss: "+str(running_loss))

print("Training complete")
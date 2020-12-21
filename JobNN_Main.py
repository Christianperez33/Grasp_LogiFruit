import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
import os
from torch.nn.modules.utils import _pair, _quadruple
from prettytable import PrettyTable
from JobSchedule_NN import JBNN, count_parameters, JBNN_ADD


device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = JBNN_ADD(in_channels=14, num_classes=14)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)


x1=torch.randn(5,14,8,16)
x2=torch.randint(0,2,(5,16))
target=torch.randint(0,14,(5,))
#y1=torch.nn.functional.one_hot(target, num_classes=14)
#print(torch.max(y1, 1)[1])
print(model(x1,x2).shape)
count_parameters(model)

running_loss = 0.0
optimizer.zero_grad()
outputs = model(x1,x2)
loss = criterion(outputs, target)
loss.backward()
optimizer.step()


running_loss += loss.item()
print('loss: %.3f' %
    (running_loss))
running_loss = 0.0


import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
import os
from torch.nn.modules.utils import _pair, _quadruple
from prettytable import PrettyTable
from JobSchedule_NN import JBNN, count_parameters


device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = JBNN(in_channels=14, num_classes=14)
x1=torch.randn(1,14,8,16)
print(model(x1).shape)
count_parameters(model)

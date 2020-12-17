import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
import os
from torch.nn.modules.utils import _pair, _quadruple
from prettytable import PrettyTable


def count_parameters(model):
    table = PrettyTable(["Modules", "Parameters"])
    total_params = 0
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad: continue
        param = parameter.numel()
        table.add_row([name, param])
        total_params+=param
    print(table)
    print(f"Total Trainable Params: {total_params}")
    return total_params


#Conv Part
JBNN_types = {
    'JBNN1' : [28, 28, 'P', 56, 56, 'P', 112, 112, 'P'],
    'JBNN2' : [28, 28, 28, 'P', 56, 56, 56, 'P', 112, 112, 112, 'P'],
    'JBNN3' : [64, 64, 'P', 128, 128, 'P', 256, 256, 'P']
}



class JBNN(nn.Module):
    def __init__(self, in_channels=14, num_classes=14):
        super(JBNN, self).__init__()
        self.in_channels = in_channels
        self.conv_layers = self.create_conv_layers(JBNN_types['JBNN1'])

        self.fcs = nn.Sequential(
            nn.Linear(112*1*16, 512),
            #nn.ReLU(),
            nn.Sigmoid(),
            nn.Linear(512,512),
            #nn.ReLU(),
            nn.Sigmoid(),
            nn.Linear(512,num_classes)
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fcs(x)
        return x

    def create_conv_layers(self, architecture):
        layers=[]
        in_channels = self.in_channels

        for x in architecture:
            if type(x) == int:
                out_channels = x

                layers += [nn.Conv2d(in_channels=in_channels, out_channels=out_channels, 
                                        kernel_size=(3,3), stride=(1,1), padding=(1,1)),
                                    nn.BatchNorm2d(x),
                                    #nn.ReLU()
                                    nn.Sigmoid()]
                in_channels = x
            elif x == 'P':
                #layers += [nn.MaxPool2d(kernel_size=(2,2), stride=(2,2))]
                #layers += [MedianPool2d()]
                layers += [nn.AvgPool2d(kernel_size=(2,1), stride=(2,1))]
        
        return nn.Sequential(*layers)




device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = JBNN(in_channels=14, num_classes=14)
x1=torch.randn(1,14,8,16)
print(model(x1).shape)
count_parameters(model)

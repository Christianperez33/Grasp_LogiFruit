import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import os
from torch.nn.modules.utils import _pair, _quadruple
from prettytable import PrettyTable
from JobSchedule_NN import count_parameters, JBNN_ADD
import matplotlib.pyplot as plt

path_conv_tr="./TrainingJBNN/train_conv.npy"
path_data_tr="./TrainingJBNN/train_data.npy"
path_label_tr="./TrainingJBNN/train_label.npy"

path_conv_ts="./TestJBNN/test_conv.npy"
path_data_ts="./TestJBNN/test_data.npy"
path_label_ts="./TestJBNN/test_label.npy"

batch=1844
numEpochs=100

#TrainDataset image part
train_conv_dataset = TensorDataset(torch.from_numpy(np.load(path_conv_tr)))
trainloader_conv = torch.utils.data.DataLoader(train_conv_dataset, batch_size=batch,shuffle=False, num_workers=4)
#TrainDataset tensor appended to fullyconnected part
train_data_dataset = TensorDataset(torch.from_numpy(np.load(path_data_tr)))
trainloader_data = torch.utils.data.DataLoader(train_data_dataset, batch_size=batch,shuffle=False, num_workers=4)
#TrainDataset labels part
train_label_dataset = TensorDataset(torch.from_numpy(np.load(path_label_tr)))
trainloader_label = torch.utils.data.DataLoader(train_label_dataset, batch_size=batch,shuffle=False, num_workers=4)


#TestDataset image part
test_conv_dataset = TensorDataset(torch.from_numpy(np.load(path_conv_ts)))
testloader_conv = torch.utils.data.DataLoader(test_conv_dataset, batch_size=batch,shuffle=False, num_workers=4)
#TestDataset tensor appended to fullyconnected part
test_data_dataset = TensorDataset(torch.from_numpy(np.load(path_data_ts)))
testloader_data = torch.utils.data.DataLoader(test_data_dataset, batch_size=batch,shuffle=False, num_workers=4)
#TestDataset labels part
test_label_dataset = TensorDataset(torch.from_numpy(np.load(path_label_ts)))
testloader_label = torch.utils.data.DataLoader(test_label_dataset, batch_size=batch,shuffle=False, num_workers=4)


#device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = JBNN_ADD(in_channels=14, num_classes=14)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)


train_losses, test_losses = [], []
for epoch in range(numEpochs):
    if epoch%5==0:
        torch.save(model.state_dict(), "./Models/last_ep_model")

    #Training
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

        print("Epoch: "+str(epoch+1)+" ; Batch: "+str(t+1))

    train_losses.append(running_loss/len(trainloader_conv))
    
    #Validation
    test_loss = 0
    accuracy = 0
    model.eval()
    with torch.no_grad():
        for conv_t,data_t,label_t in zip(enumerate(testloader_conv,0),enumerate(testloader_data,0),enumerate(testloader_label,0)):
            t,conv=conv_t
            t,data=data_t
            t,label=label_t

            outputs = model(conv[0],data[0])
            loss = criterion(outputs, label[0])
            test_loss+=loss.item()
            
            ps = torch.exp(outputs)
            top_p, top_class = ps.topk(1, dim=1)
            equals = top_class == label[0].view(*top_class.shape)
            
            accuracy += torch.mean(equals.type(torch.FloatTensor)).item()
    

    test_losses.append(test_loss/len(testloader_conv)) 

    print(f"Epoch {epoch+1}.. "
    f"Train loss: {running_loss/len(trainloader_conv):.3f}.. "
    f"Test loss: {test_loss/len(testloader_conv):.3f}.. "
    f"Test accuracy: {accuracy/len(testloader_conv):.3f}")

    model.train()



print("Training complete")

plt.plot(train_losses, label='Training loss')
plt.plot(test_losses, label='Validation loss')
plt.legend(frameon=False)
plt.show()

torch.save(model.state_dict(), "./Models/100_ep_model")
import torch
import torchvision
import numpy as np
from cnn import CNN, PruneTool

transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor(), torchvision.transforms.Normalize((0.1307,), (0.3081,))])
trainset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
testset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True, num_workers=2)
testloader = torch.utils.data.DataLoader(testset, batch_size=64, shuffle=False, num_workers=2)

model = CNN() # 实例化模型对象
criterion = torch.nn.CrossEntropyLoss() # 定义交叉熵损失函数对象
optimizer = torch.optim.SGD(model.parameters(), lr=0.01) # 定义随机

# 原始
conv1 = model.conv1
conv2 = model.conv2

conv1_1, conv2_1, patch1 = PruneTool(conv1, conv2, list(range(32))).prune(list(range(16)))
model.conv1 = conv1_1
model.conv2 = conv2_1

epochs = 1 # 定义训练轮数
for epoch in range(epochs): # 遍历每一轮
    running_loss = 0.0 # 初始化累计损失为0
    for i, data in enumerate(trainloader): # 遍历每一个批次
        inputs, labels = data # 获取输入和标签
        optimizer.zero_grad() # 清零梯度缓存
        outputs = model(inputs) # 计算模型输出
        loss = criterion(outputs, labels) # 计算损失函数值
        loss.backward() # 反向传播梯度
        optimizer.step() # 更新模型参数

        running_loss += loss.item() # 累加损失值
        if i % 200 == 0: # 每200个批次打印一次平均损失值
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i, running_loss / 200))
            running_loss = 0.0
correct = 0 # 初始化正确预测数为0
total = 0 # 初始化总样本数为0
with torch.no_grad(): # 不需要计算梯度
    for data in testloader: # 遍历每一个批次
        images, labels = data # 获取输入和标签
        outputs = model(images) # 计算模型输出
        _, predicted = torch.max(outputs.data, 1) # 获取最大概率的类别作为预测结果
        total += labels.size(0) # 累加总样本数
        correct += (predicted == labels).sum().item() # 累加正确预测数
print('Accuracy of the network on the 10000 test images: %d %%' % (
    100 * correct / total)) 


conv1_2, conv2_2 = PruneTool(conv1_1, conv2_1, list(range(16))).recovery(patch1)
conv1_3, conv2_3, patch2 = PruneTool(conv1_2, conv2_2, list(range(32))).prune(list(range(16, 32)))
model.conv1 = conv1_3
model.conv2 = conv2_3
epochs = 1 # 定义训练轮数
for epoch in range(epochs): # 遍历每一轮
    running_loss = 0.0 # 初始化累计损失为0
    for i, data in enumerate(trainloader): # 遍历每一个批次
        inputs, labels = data # 获取输入和标签
        optimizer.zero_grad() # 清零梯度缓存
        outputs = model(inputs) # 计算模型输出
        loss = criterion(outputs, labels) # 计算损失函数值
        loss.backward() # 反向传播梯度
        optimizer.step() # 更新模型参数

        running_loss += loss.item() # 累加损失值
        if i % 200 == 0: # 每200个批次打印一次平均损失值
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i, running_loss / 200))
            running_loss = 0.0
correct = 0 # 初始化正确预测数为0
total = 0 # 初始化总样本数为0
with torch.no_grad(): # 不需要计算梯度
    for data in testloader: # 遍历每一个批次
        images, labels = data # 获取输入和标签
        outputs = model(images) # 计算模型输出
        _, predicted = torch.max(outputs.data, 1) # 获取最大概率的类别作为预测结果
        total += labels.size(0) # 累加总样本数
        correct += (predicted == labels).sum().item() # 累加正确预测数
print('Accuracy of the network on the 10000 test images: %d %%' % (
    100 * correct / total)) 


conv1_4, conv2_4 = PruneTool(conv1_3, conv2_3, list(range(16, 32))).recovery(patch2)
model.conv1 = conv1_4
model.conv2 = conv2_4

epochs = 1 # 定义训练轮数
for epoch in range(epochs): # 遍历每一轮
    running_loss = 0.0 # 初始化累计损失为0
    for i, data in enumerate(trainloader): # 遍历每一个批次
        inputs, labels = data # 获取输入和标签
        optimizer.zero_grad() # 清零梯度缓存
        outputs = model(inputs) # 计算模型输出
        loss = criterion(outputs, labels) # 计算损失函数值
        loss.backward() # 反向传播梯度
        optimizer.step() # 更新模型参数

        running_loss += loss.item() # 累加损失值
        if i % 200 == 0: # 每200个批次打印一次平均损失值
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i, running_loss / 200))
            running_loss = 0.0
correct = 0 # 初始化正确预测数为0
total = 0 # 初始化总样本数为0
with torch.no_grad(): # 不需要计算梯度
    for data in testloader: # 遍历每一个批次
        images, labels = data # 获取输入和标签
        outputs = model(images) # 计算模型输出
        _, predicted = torch.max(outputs.data, 1) # 获取最大概率的类别作为预测结果
        total += labels.size(0) # 累加总样本数
        correct += (predicted == labels).sum().item() # 累加正确预测数
print('Accuracy of the network on the 10000 test images: %d %%' % (
    100 * correct / total)) 


print('Finished Training')
import torch

class CNN(torch.nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = torch.nn.Conv2d(1, 32, 3) # 输入通道为1（灰度图），输出通道为32，卷积核大小为3x3
        self.conv2 = torch.nn.Conv2d(32, 64, 3) # 输入通道为32，输出通道为64，卷积核大小为3x3
        self.pool = torch.nn.MaxPool2d(2) # 最大池化层，池化核大小为2x2
        self.fc1 = torch.nn.Linear(64 * 5 * 5 , 128) # 全连接层，输入特征维度为64*5*5（根据前面的卷积和池化计算得到），输出特征维度为128
        self.fc2 = torch.nn.Linear(128 , 10) # 全连接层，输入特征维度为128，输出特征维度为10（类别数）
        self.softmax = torch.nn.Softmax(dim=1) # softmax层，在第一个维度上进行归一化

    def forward(self, x):
        x = self.pool(torch.nn.functional.relu(self.conv1(x))) # 第一个卷积-激活-池化操作
        x = self.pool(torch.nn.functional.relu(self.conv2(x))) # 第二个卷积-激活-池化操作
        x = x.view(-1 , 64 * 5 * 5 ) # 将二维特征图展平成一维向量
        x = torch.nn.functional.relu(self.fc1(x)) # 第一个全连接-激活操作
        x = self.fc2(x) # 第二个全连接操作
        x = self.softmax(x) # softmax操作
        return x

def prune_out_chan_cnn(conv: torch.nn.Conv2d, prune_index: list):
    pruned = conv.weight[prune_index] # 被剪枝的参数




    
    
    

class PrunedCNN(CNN):
    def __init__(self):
      super().__init__()
      self.conv1.weight
        
import torch


class CNN(torch.nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = torch.nn.Conv2d(1, 32, 3)  # 输入通道为1（灰度图），输出通道为32，卷积核大小为3x3
        self.conv2 = torch.nn.Conv2d(32, 64, 3)  # 输入通道为32，输出通道为64，卷积核大小为3x3
        self.pool = torch.nn.MaxPool2d(2)  # 最大池化层，池化核大小为2x2
        # 全连接层，输入特征维度为64*5*5（根据前面的卷积和池化计算得到），输出特征维度为128
        self.fc1 = torch.nn.Linear(64 * 5 * 5, 128)
        self.fc2 = torch.nn.Linear(128, 10)  # 全连接层，输入特征维度为128，输出特征维度为10（类别数）
        self.softmax = torch.nn.Softmax(dim=1)  # softmax层，在第一个维度上进行归一化

    def forward(self, x):
        x = self.pool(torch.nn.functional.relu(self.conv1(x)))  # 第一个卷积-激活-池化操作
        x = self.pool(torch.nn.functional.relu(self.conv2(x)))  # 第二个卷积-激活-池化操作
        x = x.view(-1, 64 * 5 * 5)  # 将二维特征图展平成一维向量
        x = torch.nn.functional.relu(self.fc1(x))  # 第一个全连接-激活操作
        x = self.fc2(x)  # 第二个全连接操作
        x = self.softmax(x)  # softmax操作
        return x


def prune_out_chan_cnn(conv: torch.nn.Conv2d, prune_index: torch.tensor):
    pruned = conv.weight[prune_index]  # 被剪枝的参数


class Patch():
    def __init__(self, start_ratio: float, end_ratio: float, out_prune_tensor: torch.tensor, in_prune_tensor: torch.tensor) -> None:
        """
        表示参数重要度在 [start_ratio, end_ratio) 的参数

        out_prune_tensor 表示当前层输出通道被剪下来的 tensor

        out_prune_shape 表示当前输出通道被剪下来的参数形状，比如对于 Linear(in=200, out=80) 剪去 50 个输出通道
        那么将会剪去一个 (50, 200) 的 tensor
        再比如对于一个 Conv2d(in=4, out=8, kernel_size=(3,3)) 剪去 2 个输出通道
        那么将会剪去一个 (4, 4, 3, 3) 的 tensor

        in_prune_shape 表示下一个层的输入通道被剪下来的参数形状
        """
        self.start_ratio = start_ratio
        self.end_ratio = end_ratio
        self.in_prune_shape = in_prune_tensor.shape
        self.out_prune_shape = out_prune_tensor.shape
        self.in_prune_tensor = in_prune_tensor
        self.out_prune_tensor = out_prune_tensor


class PrunedConv():
    def __init__(self, origin_layer: torch.nn.Conv2d, prune_weight: torch.tensor, prune_ratio: float = 0):
        self.origin_layer = origin_layer
        self.prune_weight = prune_weight  # 代表当前层所有输出通道的重要度
        # 代表当前层拥有 [0, current_weight) 重要度
        self.current_prune_ratio = prune_ratio

    def prune(self, next_layer: torch.nn.Module, target_prune_ratio: float, pic_size: float = -1) -> Patch:
        """
        pic_size 只有当下一层是 linear 的时候需要提供，目的是使用 pic_size 确定一个 conv 输出通道需要对应几个 linear 输入通道 
        """
        prune_index = self._get_prune_channel_index(target_prune_ratio)
        selected_index = list(set(range(self.origin_layer.weight.size(0))) - set(prune_index))

        prune_out = self._prune_current_layer(selected_index, prune_index)

        if isinstance(next_layer, torch.nn.Conv2d):
            prune_in = self._prune_next_cnn(
                next_layer, selected_index, prune_index)
        if isinstance(next_layer, torch.nn.Linear):
            if pic_size < 0:
                print("对于 conv2d -> linear 的剪枝，需要提供 conv2d 输出的特征图大小")
            prune_in = self._prune_next_linear(
                next_layer,  selected_index, prune_index, pic_size)
        return Patch(self.current_prune_ratio, target_prune_ratio, prune_out, prune_in)

    def _prune_current_layer(self, selected_index: list, prune_index: list) -> list:
        """
        返回剪枝的下标（在当前 weight 中的坐标，而不是原始模型）
        """
        pruned = torch.index_select(self.origin_layer.weight, 0, torch.tensor(prune_index))
        selected = torch.index_select(self.origin_layer.weight, 0, torch.tensor(selected_index))
        self.origin_layer.weight.data = selected
        return pruned

    def _prune_next_cnn(self, next_layer: torch.nn.Conv2d, selected_index: list, prune_index: list):
        pruned = torch.index_select(next_layer.weight, 1, torch.tensor(prune_index))
        selected = torch.index_select(next_layer.weight, 1, torch.tensor(selected_index))
        next_layer.weight.data = selected
        return pruned

    def _prune_next_linear(self, next_layer: torch.nn.Conv2d, selected_index: list, prune_index: list, pic_size: int):
        # 暂时未实现
        pass

    def _get_prune_channel_index(self, prune_ratio: float):
        """
        返回在 super.weight.data 中的通道下标，用于剪去通道
        """
        # 在原始模型中的下标
        current_layer_exist_channel = (
            self.prune_weight >= self.current_prune_ratio).nonzero().flatten()
        prune_channel = torch.logical_and(
            self.prune_weight >= self.current_prune_ratio, self.prune_weight < prune_ratio).nonzero().flatten()
        prune_channel_index = []
        cursor = 0
        for i in range(len(current_layer_exist_channel)):
            if current_layer_exist_channel[i] == prune_channel[cursor]:
                prune_channel_index.append(i)
                cursor += 1
                if cursor >= len(prune_channel_index):
                    break
        return prune_channel_index

    def get_shape(self):
        """
        返回当前层实际的的输入和输出通道数
        返回形式为 (输出通道数，输入通道数)
        """
        return (self.origin_layer.weight.size(0), self.origin_layer.weight.size(1))

if __name__ == "__main__":
    a = torch.nn.Conv2d(1, 4, 3)
    b = PrunedConv(a, torch.tensor([0, 0.25, 0.5, 1]))
    c = torch.nn.Conv2d(4,1,3)
    print(c.weight.data.shape)
    b.prune(c, 0.5)
    print(c.weight.data.shape)
    print(c)
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


class Patch():
    def __init__(self, prune_channel_id: list, out_prune_tensor: torch.tensor, in_prune_tensor: torch.tensor, out_prune_bias: torch.tensor, scale: int = 1) -> None:
        """
        prune_channel_id 表示当前补丁中包括哪些通道 id 的数据

        out_prune_tensor 表示当前层输出通道被剪下来的 tensor
        in_prune_tensor 表示下一层输入通道被剪下来的 tensor

        self.out_prune_shape 表示当前输出通道被剪下来的参数形状，比如对于 Linear(in=200, out=80) 剪去 50 个输出通道
        那么将会剪去一个 (50, 200) 的 tensor
        再比如对于一个 Conv2d(in=4, out=8, kernel_size=(3,3)) 剪去 2 个输出通道
        那么将会剪去一个 (4, 4, 3, 3) 的 tensor

        in_prune_shape 表示下一个层的输入通道被剪下来的参数形状

        scale: 表示一个输出通道对应下一层几个输入通道，如果是 conv->flatten->linear 那么 linear 的输入通道数应该为 conv 输出通道乘以输出通道特征图大小
        需要使用scale进行放缩
        """
        self.prune_channel_id = prune_channel_id
        # self.in_prune_shape = in_prune_tensor.shape
        # self.out_prune_shape = out_prune_tensor.shape
        self.in_prune_tensor = in_prune_tensor
        self.out_prune_tensor = out_prune_tensor
        self.out_prune_bias = out_prune_bias
        self.scale = scale


def scale_array(array, factor):
    # 创建一个空的 numpy 数组，长度是原数组乘以放缩因子
    result = torch.empty(len(array) * factor, dtype=int)
    # 遍历原数组中的每个元素
    for i, x in enumerate(array):
        # 将元素放缩成 factor 个连续的整数，并存入结果数组中
        result[i*factor:(i+1)*factor] = torch.arange(x*factor, (x+1)*factor)
    # 返回结果数组
    return result

# switchfl 的 layer，包装了 torch 的网络层


def select_index(tensor: torch.tensor, dim: int, index):
    return torch.index_select(tensor, dim, torch.tensor(index))


def create_layer(origin_layer: torch.nn.Module, weight: torch.tensor, bias: torch.tensor):
    """
    创建一个新的网络层实例，输入和输出通道由传入的weight和bias确定
    """
    if isinstance(origin_layer, torch.nn.Conv2d):
        new_layer = torch.nn.Conv2d(
            in_channels=weight.size(0),
            out_channels=weight.size(1),
            kernel_size=origin_layer.kernel_size,
            stride=origin_layer.stride,
            padding=origin_layer.padding,
            dilation=origin_layer.dilation,
            groups=origin_layer.groups,
            padding_mode=origin_layer.padding_mode,
        )
    if isinstance(origin_layer, torch.nn.Linear):
        new_layer = torch.nn.Linear(
            in_features=weight.size(0),
            out_features=weight.size(1),
        )
    new_layer.weight.data = weight
    new_layer.bias.data = bias
    return new_layer


class PruneTool():
    def __init__(self, curr_layer: torch.nn.Module, next_layer: torch.nn.Module, exist_channel_id: list):
        """
        exist_channel_id: 当前 origin layer 中的通道对应了原始模型的哪些通道
        """
        self.curr_layer = curr_layer
        self.next_layer = next_layer
        self.exist_channel_id = exist_channel_id

    def _get_prune_index(self, prune_channel_id: list):
        """
        prune_channel_id: 想要剪去的 channel_id 列表，从小到大排列
        返回 curr_layer.weight 中需要删除的行号
        """
        cursor = 0
        prune_index = []
        for i in range(len(self.exist_channel_id)):
            if self.exist_channel_id[i] == prune_channel_id[cursor]:
                prune_index.append(i)
                cursor += 1
                if cursor >= len(prune_channel_id):
                    break
        return prune_index

    def recovery(self, patch: Patch):
        """
        恢复函数，可以使当前层的输出通道增加，下一层的输入通道相应增加
        """
        # 还原当前层输出通道
        # cursor = 0 # 对于patch的指针
        # for i in range(self.exist_channel_id):
        #     while patch.prune_channel_id[i] < self.exist_channel_id[cursor]:
        #         # 说明此处可以插入补丁中的通道
        #         self.curr_layer.weight.data = self.curr_layer.weight.data.index_add(0, torch.tensor([cursor]), patch.prune_channel_id)
        cursor1 = 0  # 对于 当前层输出通道 的指针
        cursor2 = 0  # 对于 patch 的指针
        # stack
        out_temp = []
        in_temp = []
        bias_temp = []
        new_exist_channel_id = []
        while cursor1 < len(self.exist_channel_id) or cursor2 < len(patch.prune_channel_id):
            should_read_from_curr = (cursor1 < len(self.exist_channel_id) and cursor2 == len(
                patch.prune_channel_id)) or self.exist_channel_id[cursor1] < patch.prune_channel_id[cursor2]
            if should_read_from_curr:
                out_temp.append(select_index(
                    self.curr_layer.weight, 0, [cursor1]))
                bias_temp.append(select_index(
                    self.curr_layer.bias, 0, [cursor1]))
                for i in range(patch.scale):
                    in_temp.append(select_index(
                        self.next_layer.weight, 1, [cursor1 * patch.scale + i]))
                new_exist_channel_id.append(self.exist_channel_id[cursor1])
                cursor1 += 1
            else:
                out_temp.append(select_index(
                    patch.out_prune_tensor, 0, [cursor2]))
                bias_temp.append(select_index(
                    patch.out_prune_bias, 0, [cursor2]))
                for i in range(patch.scale):
                    in_temp.append(select_index(
                        patch.in_prune_tensor, 1, [cursor2 * patch.scale + i]))
                new_exist_channel_id.append(patch.prune_channel_id[cursor2])
                cursor2 += 1

        new_curr_layer = create_layer(
            self.curr_layer, torch.vstack(out_temp), torch.vstack(bias_temp))
        # todo 处理 scale

        new_next_layer = create_layer(
            self.next_layer, torch.hstack(in_temp), self.next_layer.bias.data)
        self.exist_channel_id = new_exist_channel_id
        return (new_curr_layer, new_next_layer)

    def prune(self, prune_channel_id: list, pic_size: float = -1) -> Patch:
        """
        prune_channel_id: 想要剪去的 channel_id 列表，从小到大排列
        pic_size 只有当下一层是 linear 的时候需要提供，目的是使用 pic_size 确定一个 conv 输出通道需要对应几个 linear 输入通道 
        """
        prune_index = self._get_prune_index(prune_channel_id)
        selected_index = list(
            set(range(self.curr_layer.weight.size(0))) - set(prune_index))

        # 剪当前 layer 的输出通道
        (new_curr_layer, prune_out, prune_out_bias) = self._prune_current_layer(
            selected_index, prune_index)

        # 剪下一个 layer 的输入通道
        (new_next_layer, prune_in) = self._prune_next(
            scale_array(selected_index, pic_size) if isinstance(
                self.next_layer, torch.nn.Linear) else selected_index,
            scale_array(prune_index, pic_size) if isinstance(
                self.next_layer, torch.nn.Linear) else prune_index,
        )

        # 更新元信息并构建补丁
        self.exist_channel_id = list(
            set(self.exist_channel_id) - set(prune_channel_id))
        patch = Patch(prune_channel_id, prune_out, prune_in,
                      prune_out_bias, pic_size if pic_size > 0 else 1)
        return (new_curr_layer, new_next_layer, patch)

    def _prune_current_layer(self, selected_index: list, prune_index: list) -> list:
        """
        返回剪枝的下标（在当前 weight 中的坐标，而不是原始模型）
        """
        pruned_weight = select_index(self.curr_layer.weight, 0, prune_index)
        selected_weight = select_index(
            self.curr_layer.weight, 0, selected_index)

        pruned_bias = select_index(self.curr_layer.bias, 0, prune_index)
        selected_bias = select_index(self.curr_layer.bias, 0, selected_index)

        return (create_layer(self.curr_layer, selected_weight, selected_bias), pruned_weight, pruned_bias)

    def _prune_next(self, selected_index: list, prune_index: list):
        pruned = select_index(self.next_layer.weight, 1, prune_index)
        selected = select_index(self.next_layer.weight, 1, selected_index)
        return (create_layer(self.next_layer, selected, self.next_layer.bias.data), pruned)

    def get_shape(self):
        """
        返回当前层实际的的输入和输出通道数
        返回形式为 (输出通道数，输入通道数)
        """
        return (self.curr_layer.weight.size(0), self.curr_layer.weight.size(1))


if __name__ == "__main__":

    pic_size = 4  # 卷积层每个输出通道的特征图大小
    conv1_in = 1
    conv1_out = 4

    lin_in = conv1_out * pic_size
    lin_out = 2

    conv2_out = 2

    l1 = torch.nn.Conv2d(conv1_in, conv1_out, 100)
    l2 = torch.nn.Linear(lin_in, lin_out, 100)
    l1_weight_1 = torch.clone(l1.weight)  # 起始参数
    l2_weight_1 = torch.clone(l2.weight)  # 起始参数

    # 剪去通道

    # layer1 包含多个通道，使用 range 给他们编号 [0 ... conv1_out]
    # l1_prune1 指 l1 经过一次剪枝
    tool = PruneTool(l1, l2, list(range(conv1_out)))
    (l1_prune1, l2_prune1, patch1) = tool.prune([0], pic_size)

    # 需要重新构建一个 PruneTool，因为需要在 l1_prune1 的基础上再次剪枝
    tool = PruneTool(l1_prune1, l2_prune1, tool.exist_channel_id)
    (l1_prune2, l2_prune2, patch2) = tool.prune([1], pic_size)

    # 用补丁还原通道，需要严格按照剪枝顺序
    tool = PruneTool(l1_prune2, l2_prune2, tool.exist_channel_id)
    (l1_rec2, l2_rec2) = tool.recovery(patch2)

    tool = PruneTool(l1_rec2, l2_rec2, tool.exist_channel_id)
    (l1_rec1, l2_rec1) = tool.recovery(patch1)

    # 对比剪枝还原前后参数是否产生错误
    l1_weight_2 = torch.clone(l1_rec1.weight)  # 起始参数
    l2_weight_2 = torch.clone(l2_rec1.weight)  # 起始参数
    print((l1_weight_2 - l1_weight_1).max())
    print((l2_weight_2 - l2_weight_1).max())

    print("finish")

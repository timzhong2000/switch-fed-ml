import torch
from prune_tool import *

def test_conv_to_linear():
    pic_size = 4  # 卷积层每个输出通道的特征图大小
    conv1_in = 1
    conv1_out = 4

    lin_in = conv1_out * pic_size
    lin_out = 20

    l1 = torch.nn.Conv2d(conv1_in, conv1_out, 3)
    l2 = torch.nn.Linear(lin_in, lin_out)
    l1_weight_1 = torch.clone(l1.weight)  # 起始参数
    l2_weight_1 = torch.clone(l2.weight)  # 起始参数

    # 剪去通道

    # layer1 包含多个通道，使用 range 给他们编号 [0 ... conv1_out]
    # l1_prune1 指 l1 经过一次剪枝
    tool = PruneTool(l1, l2, list(range(conv1_out)))
    (l1_prune1, l2_prune1, patch1, exist_channel_id) = tool.prune([0], pic_size)

    # 需要重新构建一个 PruneTool，因为需要在 l1_prune1 的基础上再次剪枝
    tool = PruneTool(l1_prune1, l2_prune1, exist_channel_id)
    (l1_prune2, l2_prune2, patch2, exist_channel_id) = tool.prune([1], pic_size)

    # 用补丁还原通道，需要严格按照剪枝顺序
    tool = PruneTool(l1_prune2, l2_prune2, exist_channel_id)
    (l1_rec2, l2_rec2, exist_channel_id) = tool.recovery(patch2)

    tool = PruneTool(l1_rec2, l2_rec2, exist_channel_id)
    (l1_rec1, l2_rec1, exist_channel_id) = tool.recovery(patch1)

    # 对比剪枝还原前后参数是否产生错误
    l1_weight_2 = torch.clone(l1_rec1.weight)  # 起始参数
    l2_weight_2 = torch.clone(l2_rec1.weight)  # 起始参数
    print((l1_weight_2 - l1_weight_1).max())
    print((l2_weight_2 - l2_weight_1).max())

    print("finish")



def test_importance():
  l1 = torch.nn.Conv2d(1, 4, 3)
  l2 = torch.nn.Conv2d(4, 2, 3)
  l1w = l1.weight
  imp = PruneTool(l1, l2, list(range(4))).cal_importance()
  print(imp)

def test_dump_patch():
  l1 = torch.nn.Conv2d(1, 4, 3)
  l2 = torch.nn.Conv2d(4, 2, 3)
  (_, _, patch1) = PruneTool(l1, l2, list(range(4))).prune([0])
  # dump 成元信息和向量
  meta, data = dump_patch(patch1)
  # 从元信息和向量恢复patch
  patch2 = load_patch(meta, data)
  print(patch2)

if __name__ == "__main__":
  test_conv_to_linear()
  # test_importance()
  # test_dump_patch()
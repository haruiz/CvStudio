import torch.hub
import urllib
from PIL import Image
from torch import Tensor,nn
from torchvision import transforms
import  numpy as np
import matplotlib.pyplot as plt
from torchvision.models import ResNet

model : nn.Module = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
#print(model.eval())
for m in model.modules():
    print(model)

# url, filename = ("https://github.com/pytorch/hub/raw/master/dog.jpg", "dog.jpg")
# try: urllib.URLopener().retrieve(url, filename)
# except: urllib.request.urlretrieve(url, filename)
#
# def imshow(inp, title=None):
#     """Imshow for Tensor."""
#     inp = inp.numpy().transpose((1, 2, 0))
#     mean = np.array([0.485, 0.456, 0.406])
#     std = np.array([0.229, 0.224, 0.225])
#     inp = std * inp + mean
#     inp = np.clip(inp, 0, 1)
#     plt.imshow(inp)
#     if title is not None:
#         plt.title(title)
#     plt.pause(0.001)  # pause a bit so that plots are updated
#
# input_image = Image.open(filename)
# preprocess = transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
# ])
# input_tensor: Tensor = preprocess(input_image)
# imshow(input_tensor)
# input_batch = input_tensor.unsqueeze(0)

# models = torch.hub.list('pytorch/vision', force_reload=False)
# for m in models:
#     print(torch.hub.help('pytorch/vision', m, force_reload=True))
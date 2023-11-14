import torchvision.models as models

resnet50 = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
resnet50.eval()
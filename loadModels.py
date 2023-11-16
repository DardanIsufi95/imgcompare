import torchvision.models as models

resnet50 = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
resnet50.eval()

vgg16 = models.vgg16(weights=models.VGG16_Weights.DEFAULT)
vgg16.eval()
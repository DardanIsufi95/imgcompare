import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import json
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('--image', type=str)

args = parser.parse_args()

image_path =  args.image

if image_path is None:
    raise Exception(json.dumps({
        "error" : "No image path provided"
    }))

model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
#model = models.vgg16(weights=models.VGG16_Weights.DEFAULT)
model.eval()  

# Define image transformations
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_features(image_path):
    img = Image.open(image_path).convert('RGB')
    img = transform(img).unsqueeze(0)  

    with torch.no_grad():
        features = model(img)
    return features.squeeze(0).numpy() 



features = extract_features(image_path)



print(json.dumps(features.tolist()))


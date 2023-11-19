import json
import cv2
import numpy as np
import math
import imagehash
from PIL import Image
import multiprocessing
import time
import torch
import torchvision.models as models
import torchvision.transforms as transforms


import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--progress', type=str , default="true")
parser.add_argument('--video', type=str , required=True )
parser.add_argument('--group-size', type=float , default=1)

args = parser.parse_args()

# transform = transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
# ])


weights = models.ResNet152_Weights.DEFAULT
transform = weights.transforms()

model = models.resnet152(weights=weights)
model.eval()  


def loading_bar(progress, total):
    bar_length = 50  # Customize the loading bar length

    if(total <= 0):
        return

    progress_length = int(bar_length * progress / total)
    
    bar = '#' * progress_length + '-' * (bar_length - progress_length)

    
    print(f"\r[{bar}] {progress}/{total}", end='')


def extract_features(image):
    img = image.convert('RGB')
    img = transform(img).unsqueeze(0)  

    with torch.no_grad():
        features = model(img)
    return features.squeeze(0).numpy() 
#frame_group_size_type = "frame" or "second"
def process_video(video_path  , frame_group_size=1 , frame_group_size_type= "frame"):


    vectors = []

    video = cv2.VideoCapture(video_path)
    fps = math.floor(video.get(cv2.CAP_PROP_FPS))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if frame_group_size_type == "second":
        frame_group_size = frame_group_size * fps


    if frame_group_size < 1:
        frame_group_size = 1


    fc = 0
    while video.isOpened():
        blended_frame = None
        count = 0


        

        # Process each group of X frames
        while count < frame_group_size and video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            

            #the progess bar
            if(not args.progress or not args.progress.lower().startswith("f") ):
                fc+=1
                loading_bar(fc, total_frames)


            # Convert frame to float for processing
            frame  = frame.astype(np.float32)

            if blended_frame is None:
                blended_frame = frame
            else:
                # Blend by averaging
                blended_frame = (blended_frame * count + frame) / (count + 1)

            count += 1

        if blended_frame is not None:
            # Convert blended frame to uint8 and show or save
            blended_frame = np.uint8(blended_frame)
            pil_image = Image.fromarray(blended_frame)


            #center crop the 7.5% of the image
            crop_percent = 0.075
            width, height = pil_image.size

            pil_image = pil_image.crop((width * crop_percent, height * crop_percent, width * (1-crop_percent), height * (1-crop_percent)))

            # print(pil_image)
            vec = extract_features(pil_image)
            vectors.append(vec)

            # pil_image = cv2.convertScaleAbs(np.array(pil_image))
            # cv2.imshow('Blended Frame', pil_image)
            # cv2.waitKey(0)  # Change to cv2.waitKey(0) to wait for a key press between each group

        if not ret:
            break

    # Release the video capture
    video.release()
    cv2.destroyAllWindows()


    vector_save_path = video_path + ".npy"
    np.save(vector_save_path , vectors)



    #save the vectors to a file based on the video name
    #np.save(video_path + ".npy" , vectors)

    result = {
        'vectors': vector_save_path,
        'fps': fps,
        'frame_group_size': frame_group_size,
        'frame_group_size_type': frame_group_size_type,
        'total_frames': total_frames
    }

    return result
    


if __name__ == "__main__":
    video_path = args.video
    frame_group_size = args.group_size
    video_data = process_video(video_path , frame_group_size , "second")

    print(json.dumps(video_data, indent=4, sort_keys=False))


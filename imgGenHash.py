from PIL import Image
import imagehash
import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--image', type=str)

args = parser.parse_args()

def generate_hashes(image_path):
    img = Image.open(image_path)
    hashes = {
        "ahash" : str(imagehash.average_hash(img)) ,
        "phash" : str(imagehash.phash(img)) ,
        "dhash" : str(imagehash.dhash(img)) ,
        "whash" : str(imagehash.whash(img)),
        "chash" : str(imagehash.colorhash(img)) 
        
    }
    return hashes

    
image_path = args.image

if image_path is None:
    raise Exception(json.dumps({
        "error" : "No image path provided"
    }))

image_hashes = generate_hashes(image_path)


print(json.dumps(image_hashes))




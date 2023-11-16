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
        "ahash" : '0b'+bin(int(str(imagehash.average_hash(img)),16)).strip("0b").zfill(64) ,
        "phash" : '0b'+bin(int(str(imagehash.phash(img)) ,16)).strip("0b").zfill(64),
        "dhash" : '0b'+bin(int(str(imagehash.dhash(img)) ,16)).strip("0b").zfill(64),
        "whash" : '0b'+bin(int(str(imagehash.whash(img)) ,16)).strip("0b").zfill(64),
        "chash" : '0b'+bin(int(str(imagehash.colorhash(img)) ,16)).strip("0b").zfill(64)
        
    }
    return hashes


image_path = args.image

if image_path is None:
    raise Exception(json.dumps({
        "error" : "No image path provided"
    }))

image_hashes = generate_hashes(image_path)


print(json.dumps(image_hashes))




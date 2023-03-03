import os
import json
import math
import shutil

# .\tensYOD\Scripts\activate

# Dictionary with distinct path to different collections of annotations
path_annotations = {
                    'captions':'./dataset/annotations/captions_train2017.json',
                    'instances':'./dataset/annotations/instances_train2017.json',
                    'panoptic':'./dataset/annotations/panoptic_train2017.json',
                    'persons':'./dataset/annotations/person_keypoints_train2017.json',
                    'stuff':'./dataset/annotations/stuff_train2017.json',
                    }

def convert_coco_category(category_id):
    offset = 0
    if category_id > 11:
        offset = offset + 1
    if category_id > 25:
        offset = offset + 1
    if category_id > 28:
        offset = offset + 2
    if category_id > 44:
        offset = offset + 1
    if category_id > 65:
        offset = offset + 1
    if category_id > 67:
        offset = offset + 2
    if category_id > 70:
        offset = offset + 1
    if category_id > 82:
        offset = offset + 1

    return category_id - 1 - offset


# Iterate through dataset to create list of image IDs for every category
def explore_dataset():
    class_count = {}    # Dictionary with amount of images per class
    class_images = {}   # Dictionary with list of images per class

    file = open(path_annotations['instances'])  # Open .json file
    annotations = json.load(file)  # Load in .json information

    for ann in annotations['annotations']:
        category_nr = convert_coco_category(ann['category_id']) # Convert category from COCO to YOLO
        image_id = ann['image_id']

        try: 
            class_count[category_nr] = class_count[category_nr] + 1
        except KeyError:
            class_count[category_nr] = 1

        try:
            if image_id not in class_images[category_nr]:
                class_images[category_nr].append(image_id)
        except KeyError:
            class_images[category_nr] = []

    class_count = dict(sorted(class_count.items()))
    class_images = dict(sorted(class_images.items()))

    for key in class_count.keys():
        print('Instances per class, {c}: {nr}'.format(c=key, nr=class_count[key]))
        print('Images per class, {c}: {nr}'.format(c=key, nr=len(class_images[key])))

    json_data = json.dumps(class_images)    # JSON string
    with open('category_image_list.json', 'w') as f:
        f.write(json_data)   # Write to file


def create_subset(img_amount, min_batch_size=160, min_instance_amount=160, enforce_size=True):
    class_images = {}   # Dictionary with list of images per class
    image_id_list = []  # Final subset of images

    file = open('category_image_list.json')  # Open .json file
    class_images = json.load(file)  # Load in .json information

    if enforce_size:
        total_amount = 0
        current_category = 0
        images_per_category = math.floor((img_amount - total_amount) / (80 - current_category))

        for key in class_images.keys(): # Iterate through each category
            current = 0 # Keep track of total images per class
            for image_id in class_images[key]:  # Iterate through images
                if current >= images_per_category:
                    break
                if image_id not in image_id_list:   # Add to list if unique
                    image_id_list.append(image_id)
                    current = current + 1

            if (current_category == 79):
                total_amount = total_amount + current   # Update
                current_category = current_category + 1 # Update
                images_per_category = math.floor((img_amount - total_amount) / 1)

            else:
                total_amount = total_amount + current   # Update
                current_category = current_category + 1 # Update
                images_per_category = math.floor((img_amount - total_amount) / (80 - current_category))

    else:
        images_per_category = math.floor(img_amount / 80)

        for key in class_images.keys(): # Iterate through each category
            current = 0 # Keep track of total images per class
            for image_id in class_images[key]:  # Iterate through images
                if current >= images_per_category:
                    break
                if image_id not in image_id_list:   # Add to list if unique
                    image_id_list.append(image_id)
                    current = current + 1

    print('Subset with {nr} images created.'.format(nr=len(image_id_list)))
    image_list = {'images':image_id_list}   # Convert to dict

    json_data = json.dumps(image_list)    # JSON string
    with open('image_list.json', 'w') as f:
        f.write(json_data)   # Write to file


# Step 1: Explore dataset and calculated instances and images per class
explore_dataset()

# Step 2: From previous information, create subset of dataset
create_subset(25600, enforce_size=True)
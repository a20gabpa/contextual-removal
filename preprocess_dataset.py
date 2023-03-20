import os
import json
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

# Dictionary with distinct path to different set of images used for training
path_images = {
                'images':'./dataset/coco/images/train2017/',
                'images_val':'./dataset/coco/images/val2017/',
                'panoptic':'./dataset/coco/images/panoptic/train2017/',
                'stuff':'./dataset/coco/images/stuff/train2017/',
                }

# Dictionary with distinct path to different set of images used for training (YOLO format)
path_images_yolo = {
                'images':'./dataset/yolo/train2017/images/',
                'images_val':'./dataset/yolo/val2017/images/',
                'panoptic':'./dataset/yolo/images/panoptic/train2017/',
                'stuff':'./dataset/yolo/images/stuff/train2017/',
                }

# Dictionary with distinct path to different set of labels used for training (YOLO format)
path_labels_yolo = {
                'images':'./dataset/yolo/train2017/labels/',
                'images_val':'./dataset/yolo/val2017/labels/',
                'panoptic':'./dataset/yolo/images/panoptic/train2017/',
                'stuff':'./dataset/yolo/images/stuff/train2017/',
                }

# Copy images between two folders
def copy_images_json(data_type, json_path):
    counter = 0 # Keep track of total images copied

    file = open(json_path)  # Open .json file
    image_list = json.load(file)  # Load in .json information

    # Iterate over images in source folder
    for image_id in image_list['images']:

        temp = str(image_id).zfill(12) + '.jpg'  # Format ID string
        img_source = os.path.join(path_images[data_type], temp) # Construct path
        img_dest = os.path.join(path_images_yolo[data_type], temp)

        if os.path.exists(img_source):
            # Try to copy file
            try:
                shutil.copy(img_source, img_dest)
                print('Image nr. {i} copied...'.format(i = counter))

            except shutil.SameFileError:
                print('Failed to copy, image nr. {i} is the same...'.format(i = counter))

            counter = counter + 1   # Increase counter

# Copy images between two folders
def copy_images(amount, data_type):
    counter = 0 # Keep track of total images copied

    # Iterate over images in source folder
    for filename in os.listdir(path_images[data_type]):
        img_source = os.path.join(path_images[data_type], filename)
        img_dest = os.path.join(path_images_yolo[data_type], filename)

        if counter < amount:
            # Try to copy file
            try:
                shutil.copy(img_source, img_dest)
                print('Image nr. {i} copied...'.format(i = counter))

            except shutil.SameFileError:
                print('Failed to copy, image nr. {i} is the same...'.format(i = counter))

            counter = counter + 1   # Increase counter

        else:
            break

# Get all annotations for specific image
def get_image_annotations(image_id): 
    image_annotations = [] # List with image specific labels
    doesExists = False

    # Iterate through all ground truth annotations and 
    for ann in anns['annotations']:
        if ann['image_id'] == image_id:
            image_annotations.append(ann)
            doesExists = True

    if doesExists:
        return image_annotations   # Return list of annotations
    else:
        return None # Image does not exist, return nothing

# Get image by filename
def get_image(image_filename):
    # Iterate and search through images
    for image in anns['images']:
        if image['file_name'] == image_filename:
            return image # Return match

# Gather information from COCO images and convert to YOLO standard
def process_coco_dataset(data_type):
    # Iterate though images in folder
    for filename in os.listdir(path_images_yolo[data_type]):
        image = get_image(filename) # Get image

        # Image information
        image_id = image['id']
        image_w = image['width']
        image_h = image['height']

        image_ann = get_image_annotations(image_id) # Get all annotations for image

        if image_ann:
            temp = str(image_id).zfill(12)  # Format ID string
            file = open(path_labels_yolo[data_type] + temp + '.txt', 'a')   # Open related .txt for image

            for annotation in image_ann:
                offset = 0
                if annotation['category_id'] > 11:
                    offset = offset + 1
                if annotation['category_id'] > 25:
                    offset = offset + 1
                if annotation['category_id'] > 28:
                    offset = offset + 2
                if annotation['category_id'] > 44:
                    offset = offset + 1
                if annotation['category_id'] > 65:
                    offset = offset + 1
                if annotation['category_id'] > 67:
                    offset = offset + 2
                if annotation['category_id'] > 70:
                    offset = offset + 1
                if annotation['category_id'] > 82:
                    offset = offset + 1

                image_category = annotation['category_id'] - 1 - offset # YOLO starts from 0
                bbox = annotation['bbox']   # Get position and and size of bounding box

                x = bbox[0]
                y = bbox[1]
                w = bbox[2]
                h = bbox[3]

                # Calculate center
                center_x = (x + (x + w)) / 2
                center_y = (y + (y + h)) / 2

                # Normalize values, YOLO expects values between 0 and 1
                center_x = center_x / image_w
                center_y = center_y / image_h
                w = w / image_w
                h = h / image_h

                # Round decimal numbers
                center_x = format(center_x, '.6f')
                center_y = format(center_y, '.6f')
                w = format(w, '.6f')
                h = format(h, '.6f')

                # Store information in '.txt' file
                file.write("{category} {x} {y} {width} {height}\n".format(category = image_category, 
                                                                        x = center_x, y = center_y, 
                                                                        width = w, height = h))  

            file.close()    # Close file  

# Main
file = open(path_annotations['instances'])  # Open .json file
anns = json.load(file)  # Load in .json information

copy_images_json('images', './SubsetEuclidian/twenty/image_list.json')

#copy_images(1280, 'images')
process_coco_dataset('images')
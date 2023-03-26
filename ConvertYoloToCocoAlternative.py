
#Converts yolo labels into an array of predictions(coco format) 
#Coco format: 
#   [[{"image_id": int,
#     "category_id": int,
#     "bbox": [x,y,width,height],  (all float)
#     "score": float,}],...]

# Note: YOLO x any y position points to the middle of the object. COCO x and y point to the top left corner. 
#       width, height, x and y are all fractions in the YOLO results, 
#       COCO wants the absolute position of the predictions relative to the image widht and height.
# The results are saved from the labels using json.dumps.
import json
import os
import cv2

# ...
def ConvertCategory(yoloid):
    # YOLO starts at 0, COCO starts at 1
    offset = yoloid + 1
    # There are some numbers missing from COCO and so we must skip these.
    if offset > 11:
        offset = offset + 1
    if offset > 25:
        offset = offset + 1
    if offset > 28:
        offset = offset + 2
    if offset > 44:
        offset = offset + 1
    if offset > 65:
        offset = offset + 1
    if offset > 67:
        offset = offset + 2
    if offset > 70:
        offset = offset + 1
    if offset > 82:
        offset = offset + 1
        
    # Making sure we are returning an int and not something else.
    return int(offset)


def ConvertTOLOannotation(pathtoyololabel, pathtoimagestested):
    # Each bounding box will be appended to this list using the coco format found at the top of the file.
    convertedannotations = []
    
    # need to only convert the images used in the test-dev version (20k) images
    with open(f"./dataset/annotations/image_info_test-dev2017.json", "r") as f:
        touse = json.loads(f.read())
        
    imagestouse = []
    for i in touse["images"]:
        imagestouse.append(i["file_name"])
        
        
    for labelfile in os.listdir(pathtoyololabel):
        filenamenoext = os.path.splitext(labelfile)[0]
        
        if f"{filenamenoext}.jpg" not in imagestouse:
            continue
            
        with open(f"{pathtoyololabel}/{labelfile}") as f:
            # readlines gives an array where each index is seperated using \n(newline)
            lineseparated = f.readlines()
            convertedannotation = {}
            for boundingboxes in lineseparated:
                # boundingbox.split() gives an array of whitespace separated strings. 
                # Position [0] is category_id (Needs to be converted into the coco format)
                # Position [1] is x (Needs to be realligned to the top right rather than the center)
                # Position [2] is y (Same as above)
                # Position [3] is widht
                # Position [4] is height.
                # Position [5] is confidence (score)
                boundingbox = boundingboxes.split()
                
                # Get image_id by removing the file extension and converting to an integer.
                filenamenoext = os.path.splitext(labelfile)[0]
                convertedannotation["image_id"] = int(filenamenoext)
                print(convertedannotation["image_id"])
                # Get category_id by passing the category to the conversion function.
                convertedannotation["category_id"] = ConvertCategory(int(boundingbox[0]))
                print(convertedannotation["category_id"])
                
                convertedwidth = 0.0 # Will be yolo_width*image_width
                convertedheight = 0.0 # Will be yolo_height*image_height
                convertedx = 0.0 # Will be (yolo_x*image_width) - (convertedwidth/2)
                convertedy = 0.0 # Will be (yolo_y*image_height) - (convertedheight/2)
                
                # We need to extract the image dimensions.
                currentimage = f"{filenamenoext}.jpg"
                height,width = cv2.imread(f"{pathtoimagestested}/{currentimage}").shape[:2] # Returns the dimension of the image.
                
                x_yolo,y_yolo,width_yolo,height_yolo= float(boundingbox[1]),float(boundingbox[2]),float(boundingbox[3]),float(boundingbox[4])
                
                h,w = abs(height_yolo*height),abs(width_yolo*width)
                x_coco = round(x_yolo*width -(w/2))
                y_coco = round(y_yolo*height -(h/2))
                if x_coco <0: #check if x_coco extends out of the image boundaries
                    x_coco = 1
                if y_coco <0: #check if y_coco extends out of the image boundaries
                    y_coco = 1
                
                # "bbox": [x,y,width,height],
                convertedannotation["bbox"] = [x_coco,y_coco,w,h]
                convertedannotation["score"] = float(boundingbox[5])
                print(convertedannotation)
            convertedannotations.append(convertedannotation)
        print(f"Lines read in label: {labelfile}")
        
        
    with open(f"{pathtoyololabel}/detections_test-dev2017_yolo_results.json", "w") as f:
        f.write(json.dumps(convertedannotations))
        
        
ConvertTOLOannotation(pathtoyololabel="Z:/Context-CV/runs/detect/BaselineTest/labels", pathtoimagestested = "Z:/Context-CV/dataset/coco/images/test2017")
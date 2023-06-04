import json
import cv2 as cv
import onnx
from ultralytics import YOLO

# .\tensYOD\Scripts\activate

if __name__ == '__main__':
    model = YOLO('./runs/detect/train82/weights/best.pt')
    results = model.predict(source="./dataset/coco/images/test2017/", save_txt=True, save_conf=True)

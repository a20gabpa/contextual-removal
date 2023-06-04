import json
import cv2 as cv
#from pycocotools.coco import COCO
import onnx
from ultralytics import YOLO

# .\tensYOD\Scripts\activate

if __name__ == '__main__':
    # Load model
    model = YOLO('yolov8n.yaml')
    results = model.train(data="./coco12800.yaml", epochs=200, device=0, batch= 10, save_period=10)
    results = model.predict(source="./dataset/coco/images/train2017/000000000257.jpg", save=True, save_txt=True)

    sucess = model.export(format='onnx')

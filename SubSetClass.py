from pycocotools.coco import COCO
import json

class Subset:
    def __init__(self, pathtoannotation):
        object_annotation_path = "dataset/annotations/instances_train2017.json"
        object_annotations = COCO(annotation_file=object_annotation_path)

        stuff_annotation_path = "dataset/annotations/stuff_train2017.json"
        stuff_annotations = COCO(annotation_file=stuff_annotation_path)

        with open(f"{pathtoannotation}image_list.json", "r") as f:
            subset = json.loads(f.read())

        subsetObject = object_annotations.loadAnns(ids = subset["images"])
        subsetStuff = stuff_annotations.loadAnns(ids = subset["images"])


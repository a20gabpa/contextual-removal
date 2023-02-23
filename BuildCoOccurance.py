from pycocotools.coco import COCO
from StuffObject import StuffObjectNode
import pickle
import json


def CreateCoOccurance():
    object_annotation_path = "dataset/annotations/instances_train2017.json"
    stuff_annotation_path = "dataset/annotations/stuff_train2017.json"
    object_annotations = COCO(annotation_file=object_annotation_path)
    stuff_annotations = COCO(annotation_file=stuff_annotation_path)

    object_ids = object_annotations.getCatIds()
    object_cats = object_annotations.loadCats(object_ids)

    stuff_ids = stuff_annotations.getCatIds()
    stuff_cats = stuff_annotations.loadCats(stuff_ids)

    objectsWithRelation = []
    for i in object_ids:
        objectsWithRelation.append(StuffObjectNode(i, object_annotations.loadCats([i])[0]['name'], object_ids, stuff_ids))

    for i in stuff_ids:
        objectsWithRelation.append(StuffObjectNode(i, stuff_annotations.loadCats([i])[0]['name'], object_ids, stuff_ids))

    imageIds = object_annotations.getImgIds()

    for objectStuff in objectsWithRelation:
        print(f"Started working on {objectStuff.name}")
        # This is unfortunately how we have to separate objects and stuff, anything less than 91 is an object.
        if objectStuff.id < 91:
            containsObjectStuff = object_annotations.getImgIds(catIds=[objectStuff.id])
        else:
            containsObjectStuff = stuff_annotations.getImgIds(catIds=[objectStuff.id])

        for i in containsObjectStuff:
            # First for all the objects in the image.
            pictureAnnotations = object_annotations.loadAnns(object_annotations.getAnnIds(i, iscrowd=None))
            for j in pictureAnnotations:
                if j['category_id'] == objectStuff.id:
                    # Skip self.
                    continue
                objectStuff.otherStuffObjects[j['category_id']] = objectStuff.otherStuffObjects[j['category_id']] + 1

            # Secondly for all the stuff in the image containing objectStuff
            pictureAnnotations = stuff_annotations.loadAnns(stuff_annotations.getAnnIds(i, iscrowd=None))
            for j in pictureAnnotations:
                if j['category_id'] == objectStuff.id:
                    continue
                objectStuff.otherStuffObjects[j['category_id']] = objectStuff.otherStuffObjects[j['category_id']] + 1

    print(f"Completed final co-occurance for Train2017 Stuff/Objects")

    #Saving the work
    with open("Co_occurance.txt", "wb") as f:
        pickle.dump(objectsWithRelation,f)

    # Creating a IdLookup table that translates id to names easilly.
    lookup = {}
    for i in objectsWithRelation:
        lookup[i.id] = i.name

    with open("IdLookup.txt", "w") as f:
        f.write(json.dumps(lookup))
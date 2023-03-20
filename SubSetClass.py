from pycocotools.coco import COCO
import json

class ImageInSubset:
    def __init__(self, imageid, objects, stuff):
        self.imageid = imageid
        self.objects = objects
        self.stuff = stuff
        

class Subset:
    def __init__(self, pathtoannotation):
        # Creating an array to hold all the ImageInSubset classes.
        self.imagesInSubset = []
        
        object_annotation_path = "dataset/annotations/instances_train2017.json"
        object_annotations = COCO(annotation_file=object_annotation_path)

        stuff_annotation_path = "dataset/annotations/stuff_train2017.json"
        stuff_annotations = COCO(annotation_file=stuff_annotation_path)

        with open(f"{pathtoannotation}image_list.json", "r") as f:
            subset = json.loads(f.read())
            
        with open(f"{pathtoannotation}IdLookup.txt", "r") as f:
            lookup = json.loads(f.read())    
        amountOfImages = 0    
        for image in subset:
            imageAnnotations = object_annotations.loadAnns(object_annotations.getAnnIds(image, iscrowd=None))
            stuffInImage = stuff_annotations.loadAnns(stuff_annotations.getAnnIds(image, iscrowd=None))
            
            objects = []
            for label in imageAnnotations:
                objects.append(lookup[str(label['category_id'])])
                
            stuff = []
            for label in stuffInImage:
                stuff.append(lookup[str(label['category_id'])])
               
            #Add the image data to the list of images once we have check what objects are present.
            self.imagesInSubset.append(ImageInSubset(imageid = image, objects = objects, stuff = stuff))
            amountOfImages += 1
            
        self.amountOfImages = amountOfImages
        
    def GiveInstancesInDataset(self, onlyobjects = False):
        objectsAndStuff = {}
        for image in self.imagesInSubset:
            for objects in image.objects:
                objectsAndStuff[objects] += 1
                
            if onlyobjects == False:
                for stuff in image.stuff:
                    objectsAndStuff[stuff] += 1
                    
        return objectsAndStuff
        


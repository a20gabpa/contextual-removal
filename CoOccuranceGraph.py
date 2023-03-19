import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import json
import networkx as nx
import os
import math
from StuffObject import StuffObjectNode
from pycocotools.coco import COCO


class CoOccuranceGraph:
    def __init__(self, subsetofimages, omit=[], createimage=True, relationcutoff=0.5, usepercentage=True, saveto="./"):
        # If we do not have the specified Co_occurance.txt or IdLookup.txt file yet:
        # we will call the function that creates them.
        if not os.path.isfile(f"{saveto}Co_occurance.txt") or not os.path.isfile(f"{saveto}IdLookup.txt"):
            self.CreateCoOccurance(savefileto=saveto, images=subsetofimages, countinstances=False)

        # TODO: Co_occurance is misspelled
        with open(f"{saveto}Co_occurance.txt", "rb") as f:
            stuffAndObjects = pickle.load(f)

        with open(f"{saveto}IdLookup.txt", "r") as f:
            lookup = json.loads(f.read())

        # Creating a pandas dataframe of edges where
        # (To=SourceVertex) (From = DestinationVertex) (Weight = Edge Weight)
        fromX = []
        toY = []
        weight = []
        for i in stuffAndObjects:
            # Skipping stuff/objects we dont want.
            shouldContinue = False
            for j in omit:
                if i.id == j:
                    shouldContinue = True
            if shouldContinue:
                continue
            sumCoOccurance = 0
            # Need to get sum to extract percentage.
            for key, value in i.otherStuffObjects.items():
                shouldContinue = False
                # Skipping stuff/objects we dont want.
                for j in omit:
                    if key == j:
                        shouldContinue = True
                if shouldContinue:
                    continue
                sumCoOccurance += value
            # For every weighted relation in stuffandobject we create an edge.
            for key, value in i.otherStuffObjects.items():
                shouldContinue = False
                # Skipping stuff/objects we dont want.
                for j in omit:
                    if key == j:
                        shouldContinue = True
                if shouldContinue:
                    continue
                if (usepercentage):
                    # Only allow edges with a significant enough weight.
                    if (value / sumCoOccurance) * 100 > relationcutoff:
                        fromX.append(i.name)
                        toY.append(str(lookup[str(key)]))
                        weight.append((value / sumCoOccurance) * 100)
                else:
                    # We use the raw values
                    fromX.append(i.name)
                    toY.append(str(lookup[str(key)]))
                    weight.append(value)

        df = pd.DataFrame({'from': fromX, 'to': toY, 'weight': weight})
        G = nx.from_pandas_edgelist(df, 'from', 'to', 'weight')

        plt.title("Co-Occurance clustering")
        plt.figure(figsize=(150, 150))
        color_map = []
        # Adding colors to the graph.
        for node in G:
            for key, value in lookup.items():
                if value == node:
                    if int(key) < 91:
                        color_map.append('green')
                    else:
                        color_map.append('red')

        nx.draw_spring(G, node_size=10000, node_color=color_map, with_labels=True)

        if createimage:
            plt.savefig(f"{saveto}CoOccuranceGraph.png", transparent=True)

        self.nodes = nx.spring_layout(G, seed=1337)

    def PositionOfObjects(self, objects):
        allObjects = {}
        for object in objects:
            allObjects[object] = self.nodes[object]

        return allObjects

    def GetCentroid(self, objects):
        sumX = 0
        sumY = 0
        amountOfNodes = len(objects)
        for key, value in objects.items():
            sumX += value[0]
            sumY += value[1]

        # Centroid is the center of all the nodes given.
        centroid = [sumX / amountOfNodes, sumY / amountOfNodes]
        return centroid

    def GetEuclideanDistance(self, centroid, object):
        centroidX = centroid[0]
        centroidY = centroid[1]
        objectX = object[0]
        objectY = object[1]
        # square((objectX - centroidX)^2 + (objectY - centroidY)^2)
        return math.sqrt((objectX - centroidX) ** 2 + (objectY - centroidY) ** 2)

    def FindEuclideanDistance(self, objects):
        nodePositions = self.PositionOfObjects(objects)
        centroid = self.GetCentroid(nodePositions)
        eucDistance = 0
        for key, value in nodePositions.items():
            eucDistance += self.GetEuclideanDistance(centroid, value)
        return eucDistance

    # Get the combinations with the lowest and highest euclidian distances.
    # With an input of [person, horse, dog] the combinations could include:
    #       [person, horse], [horse,dog], [person, dog]
    def GetLowestAndHighestEucDistance(self, objects, stuff=""):
        # Setting highest and lowest to values that realistically shouldnt be retained.
        lowest = 100000
        highest = -10000
        lowestRemoved = ""
        highestRemoved = ""
        # We want to include stuff in our calculation, we however do not want to find outliars in stuff, only objects.
        # Stuff will serve as an anchor.
        # We create an array and append objects/stuff to the end of it.
        objectAndStuff = []
        for i in objects:
            objectAndStuff.append(i)

        if (stuff):
            for i in stuff:
                objectAndStuff.append(i)

        # We deque from objectAndStuff objects.size -1 amount of times, this ensures that the stuff in objectsAndStuff are never touched.
        for i in range(len(objects)):
            removed = objectAndStuff.pop(0)
            hightOrLow = self.FindEuclideanDistance(objectAndStuff)
            if hightOrLow < lowest:
                lowest = hightOrLow
                lowestRemoved = removed
            if hightOrLow > highest:
                highest = hightOrLow
                highestRemoved = removed
            objectAndStuff.append(removed)
        return lowest, highest, lowestRemoved, highestRemoved

    def CreateCoOccurance(self, savefileto, images, countinstances=True):
        object_annotation_path = "dataset/annotations/instances_train2017.json"
        stuff_annotation_path = "dataset/annotations/stuff_train2017.json"
        object_annotations = COCO(annotation_file=object_annotation_path)
        stuff_annotations = COCO(annotation_file=stuff_annotation_path)

        object_ids = object_annotations.getCatIds()

        stuff_ids = stuff_annotations.getCatIds()

        objectsWithRelation = []
        for i in object_ids:
            objectsWithRelation.append(
                StuffObjectNode(i, object_annotations.loadCats([i])[0]['name'], object_ids, stuff_ids))

        for i in stuff_ids:
            objectsWithRelation.append(
                StuffObjectNode(i, stuff_annotations.loadCats([i])[0]['name'], object_ids, stuff_ids))

        for objectStuff in objectsWithRelation:
            print(f"Started working on {objectStuff.name}")
            # This is unfortunately how we have to separate objects and stuff, anything less than 91 is an object.
            if objectStuff.id < 91:
                containsObjectStuff = object_annotations.getImgIds(catIds=[objectStuff.id])
            else:
                containsObjectStuff = stuff_annotations.getImgIds(catIds=[objectStuff.id])

            for i in containsObjectStuff:
                # We skip the image its not in the subset of images.
                if i not in images:
                    continue
                # First for all the objects in the image.
                pictureAnnotations = object_annotations.loadAnns(object_annotations.getAnnIds(i, iscrowd=None))
                duplicateInstance = []
                for j in pictureAnnotations:
                    if j['category_id'] == objectStuff.id:
                        # Skip self.
                        continue
                    # If we shouldnt count duplicates we will check if the object/stuff has already been added for the image.
                    if not countinstances:
                        if j['category_id'] in duplicateInstance:
                            continue
                    objectStuff.otherStuffObjects[j['category_id']] = objectStuff.otherStuffObjects[
                                                                          j['category_id']] + 1
                    duplicateInstance.append(j['category_id'])

                # Secondly for all the stuff in the image containing objectStuff
                pictureAnnotations = stuff_annotations.loadAnns(stuff_annotations.getAnnIds(i, iscrowd=None))
                duplicateInstance = []
                for j in pictureAnnotations:
                    if j['category_id'] == objectStuff.id:
                        continue
                    if not countinstances:
                        if j['category_id'] in duplicateInstance:
                            continue
                    objectStuff.otherStuffObjects[j['category_id']] = objectStuff.otherStuffObjects[
                                                                          j['category_id']] + 1
                    duplicateInstance.append(j['category_id'])

        print(f"Completed final co-occurance for Train2017 Stuff/Objects")

        # Saving the work
        with open(f"{savefileto}Co_occurance.txt", "wb") as f:
            pickle.dump(objectsWithRelation, f)

        # Creating a IdLookup table that translates id to names easilly.
        lookup = {}
        for i in objectsWithRelation:
            lookup[i.id] = i.name

        with open(f"{savefileto}IdLookup.txt", "w") as f:
            f.write(json.dumps(lookup))

    def RemovePercentageOfImagesEuclidian(self, pathtofiles, percentagetoremove, subsetofimages):
        subset = []
        subsetDict = {}
        object_annotation_path = "dataset/annotations/instances_train2017.json"
        object_annotations = COCO(annotation_file=object_annotation_path)

        stuff_annotation_path = "dataset/annotations/stuff_train2017.json"
        stuff_annotations = COCO(annotation_file=stuff_annotation_path)

        with open("IdLookup.txt", "r") as f:
            lookup = json.loads(f.read())

        # Creating a map of strings and arrays. Key will be the image id and value is an array of the object/stuff inside the picture.
        imagesAndObjects = {}
        imagesAndStuff = {}
        # Getting all the ids of the images in the coco dataset.
        imageIds = object_annotations.getImgIds()
        for image in imageIds:
            # Skipping the image if it is not a part of the subset.
            if image not in subsetofimages:
                continue
            # Loading the annotations from imageid
            imageAnnotations = object_annotations.loadAnns(object_annotations.getAnnIds(image, iscrowd=None))
            stuffInImage = stuff_annotations.loadAnns(stuff_annotations.getAnnIds(image, iscrowd=None))

            objects = []
            for label in imageAnnotations:
                # If there is a duplicate we do not want to append it.
                if lookup[str(label['category_id'])] in objects:
                    continue
                objects.append(lookup[str(label['category_id'])])

            stuff = []
            for label in stuffInImage:
                if lookup[str(label['category_id'])] in stuff:
                    continue
                stuff.append(lookup[str(label['category_id'])])

            imagesAndObjects[str(image)] = objects
            imagesAndStuff[str(image)] = stuff

        lowHighEuclidian = {}
        for key, value in imagesAndObjects.items():
            # If there are less than three unique objects in the image we skip
            low, high, lowExcluded, highExcluded = self.GetLowestAndHighestEucDistance(value, imagesAndStuff[key])
            lowHighEuclidian[key] = {'low': low, 'high': high, 'object': value, 'lowexcluded': lowExcluded,
                                     'highexcluded': highExcluded}
        # We check for the delta in the images and find the largest delta.
        highestDelta = 0.0
        for key, value in lowHighEuclidian.items():
            delta = value['high'] - value['low']
            if delta > highestDelta:
                highestDelta = delta

        # Once we have found the highest delta we will remove the images using a threshold.
        amountOfImages = len(lowHighEuclidian)
        # Images to be removed from the dataset {<image>: Reason for removal}
        toBeRemoved = []
        # Starting delta value.
        previousDelta = highestDelta + 0.01
        while len(toBeRemoved) / amountOfImages * 100 < percentagetoremove:
            previousDelta -= 0.01
            highestDelta -= 0.01
            for key, value in lowHighEuclidian.items():
                delta = value['high'] - value['low']
                if delta >= highestDelta and delta < previousDelta:
                    toBeRemoved.append(int(key))

        print(f"Done removing {percentagetoremove}% of anomalous pictures.")
        print(f"The delta for the last itteration was: {highestDelta}")
        # We remove all the anomalous images from the subsetofimages list.
        for i in subsetofimages:
            if i in toBeRemoved:
                continue
            subset.append(i)

        # We save the new list of images to be used in the folder we were given.
        subsetDict["images"] = subset
        with open(f"{pathtofiles}image_list.json", "w") as f:
            f.write(json.dumps(subsetDict))
        print(f"Saved a new subset where {percentagetoremove}% of images are removed to {pathtofiles}image_list.json")
        return subset

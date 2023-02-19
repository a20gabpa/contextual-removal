import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import json
import networkx as nx
import os
import math
from StuffObject import StuffObjectNode

class CoOccuranceGraph:
    def __init__(self, omit):
        # If we do not have a Co_occurance.txt or IdLookup.txt file yet we will call the function that creates them.
        if not os.path.isfile("./Co_occurance.txt") or not os.path.isfile("./IdLookup.txt"):
            from BuildCoOccurance import CreateCoOccurance
            CreateCoOccurance()

        # TODO: Co_occurance is misspelled
        with open("Co_occurance.txt", "rb") as f:
            stuffAndObjects = pickle.load(f)

        with open("IdLookup.txt", "r") as f:
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
            # For every weighted relation in stuffandobject
            for key, value in i.otherStuffObjects.items():
                shouldContinue = False
                # Skipping stuff/objects we dont want.
                for j in omit:
                    if key == j:
                        shouldContinue = True
                if shouldContinue:
                    continue
                # Only allow edges with a significant enough weight.
                if (value / sumCoOccurance) * 100 > 0.5:
                    fromX.append(i.name)
                    toY.append(str(lookup[str(key)]))
                    weight.append((value / sumCoOccurance) * 100)

        df = pd.DataFrame({'from': fromX, 'to': toY, 'weight': weight})
        G = nx.from_pandas_edgelist(df, 'from', 'to', 'weight')

        # pos = nx.spring_layout(G, seed=1337)

        plt.title("Co-Occurance clustering")
        plt.figure(figsize=(150, 150))
        nx.draw_spring(G, node_size=10000, node_color="cyan", with_labels=True)

        plt.savefig('CoOccuranceGraph.pdf')

        self.nodes = nx.spring_layout(G, seed = 1337)


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

        #Centroid is the center of all the nodes given.
        centroid = [sumX/amountOfNodes, sumY/amountOfNodes]
        return centroid


    def GetEuclideanDistance(self, centroid, object):
        centroidX = centroid[0]
        centroidY = centroid[1]
        objectX = object[0]
        objectY = object[1]
        # square((objectX - centroidX)^2 + (objectY - centroidY)^2)
        return math.sqrt((objectX - centroidX)**2 + (objectY - centroidY)**2)

    def FindEuclideanDistance(self, objects):
        nodePositions = self.PositionOfObjects(objects)
        centroid = graph.GetCentroid(nodePositions)
        eucDistance = 0
        for key, value in nodePositions.items():
            eucDistance += self.GetEuclideanDistance(centroid, value)
        return eucDistance

    def GetLowestAndHighestEucDistance(self, objects):
        #If there is only one object we return an error
        if len(objects) <= 1:
            return 0, 0

        #Setting highest and lowest to values that realistically shouldnt be retained.
        lowest = 100000
        highest = -10000
        lowestRemoved = ""
        highestRemoved = ""

        # Get the combinations with the lowest and highest euclidian distances.
        # With an input of [person, horse, dog] the combinations could include:
        #       [person, horse], [horse,dog], [person, dog]
        for object in objects:
            removed = objects.pop(0)
            print(objects)
            hightOrLow = self.FindEuclideanDistance(objects)
            if hightOrLow < lowest:
                lowest = hightOrLow
                lowestRemoved = removed
            if hightOrLow > highest:
                highest = hightOrLow
                highestRemoved = removed
            objects.append(removed)
        return lowest, highest, lowestRemoved, highestRemoved


toOmit = [1, 183, 181, 167, 172, 105, 132]
graph = CoOccuranceGraph(toOmit)
toPrint = ['bus', 'car', 'elephant']
print(graph.PositionOfObjects(toPrint))

printXY = graph.PositionOfObjects(toPrint)

print(graph.GetCentroid(printXY))
centroid = graph.GetCentroid(printXY)
for key, value in printXY.items():
    print(key)
    print(graph.GetEuclideanDistance(centroid, value))

print("Euc distance between car and bus")
toTest = ['bus', 'car']
positionObj = graph.PositionOfObjects(toTest)
centroid = graph.GetCentroid(positionObj)
simDistance = 0
for key, value in positionObj.items():
    simDistance += graph.GetEuclideanDistance(centroid, value)
print(f"Sum of Euc Distance for: 'bus', 'car' = {simDistance}")

print("Euc distance between car and elephant")
toTest = ['car', 'elephant']
positionObj = graph.PositionOfObjects(toTest)
centroid = graph.GetCentroid(positionObj)
simDistance = 0
for key, value in positionObj.items():
    simDistance += graph.GetEuclideanDistance(centroid, value)
print(f"Sum of Euc Distance for: 'car', 'elephant' = {simDistance}")

print("Euc distance between bus and elephant")
toTest = ['bus', 'elephant']
positionObj = graph.PositionOfObjects(toTest)
centroid = graph.GetCentroid(positionObj)
simDistance = 0
for key, value in positionObj.items():
    simDistance += graph.GetEuclideanDistance(centroid, value)
print(f"Sum of Euc Distance for: bus and elephant = {simDistance}")


print("Euc distance between bed, pillow, tv, remote, carpet")
toTest = ['bed', 'pillow', 'tv', 'remote', 'carpet']
positionObj = graph.PositionOfObjects(toTest)
centroid = graph.GetCentroid(positionObj)
simDistance = 0
for key, value in positionObj.items():
    simDistance += graph.GetEuclideanDistance(centroid, value)
print(f"Sum of Euc Distance for: 'bed', 'pillow', 'tv', 'remote', 'carpet' = {simDistance}")

print("Euc distance between snowboard, pillow, tv, remote, carpet")
toTest = ['snowboard', 'pillow', 'tv', 'remote', 'carpet']
positionObj = graph.PositionOfObjects(toTest)
centroid = graph.GetCentroid(positionObj)
simDistance = 0
for key, value in positionObj.items():
    simDistance += graph.GetEuclideanDistance(centroid, value)
print(f"Sum of Euc Distance for: 'snowboard', 'pillow', 'tv', 'remote', 'carpet' = {simDistance}")

# New version that does it all.
print("Euc distance between snowboard, pillow, tv, remote, carpet, Test 2")
toTest = ['snowboard', 'pillow', 'tv', 'remote', 'carpet']
print(f"Sum of Euc Distance for: 'snowboard', 'pillow', 'tv', 'remote', 'carpet' = {graph.FindEuclideanDistance(toTest)}")

print("Tesing if the function does what it should")
toTest = ['bed', 'snowboard', 'pillow', 'tv', 'remote', 'carpet']
a, b ,c ,d = graph.GetLowestAndHighestEucDistance(toTest)
print(a)
print(c)

print(b)
print(d)
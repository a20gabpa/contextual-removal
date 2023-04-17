import matplotlib as plt
import json

with open("./image_list.json") as f:
    default = json.load(f)
    
with open("./SubsetEuclidian/five/image_list.json") as f:
    euc = json.load(f)
    
with open("./SubsetKMeans/five/image_list.json") as f:
    kmeans = json.load(f)
    
with open("./SubsetRandom/five/image_list.json") as f:
    random = json.load(f)

notInEuc = []
notInKmeans = []
notInRandom = []

for i in default["images"]:
    if i not in euc:
        notInEuc.append(i)
    
    if i not in kmeans:
        notInKmeans.append(i)
        
    if i not in random:
        notInRandom.append(i)

inKMeansNotInEuc = []
inEucNotInKMeans = []
inBoth = []
    
for i in kmeans["images"]:
    if i not in euc["images"]:
        inKMeansNotInEuc.append(i)
        
for i in euc["images"]:
    if i not in kmeans["images"]:
        inEucNotInKMeans.append(i)

inRandNotInEuc = []
inRandNotInKmeans = []

for i in random["images"]:
    if i not in euc["images"]:
        inRandNotInEuc.append(i)
    if i not in kmeans["images"]:
        inRandNotInKmeans.append(i)
        
print(len(kmeans["images"]))
print(len(euc["images"]))
print(f"In Kmeans not in euclidian: {inKMeansNotInEuc}")
print(f"In Euclidian not in kmeans: {len(inEucNotInKMeans)}")

print("Random aggreement")
print(f"In Rand not in euc: {len(inRandNotInEuc)}")
print(f"In Rand not in kmeans: {len(inRandNotInKmeans)}")

print(f"Amount of images in both: {len(inBoth)}") 
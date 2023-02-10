import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import json
import networkx as nx
import os
from StuffObject import StuffObjectNode

def CreateGraph():
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
        if i.id == 1 or i.id == 183 or key == 181 or key == 167 or key == 172 or key == 105 or key == 132:
            continue

        sumCoOccurance = 0
        # Need to get sum to extract percentage.
        for key, value in i.otherStuffObjects.items():
            # Skipping stuff/objects we dont want.
            if key == 1 or key == 183 or key == 181 or key == 167 or key == 172 or key == 105 or key == 132:
                continue

            sumCoOccurance += value
        # For every weighted relation in stuffandobject
        for key, value in i.otherStuffObjects.items():
            # Skipping stuff/objects we dont want.
            if key == 1 or key == 183 or key == 181 or key == 167 or key == 172 or key == 105 or key == 132:
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
    nx.draw(G, node_size=10000, node_color="cyan", with_labels=True)

    plt.savefig('CoOccuranceGraph.pdf')


CreateGraph()

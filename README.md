# Context-CV
## Steps for replication:
    1. Create a virutual environment using the listed libraries below, (virtualenv python= "<Path/To/Python3.8.9.exe>").
    2. Download the dataset from https://cocodataset.org/#download according the instructions in README.txt in ./dataset
    3. Activate virtual environment
    4. Run the create_subset.py
    5. Through the terminal, run:
            from CoOccuranceGraph import CoOccuranceGraph
            CoOccuranceGraph()
    6. Run all of the following notesbooks, CreateSubsetEuclidean.ipynb, CreateSubsetRandom.ipynb, CreateSubsetKMeans.ipynb
    7. Run the preprocess_subset.py and change the path to the wanted .json file on line 182. 
    8. Through the terminal, run train.py
    9. After the finished training, run predict.py and on line 9, change the path to the best weight generated from the training
    9. Finally run ConvertYOLOtoCOCO.py and zip the file called detections_test-dev2017_yolo_results.json
    10. Upload the result to https://codalab.lisn.upsaclay.fr/competitions/7384

## Libraries and versions (as of 31-04-2023)

    - Python                       3.8.9
    - jupyter_core                 5.2.0
    - keras                        2.11.0
    - matplotlib                   3.7.0
    - networkx                     3.0
    - numba                        0.56.4
    - numpy                        1.23.5
    - onnx                         1.13.0
    - opencv-python                4.7.0.72
    - pandas                       1.5.3
    - Pillow                       9.4.0
    - pip                          23.0
    - pycocotools                  2.0.6
    - scikit-learn                 1.2.2
    - tensorflow                   2.11.0
    - torch                        1.13.1
    - ultralytics                  8.0.56

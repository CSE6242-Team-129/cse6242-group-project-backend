# Model

*note*: this is currently using Python 3.9.15

## How to use
1. Please refer to the 'requirements.txt' to check all the necessary libraries and their version to run the files.
2. 'prediction.py' contains a class to train a classification model using historical data('la_final_data.csv') and xgboost.
Also, it contains a function to read and transform an input data(here, the sample data is 'sample_test_data.csv'.
In reality we will use retrieved data from APIs) and generate output of prediction results.
3. 'perform.py' include a sample code of calling a class in 'prediction.py', train a model, read an input, and delivers the output.

## Data
1. 'la_final_data,csv': This data can be directly fed into 'Prediction()' class of 'prediction.py' without any cleaning procedure.
2. 'sample_test_data.csv': This is just a sample input data for testing purpose only. In reality, we will use retrieved data from APIs.

## Outputs
1. As a result of prediction, we will generate 'prediction_results.csv' in the same folder.
This file will contain predicted labels(1: high probability of accident, 0: low probability of accident)
as well as the time information and geo information of latitude and longitude.
import copy
import csv
import random

from fastapi import FastAPI


app = FastAPI()


data = None
with open('../data/transformed-data.csv') as f:
    reader = csv.DictReader(f)
    data = [row for row in reader]


max_predictions = 25
min_predictions = 0
max_predictions = len(data)

def make_prediction(data: dict):
    data_copy = copy.deepcopy(data)
    data_copy.update({'predictions': {
        'linear': random.randint(min_predictions, max_predictions),
        'decision_tree': random.randint(min_predictions, max_predictions)
    }})
    return data_copy


def make_predictions(num_predictions: int=max_predictions) -> list:
    """
    Make `num_predictions` number of predictions and shuffle them
    """
    return {
        'results': random.sample(
            [make_prediction(row) for row in data[0:num_predictions]],
            k=num_predictions
        )
    }


def make_random_number_of_predictions():
    num_predictions = random.randint(2, max_predictions)
    return make_predictions(num_predictions)


@app.get('/')
async def home():
    return make_predictions()


@app.get('/predict/days/{number_of_days}')
async def predict_number_of_days(number_of_days: int):
    return make_random_number_of_predictions()


@app.get('/predict/days/{number_of_hours}')
async def predict_number_of_hours(number_of_hours: int):
    return make_random_number_of_predictions()


@app.get('/predict/area/{area_name}')
async def predict_area(area_name: str):
    return make_random_number_of_predictions()


@app.get('/predict/zip/{zip_code}')
async def predict_zip_code(zip_code: int):
    return make_random_number_of_predictions()

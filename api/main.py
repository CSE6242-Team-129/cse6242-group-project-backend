import csv
import random

from fastapi import FastAPI


app = FastAPI()


data = None
with open('../data/sample.csv') as f:
    reader = csv.DictReader(f)
    data = [row for row in reader]


max_crashes = 25
min_crashes = 0
max_predictions = len(data)

def make_prediction(data):
    return {
        'latitude': data['latitude'],
        'longitude': data['longitude'],
        'predictions': {
            'linear': random.randint(min_crashes, max_crashes),
            'decision_tree': random.randint(min_crashes, max_crashes)
        },
        'street': data['street'],
        'cross_street': data['cross_street'],
        'area_id': data['area_id'],
        'time': data['time'],
        'date': data['date'],
    }


def make_predictions(num_predictions: int=max_predictions) -> list:
    """
    Make `num_predictions` number of predictions and shuffle them
    """
    return random.sample(
        [make_prediction(row) for row in data[0:num_predictions]],
        k=num_predictions
    )


def make_random_number_of_predictions():
    num_predictions = random.randint(2, max_predictions)
    return make_predictions(num_predictions)


@app.get('/')
def home():
    return make_predictions()


@app.get('/predict/days/{number_of_days}')
def predict_number_of_days(number_of_days: int):
    return make_random_number_of_predictions()


@app.get('/predict/days/{number_of_hours}')
def predict_number_of_hours(number_of_hours: int):
    return make_random_number_of_predictions()


@app.get('/predict/area/{area_name}')
def predict_area(area_name: str):
    return make_random_number_of_predictions()


@app.get('/predict/zip/{zip_code}')
def predict_zip_code(zip_code: int):
    return make_random_number_of_predictions()

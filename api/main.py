import copy
from datetime import datetime, timedelta
import random

from fastapi import FastAPI

from models import Classifier, InputData
import utils
import weather as wt


app = FastAPI()
classifier = Classifier.load_model(path="model.json")


max_predictions = 25
min_predictions = 0
conn = utils.connect_to_db("locations.db")


def make_prediction(data: dict):
    data_copy = copy.deepcopy(data)
    data_copy.update(
        {
            "predictions": {
                "linear": random.randint(min_predictions, max_predictions),
                "decision_tree": random.randint(min_predictions, max_predictions),
            }
        }
    )
    return data_copy


def make_predictions(num_predictions: int = max_predictions) -> list:
    """
    Make `num_predictions` number of predictions and shuffle them
    """
    data = utils.get_random_entries(conn, max_predictions)
    return {
        "results": random.sample(
            [make_prediction(row) for row in data[0:num_predictions]], k=num_predictions
        )
    }


def make_random_number_of_predictions():
    num_predictions = random.randint(2, max_predictions)
    return make_predictions(num_predictions)


@app.get("/")
async def home():
    # just serve the sample predictions for now
    sample_data = InputData(path="sample_test_data.csv")
    prediction = classifier.predict(data=sample_data, type_="dict")
    return prediction


@app.get("/predict/days/{number_of_days}")
async def predict_number_of_days(number_of_days: int):
    return make_random_number_of_predictions()


@app.get("/predict/days/{number_of_hours}")
async def predict_number_of_hours(number_of_hours: int):
    return make_random_number_of_predictions()


@app.get("/predict/area/{area_name}")
async def predict_area(area_name: str):
    return make_random_number_of_predictions()


@app.get("/predict/zip/{zip_code}")
async def predict_zip_code(zip_code: str):
    locations = utils.get_locations_by_zip(conn, zip_code)
    start = datetime.now()
    end = start + timedelta(hours=1)
    weather_data = wt.get_hourly_data()
    return make_random_number_of_predictions()

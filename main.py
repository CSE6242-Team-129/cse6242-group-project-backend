from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from models import Classifier, InputData
import utils
import weather as wt


app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:63342",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = Classifier.load_model(path="model.json")

conn = utils.connect_to_db("locations.db")
model_data = utils.get_all_model_data(conn=conn)


@app.get("/")
async def home():
    # just serve the sample predictions for now
    data = InputData(path="sample_test_data.csv")
    prediction = classifier.predict(data.data_ohe, data.index, "list")
    return prediction


@app.get("/predict/zip/{zip_code}")
async def predict_zip_code(zip_code: str):
    # faster to filter before creating DataFrame
    locations = pd.DataFrame([d for d in model_data if d["Zip_Code"] == zip_code])
    weather = wt.get_weather_by_zip(zip_code, type_="tuple")
    prediction = utils.make_prediction(locations, weather, classifier)
    [p.update({"zip_code": zip_code}) for p in prediction]
    return prediction


@app.get("/predict/coords/")
async def predict_by_coords(lat: float, lon: float):
    closest = pd.DataFrame(utils.get_closest_match(conn, (lat, lon))[1], index=[0])
    closest[["Start_Lat", "Start_Lng"]] = lat, lon
    weather = wt.get_weather_by_lat_lon(lat, lon)
    prediction = utils.make_prediction(closest, weather, classifier)
    return prediction


@app.get("/zip_codes")
async def get_all_zip_codes():
    zips = utils.get_all_zip_codes(conn)
    return zips


@app.get("/predict/all")
async def get_all_predictions():
    md = pd.DataFrame(model_data)
    weather = wt.get_la_weather("tuple")
    prediction = utils.make_prediction(md, weather, classifier)
    return prediction

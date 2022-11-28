from datetime import datetime

from fastapi import FastAPI
import pandas as pd

from models import Classifier, InputData
import utils
import weather as wt


app = FastAPI()
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
    columns = [
        "Temperature(F)",
        "Humidity(%)",
        "Pressure(in)",
        "Wind_Speed(mph)",
        "Precipitation(in)",
    ]
    locations[columns] = weather
    locations["Start_Time"] = datetime.now()
    # strip the zip code for prediction
    locations = locations.loc[:, locations.columns != "Zip_Code"]
    idata = InputData(data=locations)
    prediction = classifier.predict(idata.data_ohe, idata.index, type_="list")
    [p.update({"zip_code": zip_code}) for p in prediction]
    return prediction


@app.get("/predict/coords/")
async def predict_by_coords(lat: float, lon: float):
    closest = pd.DataFrame(utils.get_closest_match(conn, (lat, lon))[1], index=[0])
    closest[["Start_Lat", "Start_Lng"]] = lat, lon
    weather = wt.get_weather_by_lat_lon(lat, lon)
    columns = [
        "Temperature(F)",
        "Humidity(%)",
        "Pressure(in)",
        "Wind_Speed(mph)",
        "Precipitation(in)",
    ]
    closest[columns] = weather
    closest["Start_Time"] = datetime.now()
    idata = InputData(data=closest)
    prediction = classifier.predict(idata.data_ohe, idata.index, type_="list")
    return prediction

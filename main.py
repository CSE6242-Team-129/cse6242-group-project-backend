from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from classifier import Classifier, InputData
import utils
import weather as wt


app = FastAPI()
origins = [
    "http://localhost",
    "https://localhost:5500",
    "http://localhost:63342",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = Classifier.load_model(path="model.json")

conn = utils.connect_to_db()
model_data = utils.get_all_model_data(conn=conn)
zip_codes = utils.get_all_zip_codes(conn=conn)


@app.get("/")
async def home():
    # just serve the sample predictions for now
    data = InputData(path="sample_test_data.csv")
    weather = wt.get_la_weather()
    prediction = classifier.predict(data.data_ohe, data.index, "list")
    return {"predictions": prediction, "weather": weather.to_dict("index")[0]}


@app.get("/predict/zip/{zip_code}")
async def predict_zip_code(zip_code: str):
    if zip_code not in zip_codes:
        raise HTTPException(status_code=404, detail=f"{zip_code} not found in database")
    # faster to filter before creating DataFrame
    ls = [d for d in model_data if d["Zip_Code"] == zip_code]
    locations = None
    if ls:
        locations = pd.DataFrame(ls)
    else:
        raise HTTPException(status_code=404, detail=f"Nothing found for {zip_code}")
    cols = list(locations.columns)
    if not 'Start_Lat' in cols and 'Start_Lng' in cols:
        print(zip_code)
        raise HTTPException(status_code=404, detail=f"{zip_code} failed")
    weather = wt.get_weather_by_zip(zip_code)
    w_tuple = tuple(weather.values[0])
    prediction = utils.make_prediction(locations, w_tuple, classifier)
    [p.update({"zip_code": zip_code}) for p in prediction]
    return {"predictions": prediction, "weather": weather.to_dict("index")[0]}


@app.get("/predict/coords/")
async def predict_by_coords(lat: float, lon: float):
    closest = pd.DataFrame(utils.get_closest_match(conn, (lat, lon))[1], index=[0])
    closest[["Start_Lat", "Start_Lng"]] = lat, lon
    weather = wt.get_weather_by_lat_lon(lat, lon)
    prediction = utils.make_prediction(closest, weather, classifier)
    return {"predictions": prediction, "weather": weather.to_dict("index")[0]}


@app.get("/zip_codes")
async def get_all_zip_codes():
    return zip_codes


@app.get("/predict/all")
async def get_all_predictions():
    md = pd.DataFrame(model_data)
    zip_codes = tuple(md["Zip_Code"])
    weather = wt.get_la_weather()
    w_tuple = tuple(weather.values[0])
    prediction = utils.make_prediction(md, w_tuple, classifier)
    [p.update({"zip_code": zc}) for zc, p in zip(zip_codes, prediction)]
    return {"predictions": prediction, "weather": weather.to_dict("index")[0]}

# Abstract

[Insert abstract text here]

## Installing

### Using Make

Run

```
make setup
```

### Using pip

Run

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Running

### Using Make

Run

```bash
make run
```

to serve the API on port `8000`. To run another port, use the `port=<port-number>` parameter. For example,
to run the API on port `5500` run

```bash
make run port=5500
```

### Using Python

```bash
uvicorn main:app --reload --port <port>
```

or, if that doesn't work

```bash
python -m uvicorn main:app --reload --port <port>
```

where `<port>` is the desired port number.

## Endpoints:


- `/` -> prediction of data points in sample_test_data.csv
- `/predict/zip/{zip_code}` -> prediction for given zip code. Pulls the model data and gives a prediction for each point within the given zip code
- `/predict/coords?lat=<latitude>&lon=<longitude>` -> prediction for given latitude-longitude pair. This will get the data for the closest matching location (could be within a few feet to a couple of miles so the accuracy varies wildly)
- `/predict/all` -> prediction for every data point in our database (~257K data points). This endpoint uses the current weather for Los Angeles instead of each latitude-longitude pair. This was done as a sacrifice of accuracy for speed
- `/zip_codes` -> gives a list of every zip code that is in the database


Returns a JSON response with the following format:

```json
{
    "predictions": [
        {
            "time": "2022-11-29T21:54:46.271963",
            "lat": 34.1404637,
            "lon": -118.2037924,
            "label": 1,
            "probability": 0.9999909400939941
        }
    ],
    "weather": {
        "Temperature(F)": 52.66,
        "Humidity(%)": 79,
        "Pressure(in)": 14.779345474708322,
        "Wind_Speed(mph)": 2.2593094000000002,
        "Precipitation(in)": 0
    }
}
```

NOTE: the `zip_code` key is only present when using the zip code prediction endpoint.
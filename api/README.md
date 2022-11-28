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

## Endpoints:


- `/` -> prediction of data points in sample_test_data.csv
- `/predict/zip/{zip_code}` -> prediction for given zip code. Pulls the model data and gives a prediction for each point within the given zip code
- `/predict/coords?lat=<latitude>&lon=<longitude>` -> prediction for given latitude-longitude pair. This will get the data for the closest matching location (could be within a few feet to a couple of miles so the accuracy varies wildly)


Returns a JSON response with the following format:

```json
[
   {
       "lat": 34.1735806,
       "lon": -118.1303262,
       "zip_code": 91104,
       "label": 0,
       "probability": 0.9742215871810913,
   }
]
```

NOTE: the `zip_code` key is only present when using the zip code prediction endpoint.
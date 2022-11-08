"""
Used to classify locations as being an area of high-probability of accidents (1)
or not (0). Adapted from prediction.py
"""
import pandas as pd
from xgboost import XGBClassifier


SELECTED_FEATURES = [
    "Start_Lat",
    "Start_Lng",
    "Temperature(F)",
    "Humidity(%)",
    "Pressure(in)",
    "Wind_Speed(mph)",
    "Precipitation(in)",
    "Junction",
    "Railway",
    "Station",
    "Turning_Loop",
    "Start_Month",
    "Start_Hour",
    "Start_Day_0",
    "Start_Day_1",
    "Start_Day_2",
    "Start_Day_3",
    "Start_Day_4",
    "Start_Day_5",
    "Start_Day_6",
]


class Data:
    def __init__(self, path: str) -> None:
        self._training_data = pd.read_csv(path)
        self.features = None
        self.target = None
        self.preprocess()

    def preprocess(self) -> 'Data':
        self._training_data.dropna(axis=0, inplace=True)  # drop rows with null

        # Extract month, hour, day of week from 'Start_Time' column
        self._training_data["Start_Time"] = pd.to_datetime(self._training_data["Start_Time"])
        self._training_data["Start_Month"] = self._training_data["Start_Time"].dt.month
        self._training_data["Start_Hour"] = self._training_data["Start_Time"].dt.hour
        self._training_data["Start_Day"] = self._training_data["Start_Time"].dt.dayofweek
        self._training_data["Start_Day"] = self._training_data["Start_Day"].astype(object)

        # Drop 'Start_Time' column
        self._training_data.drop("Start_Time", axis=1, inplace=True)

        # Target labels and features
        self.target = self._training_data["Target"]
        x_features = self._training_data.drop("Target", axis=1, inplace=False)
        x_features_ohe = pd.get_dummies(x_features)

        # Features after performing feature selection based on p-values
        self.features = x_features_ohe[SELECTED_FEATURES]
        return self

    def input_data(self, path: str) -> 'Data':
        input_data = pd.read_csv(path)
        input_data.dropna(axis=0, inplace=True)  # drop rows with null

        # Extract month, hour, day of week from 'Start_Time' column
        input_data["Start_Time"] = pd.to_datetime(input_data["Start_Time"])
        input_data["Start_Month"] = input_data["Start_Time"].dt.month
        input_data["Start_Hour"] = input_data["Start_Time"].dt.hour
        input_data["Start_Day"] = input_data["Start_Time"].dt.dayofweek
        input_data["Start_Day"] = input_data["Start_Day"].astype(object)

        # Separately save 'Start_Time', 'Start_Lat', 'Start_Lng' column to output 
        # with the prediction
        self.index_df = input_data[["Start_Time", "Start_Lat", "Start_Lng"]]

        # Drop 'Start_Time' column since you don't need this when modeling
        input_data.drop("Start_Time", axis=1, inplace=True)
        self.input_data = input_data

        # one-hot-encoding of categorical features
        input_features_ohe = pd.get_dummies(self.input_data)

        # Features after performing feature selection based on p-values
        self.input_features = input_features_ohe[self.selected_features]

        return self


class Classifier:
    def __init__(self, path: str, *args, **kwargs) -> None:
        self._classifier = XGBClassifier(*args, **kwargs)
        self._current_prediction = None
        self._index_df = None
        self._data = Data(path=path)

    def fit(self) -> 'Classifier':
        features = self._data.features
        target = self._data.target
        self._classifier.fit(features, target)
        return self

    def predict(self, data: str) -> pd.DataFrame:
        prediction = self._classifier(data)
        output = self._index_df.copy()
        output["Pred Label"] = prediction
        self._current_prediction = output
        return self._current_prediction

    def to_csv(self, path="results.csv"):
        self._current_prediction.to_csv(path, index=False)

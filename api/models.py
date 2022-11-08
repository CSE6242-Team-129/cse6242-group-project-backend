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
    def __init__(self, path: str, dropcol=True) -> None:
        data = pd.read_csv(path)
        self._data = _preprocess(data, dropcol)

    @property
    def data(self) -> pd.DataFrame:
        return self._data


class TrainingData(Data):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._target = self.data["Target"]
        self._features = self._process_features()

    @property
    def features(self) -> pd.DataFrame:
        return self._features

    @property
    def target(self) -> pd.DataFrame:
        return self._target

    def _process_features(self):
        features = self.data.drop('Target', axis=1, inplace=False)
        features_ohe = pd.get_dummies(features)

        # Features after performing feature selection based on p-values
        return features_ohe[SELECTED_FEATURES]


class InputData(Data):
    def __init__(self, path: str) -> None:
        super().__init__(path, dropcol=False)
        columns = ["Start_Time", "Start_Lat", "Start_Lng"]
        self._index = self._data[columns]
        self._data_ohe = pd.get_dummies(self.data)[SELECTED_FEATURES]
        self._data = self.data.drop("Start_Time", axis=1, inplace=True)

    @property
    def index(self) -> pd.DataFrame:
        return self._index

    @property
    def data_ohe(self) -> pd.DataFrame:
        self._data_ohe


class Classifier:
    def __init__(self, tdata: TrainingData, **kwargs) -> None:
        self._classifier = XGBClassifier(**kwargs)
        self._current_prediction = None
        self._tdata = tdata

    def fit(self) -> 'Classifier':
        features = self._tdata.features
        target = self._tdata.target
        # TODO: fix the following error:
        # Exception has occurred: TypeError
        #   '<' not supported between instances of 'Timestamp' and 'int'
        self._classifier.fit(features, target)
        return self

    def predict(self, data: InputData) -> pd.DataFrame:
        prediction = self._classifier.predict(data._data_ohe)
        output = data.index.copy()
        output["Pred Label"] = prediction
        self._current_prediction = output
        return self._current_prediction

    def to_csv(self, path="results.csv"):
        self._current_prediction.to_csv(path, index=False)


def _get_time_data(data: pd.DataFrame, dropcol=True) -> list:
    """
    Extracts the hour, day, and month of week from the `Start_Time` column
    formatted as `yyyy-mm-dd HH:MM:SS` and drops the original column and puts
    the data into `Start_Hour`, `Start_Day`, and `Start_Month` columns
    respectively. This may drop the `Start_Time` column if `dropcol` is True.

    Args
    ----
    data (pd.DataFrame): the DataFrame with the `Start_Time` column to be
    processed.

    dropcol (bool): drops the `Start_Time` column if True, leaves it in if
    False.

    Returns
    -------
    A new DataFrame with `Start_Hour`, `Start_Day`, and `Start_Month` columns
    containing hour, day, and month of week, respectively.
    """
    data_copy = data.copy()
    # Extract month, hour, day of week from 'Start_Time' column
    data_copy["Start_Time"] = pd.to_datetime(data_copy["Start_Time"])
    data_copy["Start_Month"] = data_copy["Start_Time"].dt.month
    data_copy["Start_Hour"] = data_copy["Start_Time"].dt.hour
    data_copy["Start_Day"] = data_copy["Start_Time"].dt.dayofweek
    data_copy["Start_Day"] = data_copy["Start_Day"].astype(object)

    if dropcol:
        # Drop 'Start_Time' column since you don't need this when modeling
        data_copy.drop("Start_Time", axis=1, inplace=True)

    return data_copy


def _preprocess(data: pd.DataFrame, dropcol=True) -> pd.DataFrame:
    data.dropna(axis=0, inplace=True)  # drop rows with null
    return _get_time_data(data, dropcol=dropcol)

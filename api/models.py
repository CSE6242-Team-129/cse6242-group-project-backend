"""
Used to classify locations as being an area of high-probability of accidents (1)
or not (0). Adapted from prediction.py
"""
from os import PathLike
from typing import Union

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
    def __init__(
        self, path: Union[str, PathLike] = None, dropcol=True, data: pd.DataFrame = None
    ) -> None:
        data = pd.read_csv(path) if path else data
        self._data = _preprocess(data, dropcol)

    @property
    def data(self) -> pd.DataFrame:
        return self._data


class TrainingData(Data):
    def __init__(self, path: Union[str, PathLike]) -> None:
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
        features = self.data.drop("Target", axis=1, inplace=False)
        features_ohe = pd.get_dummies(features)

        # Features after performing feature selection based on p-values
        return features_ohe[SELECTED_FEATURES]


class InputData(Data):
    def __init__(
        self,
        path: Union[str, PathLike] = None,
        dropcol=False,
        data: pd.DataFrame = None,
    ) -> None:
        super().__init__(path=path, dropcol=dropcol, data=data)
        columns = ["Start_Time", "Start_Lat", "Start_Lng"]
        self._index = self._data[columns]
        if path:
            self._data_ohe = pd.get_dummies(self.data)[SELECTED_FEATURES]
        else:
            self._data_ohe = self.data
            sd = self.data['Start_Day'].values[0]
            self._data_ohe[SELECTED_FEATURES[-7:]] = [1 if i == sd else 0 for i in range(7)]
            self._data_ohe = self._data_ohe[SELECTED_FEATURES]
            bool_data = self.data_ohe[["Junction", "Railway", "Station", "Turning_Loop"]].astype(bool)
            self.data_ohe[["Junction", "Railway", "Station", "Turning_Loop"]] = bool_data
        self._data = self.data.drop("Start_Time", axis=1, inplace=True)

    @property
    def index(self) -> pd.DataFrame:
        return self._index

    @property
    def data_ohe(self) -> pd.DataFrame:
        return self._data_ohe


class Classifier:
    def __init__(
        self, features: pd.DataFrame = None, target: pd.DataFrame = None, **kwargs
    ) -> None:
        self._classifier = XGBClassifier(**kwargs)
        self._current_prediction = None
        self._features = features
        self._target = target

    def fit(self) -> "Classifier":
        features = self._features
        target = self._target
        self._classifier.fit(features, target)
        return self

    def predict(
        self, data: pd.DataFrame, index: pd.DataFrame, type_: str = "dict"
    ) -> pd.DataFrame:
        prediction = self._classifier.predict(data)
        output = index.copy()
        output["Pred_Label"] = prediction
        proba = self._classifier.predict_proba(data)[:, 1]
        output["Pred_Proba"] = proba
        self._current_prediction = output
        if type_ == "list":
            return output.to_dict("records")
        elif type_ == "dict":
            return output.to_dict(orient="index")
        elif type_ == "pd":
            return self._current_prediction
        else:
            raise ValueError(f"'type_' must be either 'pd' or 'dict' not {type_}")

    @property
    def feature_names(self) -> list:
        """
        Returns a list of the feature names of the model
        """
        return list(self._classifier.feature_names_in_)

    @staticmethod
    def load_model(path: Union[str, PathLike] = "model.json") -> "Classifier":
        classifier = Classifier()
        classifier._classifier.load_model(path)

        return classifier

    def save_model(self, path: Union[str, PathLike] = "model.json") -> None:
        self._classifier.save_model(path)

    def to_csv(self, path: Union[str, PathLike] = "results.csv"):
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

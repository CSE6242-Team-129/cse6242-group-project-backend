import warnings

warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)


class Prediction:
    def train_model(self):

        hist_data = pd.read_csv("la_final_data.csv")
        hist_data.dropna(axis=0, inplace=True)  # drop rows with null

        # Extract month, hour, day of week from 'Start_Time' column
        hist_data["Start_Time"] = pd.to_datetime(hist_data["Start_Time"])
        hist_data["Start_Month"] = hist_data["Start_Time"].dt.month
        hist_data["Start_Hour"] = hist_data["Start_Time"].dt.hour
        hist_data["Start_Day"] = hist_data["Start_Time"].dt.dayofweek
        hist_data["Start_Day"] = hist_data["Start_Day"].astype(object)

        # Drop 'Start_Time' column
        hist_data.drop("Start_Time", axis=1, inplace=True)
        self.hist_data = hist_data

        # Target labels and features
        self.y_target = self.hist_data["Target"]
        X_features = self.hist_data.drop("Target", axis=1, inplace=False)
        X_features_ohe = pd.get_dummies(X_features)

        # Feature selection
        self.selected_features = [
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

        # Features after performing feature selection based on p-values
        self.X_features_ohe = X_features_ohe[self.selected_features]

        # Train xgb classifier using the best params aquired thru cross validation
        self.xgb_clf = XGBClassifier(
            n_estimators=100, max_depth=7, min_child_weight=1, colsample_bytree=0.75
        )
        self.xgb_clf.fit(self.X_features_ohe, self.y_target)

        return self.xgb_clf

    def receive_input(self, path):
        # path is the path of the input data

        input_data = pd.read_csv(path)
        input_data.dropna(axis=0, inplace=True)  # drop rows with null

        # Extract month, hour, day of week from 'Start_Time' column
        input_data["Start_Time"] = pd.to_datetime(input_data["Start_Time"])
        input_data["Start_Month"] = input_data["Start_Time"].dt.month
        input_data["Start_Hour"] = input_data["Start_Time"].dt.hour
        input_data["Start_Day"] = input_data["Start_Time"].dt.dayofweek
        input_data["Start_Day"] = input_data["Start_Day"].astype(object)

        # Separately save 'Start_Time', 'Start_Lat', 'Start_Lng' column to output with the prediction
        self.index_df = input_data[["Start_Time", "Start_Lat", "Start_Lng"]]

        # Drop 'Start_Time' column since you don't need this when modeling
        input_data.drop("Start_Time", axis=1, inplace=True)
        self.input_data = input_data

        # one-hot-encoding of categorical features
        input_features_ohe = pd.get_dummies(self.input_data)

        # Features after performing feature selection based on p-values
        self.input_features_ohe = input_features_ohe[self.selected_features]

        return self.index_df, self.input_features_ohe

    def deliver_output(self):

        self.pred = self.xgb_clf.predict(self.input_features_ohe)
        self.output = self.index_df.copy()
        self.output["Pred Label"] = self.pred
        self.output.to_csv("prediction_results.csv", index=False)

import pandas as pd


# Load data
data_full = pd.read_csv("US_Accidents_Dec21_updated.csv")
print(data_full.head())
print(data_full.columns)

# Choose Los Angeles
data = data_full[data_full.loc[:, "County"] == "Los Angeles"]

# Choose columns
data_short = data[["ID", "Start_Time", "Start_Lat", "Start_Lng", "City", "County", "Zipcode"]]

# Save as csv
data_short = data_short.reset_index()
print(data_short.head())
data_short.to_csv("data_short.csv")

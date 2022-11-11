import pandas as pd
import folium
from folium import plugins


# Read data
data = pd.read_csv("vis_data_short.csv")

# Change datatype to float and str
data[["Start_Lat"]] = data[["Start_Lat"]].astype("float")
data[["Start_Lng"]] = data[["Start_Lng"]].astype("float")
data[["Start_Time"]] = data[["Start_Time"]].astype("str")
print(data.head())
print(data.dtypes)

# Create a folium map base
map_la = folium.Map([34.2012, -118.4662], zoom_start=11)

# Data for heatmap
heatmap_data = data[["Start_Lat", "Start_Lng"]].values
# Add child
map_la.add_child((plugins.HeatMap(heatmap_data, radius=15)))

# Save data as index.html
map_la.save("vis_index.html")

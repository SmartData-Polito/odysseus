import os.path

import pandas as pd

from odysseus.path_config.path_config import root_data_path

df = pd.read_csv(
    os.path.join(root_data_path, "Roma", "raw", "trips", "enjoy", "trips_202209281355.csv")
).rename(columns={
    "end_lat": "end_latitude",
    "end_lon": "end_longitude"
})

print(df.columns)

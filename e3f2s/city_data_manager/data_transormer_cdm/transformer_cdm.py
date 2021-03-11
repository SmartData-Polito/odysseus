import os
import pandas as pd
import json




def myfunc(a,b, *args, **kwargs):
      c = kwargs.get('c', None)
      d = kwargs.get('d', None)
      print(a,b)
      print(c,d)
a=1
b=2
myfunc(a,b, c='nick', d='dog')




ROOT_DIR = os.path.abspath(os.curdir) 

cdm_path,_ = os.path.split(ROOT_DIR)

root_data_path = os.path.join(
	cdm_path,
	"data"
)
# path_to__data_city_norm_trips_source_year_month_filetype = ''

# path_to__data_city_odtrips_points_year_month_filetype = ''
# path_to__data_city_odtrips_trips_year_month_filetype = ''

# path_to__data_city_raw_geo_trips = ''

# data_steps_ids = ["raw","norm","od_trips"]
# data_type_ids = ["points","trips","weather","geo"]
# data_source = ["big_data_db"]


def transform_cdm(city, data_steps_id, data_type_id, data_source, year, month, filetype):
    transformed_json={}

    path_to__data_city_norm_trips_source_year_month_filetype = os.path.join(
        root_data_path, city, data_steps_id, data_type_id, data_source, year+"_"+month + filetype

    )

    df = pd.read_csv(path_to__data_city_norm_trips_source_year_month_filetype)

    df = df.drop(df.columns[0], axis=1)

    print(df.head())

    result = df.to_json(orient="index")
    parsed = json.loads(result)

    return parsed

ppp = transform_cdm("Torino", "norm", "trips", "big_data_db", "2017", "10", ".csv")

print(type(ppp))



























# cities = [
# 	"Torino",
# 	"Louisville",
# 	"Minneapolis",
# 	"Milano",
# 	"New_York_City",
# 	"Berlin",
# 	"Vancouver",
# 	"Amsterdam",
# 	"Madrid",
# 	"Roma",
# 	"Austin",
# 	"Norfolk",
# 	"Kansas City",
# 	"Chicago",
# 	"Calgary"
# ]




# data_paths_dict = {}
# for city in cities:
# 	data_paths_dict[city] = {}
# 	for data_step_id in data_steps_ids:
# 		data_paths_dict[city][data_step_id] = {}
# 		for data_type_id in data_type_ids:
# 			data_paths_dict[city][data_step_id][data_type_id] = os.path.join(
# 				root_data_path, city, data_step_id, data_type_id
# 			)

# print(data_paths_dict)

# raw_trips_data_path = os.path.join(
#             self.raw_data_path,
#             "Dataset_" + self.city_name + ".csv"
#         )
#         self.trips_df = pd.read_csv(raw_trips_data_path)
#         return self.trips_df


# trips_df_norm_year_month.to_csv(
#                 os.path.join(
#                     self.norm_data_path,
#                     "_".join([str(year), str(month)]) + ".csv"
#                 )
#             )
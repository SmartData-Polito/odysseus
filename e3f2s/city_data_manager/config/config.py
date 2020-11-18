import os

root_data_path = os.path.join(
	os.path.dirname(os.path.dirname(__file__)),
	"data"
)

cities = [
	"Torino",
	"Louisville",
	"Minneapolis",
	"Milano",
	"New_York_City",
	"Berlin",
	"Vancouver",
	"Amsterdam",
	"Madrid",
	"Roma",
	"Austin",
	"Norfolk",
	"Kansas City",
	"Chicago",
	"Calgary"
]

data_steps_ids = [
	"raw",
	"norm",
	"od_trips"
]

data_type_ids = [
	"points",
	"trips",
	"weather",
	"geo"
]

data_paths_dict = {}
for city in cities:
	data_paths_dict[city] = {}
	for data_step_id in data_steps_ids:
		data_paths_dict[city][data_step_id] = {}
		for data_type_id in data_type_ids:
			data_paths_dict[city][data_step_id][data_type_id] = os.path.join(
				root_data_path, city, data_step_id, data_type_id
			)


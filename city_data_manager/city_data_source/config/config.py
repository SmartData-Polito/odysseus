import os

root_data_path = os.path.join(
	os.path.dirname(os.path.dirname(__file__)),
	"data"
)

data_steps_ids = [
	"raw",
	"norm",
]

data_type_ids = [
	"trips",
	"weather",
	"geo"
]

data_paths_dict = {}
for data_step_id in data_steps_ids:
	data_paths_dict[data_step_id] = {}
	for data_type_id in data_type_ids:
		data_paths_dict[data_step_id][data_type_id] = os.path.join(
			root_data_path, data_step_id, data_type_id
		)

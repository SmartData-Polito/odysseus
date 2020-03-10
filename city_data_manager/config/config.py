import os

root_data_path = os.path.join(
	os.path.dirname(os.path.dirname(__file__)), "data"
)

data_paths_dict = {
	"Minneapolis": os.path.join(root_data_path, "Minneapolis"),
}

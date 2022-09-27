from odysseus.city_data_manager.od_data_source.od_to_trips import *


week_config = generate_week_config(
    week_slots_type="weekday_weekend",
    day_slots_type="hours",
)
print(week_config)

# grid_matrix = get_city_grid_as_matrix(
#     (0, 0, 1500, 1500),
#     500,
#     "dummy_crs"
# )
# print(grid_matrix)
#
# zone_ids = np.ravel(grid_matrix.values)
#
# hourly_od_count_dict = generate_hourly_od_count_dict(week_config, zone_ids, "uniform", count=3)
#
# od_matrices = generate_od_from_week_config(
#     city_name="my_city_3X3",
#     week_config=week_config,
#     zone_ids=zone_ids,
#     od_type="count",
#     hourly_od_count_dict=hourly_od_count_dict
# )
#
# generate_trips_from_od(
#     "my_city_3X3",
#     week_config,
#     od_matrices,
#     grid_matrix,
#     zone_ids,
#     datetime.datetime(2023, 1, 1, 0, 0, 1),
#     datetime.datetime(2023, 1, 8, 0, 0, 1),
#     datetime.datetime(2023, 1, 8, 0, 0, 1),
#     datetime.datetime(2023, 1, 15, 0, 0, 1),
# )

from odysseus.city_data_manager.od_data_source.od_reader import *

read_od_matrices("my_city_3X3_1", "my_data_source")

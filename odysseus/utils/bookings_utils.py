import datetime

from odysseus.utils.geospatial_utils import get_od_distance
from odysseus.utils.time_utils import get_daytype_from_week_config


def create_booking_request_dict(
		week_config, timeout, current_datetime, origin_id, destination_id, distance_matrix,
		avg_speed_kmh_mean, max_duration, fixed_driving_distance,
		orography_factor=1.4
):

	booking_request_dict = dict()

	booking_request_dict["ia_timeout"] = timeout
	booking_request_dict["start_time"] = current_datetime
	booking_request_dict["date"] = current_datetime.date()
	current_hour = current_datetime.hour
	current_weekday = current_datetime.weekday()
	current_daytype = get_daytype_from_week_config(week_config, current_weekday)
	booking_request_dict["hour"] = current_hour
	booking_request_dict["weekday"] = current_weekday
	booking_request_dict["daytype"] = current_daytype

	booking_request_dict["origin_id"] = int(origin_id)
	booking_request_dict["destination_id"] = int(destination_id)

	if fixed_driving_distance:
		booking_request_dict["driving_distance"] = fixed_driving_distance
		booking_request_dict["euclidean_distance"] = fixed_driving_distance / orography_factor
	else:
		booking_request_dict = get_distances_from_distmatrix(
			booking_request_dict, distance_matrix,
			booking_request_dict["origin_id"],
			booking_request_dict["destination_id"],
			orography_factor
		)

	booking_request_dict["duration"] = booking_request_dict["driving_distance"] / (
			avg_speed_kmh_mean / 3.6
	)
	if booking_request_dict["duration"] > max_duration:
		booking_request_dict["duration"] = max_duration

	booking_request_dict["end_time"] = current_datetime + datetime.timedelta(
		seconds=booking_request_dict["duration"]
	)

	return booking_request_dict


def update_req_time_info(booking_request_dict):
	booking_request_dict["date"] = booking_request_dict["start_time"].date()
	booking_request_dict["hour"] = booking_request_dict["start_time"].hour
	booking_request_dict["weekday"] = booking_request_dict["start_time"].weekday()
	if booking_request_dict["weekday"] in [5, 6]:
		booking_request_dict["daytype"] = "weekend"
	else:
		booking_request_dict["daytype"] = "weekday"
	return booking_request_dict


def get_distances_from_distmatrix(
		booking_or_request_dict, distance_matrix, origin_id, destination_id, orography_factor,
):
	booking_or_request_dict["euclidean_distance"] = distance_matrix.loc[origin_id, destination_id]
	if origin_id == destination_id:
		booking_or_request_dict["euclidean_distance"] = 500
		# raise NotImplementedError("Round trips not implemented!")
	booking_or_request_dict["driving_distance"] = booking_or_request_dict["euclidean_distance"] * orography_factor
	return booking_or_request_dict


def get_walking_distances(booking_dict, grid_centroids, grid_crs):
	booking_dict["origin_walking_distance"] = get_od_distance(
		grid_centroids,
		booking_dict["req_origin_id"],
		booking_dict["origin_id"],
		grid_crs
	)
	booking_dict["destination_walking_distance"] = get_od_distance(
		grid_centroids,
		booking_dict["req_destination_id"],
		booking_dict["destination_id"],
		grid_crs
	)
	return booking_dict


def add_consumption_emission_info(booking_or_request_dict, vehicle):
	booking_or_request_dict["soc_delta"] = vehicle.consumption_to_percentage(
		vehicle.distance_to_consumption(
			booking_or_request_dict["driving_distance"] / 1000
		)
	)
	booking_or_request_dict["welltotank_kwh"] = vehicle.welltotank_energy_from_perc(
		booking_or_request_dict["soc_delta"]
	)
	booking_or_request_dict["tanktowheel_kwh"] = vehicle.tanktowheel_energy_from_perc(
		booking_or_request_dict["soc_delta"]
	)
	booking_or_request_dict["soc_delta_kwh"] = \
		booking_or_request_dict["welltotank_kwh"] + booking_or_request_dict["tanktowheel_kwh"]
	booking_or_request_dict["welltotank_emissions"] = vehicle.distance_to_welltotank_emission(
		booking_or_request_dict["driving_distance"] / 1000
	)
	booking_or_request_dict["tanktowheel_emissions"] = vehicle.distance_to_tanktowheel_emission(
		booking_or_request_dict["driving_distance"] / 1000
	)
	booking_or_request_dict["co2_emissions"] = \
		booking_or_request_dict["welltotank_emissions"] + booking_or_request_dict["tanktowheel_emissions"]

	return booking_or_request_dict


def get_grid_indexes(grid_matrix, bookings, zone_ids):
	zone_coords_dict = {}
	for j in grid_matrix.columns:
		for i in grid_matrix.index:
			zone_coords_dict[grid_matrix.iloc[i, j]] = (i, j)

	for zone in zone_ids:
		bookings.loc[bookings.origin_id == zone, "origin_i"] = zone_coords_dict[zone][0]
		bookings.loc[bookings.origin_id == zone, "origin_j"] = zone_coords_dict[zone][1]
		bookings.loc[bookings.destination_id == zone, "destination_i"] = zone_coords_dict[zone][0]
		bookings.loc[bookings.destination_id == zone, "destination_j"] = zone_coords_dict[zone][1]
	return bookings


def base_round(x, base):
	if x < 0:
		return 0
	elif x > base:
		return base
	else:
		return round(x)


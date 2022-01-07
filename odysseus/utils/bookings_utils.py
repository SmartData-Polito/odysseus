import pandas as pd

from odysseus.utils.geospatial_utils import get_od_distance


def create_booking_request_dict(
        timeout, current_datetime, origin_id, destination_id
):

    booking_request_dict = dict()

    booking_request_dict["ia_timeout"] = timeout
    booking_request_dict["start_time"] = current_datetime
    booking_request_dict["date"] = current_datetime.date()
    current_hour = current_datetime.hour
    current_weekday = current_datetime.weekday()
    if current_weekday in [5, 6]:
        current_daytype = "weekend"
    else:
        current_daytype = "weekday"
    booking_request_dict["hour"] = current_hour
    booking_request_dict["weekday"] = current_weekday
    booking_request_dict["daytype"] = current_daytype

    booking_request_dict["origin_id"] = origin_id
    booking_request_dict["destination_id"] = destination_id

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


def get_distances(booking_or_request_dict, grid, min_distance=500, orography_factor=1.4):
	booking_or_request_dict["euclidean_distance"] = get_od_distance(
		grid,
		booking_or_request_dict["origin_id"],
		booking_or_request_dict["destination_id"]
	)

	if booking_or_request_dict["euclidean_distance"] == 0:
		booking_or_request_dict["euclidean_distance"] = min_distance

	booking_or_request_dict["driving_distance"] = booking_or_request_dict["euclidean_distance"] * orography_factor
	return booking_or_request_dict


def get_walking_distances(booking_dict, grid):
	booking_dict["origin_walking_distance"] = get_od_distance(
		grid,
		booking_dict["req_origin_id"],
		booking_dict["origin_id"]
	)
	booking_dict["destination_walking_distance"] = get_od_distance(
		grid,
		booking_dict["req_destination_id"],
		booking_dict["destination_id"]
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

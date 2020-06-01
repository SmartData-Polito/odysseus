import pandas as pd


def update_req_time_info(booking_request):
	booking_request["date"] = booking_request["start_time"].date()
	booking_request["hour"] = booking_request["start_time"].hour
	booking_request["weekday"] = booking_request["start_time"].weekday()
	if booking_request["weekday"] in [5, 6]:
		booking_request["daytype"] = "weekend"
	else:
		booking_request["daytype"] = "weekday"
	return booking_request


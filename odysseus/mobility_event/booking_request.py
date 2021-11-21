import pandas as pd


class BookingRequest:

    def __init__(self, origin_id, destination_id, start_time, end_time):
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.start_time = start_time
        self.end_time = end_time

    def to_pd_record(self):
        return pd.DataFrame(
            [{
                "origin_id": self.origin_id,
                "destination_id": self.destination_id,
                "start_time": self.start_time,
                "end_time": self.end_time,
            }]
        )

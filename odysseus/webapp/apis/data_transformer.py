import numpy
import datetime
import pandas as pd
import pickle

class DataTransformer:
    def __init__(self,DEBUG=True):
        self.DEBUG=DEBUG
        
    # Bookings
    def bookings_request(self,obj):
        obj['starting_date'] = obj['start_time'].apply(lambda x:  datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S%z'))
        self.sim_booking_requests = obj.fillna(0).set_index("starting_date").iloc[:, 0].resample("60Min").count()
        if self.DEBUG:
            print(self.sim_booking_requests.to_json())
        return self.sim_booking_requests.to_json()
        
    def location_origin_bookings(self,obj):
        self.sim_booking_origin_hourly_count = obj.fillna(0).set_index("start_time").iloc[:, [0,5]].groupby([pd.Grouper(freq='60Min'),'origin_id']).count()
        if self.DEBUG:
            print(self.sim_booking_origin_hourly_count)
        return self.sim_booking_origin_hourly_count
        
    def location_destination_bookings(self,obj):
        self.sim_booking_destination_hourly_count = obj.fillna(0).set_index("start_time").iloc[:, [0,6]].groupby([pd.Grouper(freq='60Min'),'destination_id']).count()
        print(self.sim_booking_destination_hourly_count)
        return self.sim_booking_destination_hourly_count
        
        
    #Charges
    def count_charges(self,obj):
        self.sim_charges_hourly_count = obj.set_index("start_time").iloc[:, 0].resample("60Min").count()
        if self.DEBUG:
            print(self.sim_charges_hourly_count.to_json())
        return self.sim_charges_hourly_count.to_json()
        
    def location_charges(self,obj):
        self.sim_charges_hourly_location_count = obj.fillna(0).set_index("start_time").iloc[:, [0,10]].groupby([pd.Grouper(freq='60Min'),'zone_id']).count()
        print(self.sim_charges_hourly_location_count)
    
    # users-charges-bookings
    def system_charges_bookings_duration(self,obj):
        self.system_charges_bookings_duration = obj.fillna(0).set_index("start_time",drop=True).iloc[:, [9]].groupby([pd.Grouper(freq='60Min')]).mean().fillna(0)
        print(self.system_charges_bookings_duration)
    def system_charges_bookings_origin(self,obj):
        self.system_charges_bookings_origin = obj.fillna(0).set_index("start_time",drop=True).iloc[:, [5,9]].groupby([pd.Grouper(freq='60Min'),'origin_id']).mean().fillna(0)
        print(self.system_charges_bookings_origin)
    
import numpy
import pandas as pd
import pickle

class DataTransformer:
    def __init__(self,DEBUG=True):
        self.DEBUG=DEBUG
        
    # Bookings
    def bookings_request(self,obj):
        self.sim_booking_requests = obj.fillna(0).set_index("start_time").iloc[:, 0].resample("60Min").count()
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
    
if __name__ == '__main__':
    with open("../../simulator/results/Torino/single_run/inter_bre_save_true/sim_bookings.pickle","rb") as f:
        testBookings = pickle.load(f)
        print("sim_bookings")
        print(testBookings.head())
        print(testBookings.keys())
    with open("../../simulator/results/Torino/single_run/inter_bre_save_true/sim_charges.pickle","rb") as f:
        testCharges = pickle.load(f)
        print("testCharges")
        print(testCharges.head())
        print(testCharges.keys())
    with open("../../simulator/results/Torino/single_run/inter_bre_save_true/grid.pickle","rb") as f:
        testGrid = pickle.load(f)
        print("testGrid")
        print(testGrid.head())
        print(testGrid.keys())
        '''
    with open("../../simulator/results/Torino/single_run/inter_bre_save_true/sim_output.pickle","rb") as f:
        testOutput = pickle.load(f)
        print("testOutput")
        print(testOutput.head())'''
    with open("../../simulator/results/Torino/single_run/inter_bre_save_true/sim_system_charges_bookings.pickle","rb") as f:
        test_sim_system_charges_bookings = pickle.load(f)
        print("test_sim_system_charges_bookings")
        print(test_sim_system_charges_bookings.head())
        print(test_sim_system_charges_bookings.keys())
    with open("../../simulator/results/Torino/single_run/inter_bre_save_true/sim_users_charges_bookings.pickle","rb") as f:
        test_sim_users_charges_bookings = pickle.load(f)
        print("sim_users_charges_bookings")
        print(test_sim_users_charges_bookings.head())
        print(test_sim_users_charges_bookings.keys())
    dt = DataTransformer()
    #dt.location_destination_bookings(test)
    dt.system_charges_bookings_origin(test_sim_system_charges_bookings)

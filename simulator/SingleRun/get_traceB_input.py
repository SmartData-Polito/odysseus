import datetime

from SimulationInput.EFFCS_SimInput import EFFCS_SimInput

def get_traceB_input (conf_tuple):

    # print ("Creating traceB simulation input ..")
    # t0 = datetime.datetime.now()

    simInput = EFFCS_SimInput\
         (conf_tuple)

    simInput.get_booking_requests_list()
    simInput.init_cars()
    simInput.init_cars_dicts()
    simInput.init_hub()
    simInput.init_charging_poles()

    # t1 = datetime.datetime.now()
    # print (t1 - t0)

    return simInput

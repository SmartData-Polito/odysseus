import datetime

from simulator.simulation_input.sim_input import SimInput


def get_eventG_input (conf_tuple):

    # print ("Creating eventG simulation input ..")
    # t0 = datetime.datetime.now()

    simInput = SimInput(conf_tuple)

    simInput.init_vehicles()
    simInput.init_hub()
    simInput.init_charging_poles()

    # t1 = datetime.datetime.now()
    # print (t1 - t0)

    return simInput

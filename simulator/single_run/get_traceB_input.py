from simulator.simulation_input.sim_input import SimInput


def get_traceB_input (conf_tuple):

    simInput = SimInput(conf_tuple)
    simInput.get_booking_requests_list()
    simInput.init_vehicles()
    simInput.init_hub()
    simInput.init_charging_poles()
    print("A simulation input was created!")
    return simInput

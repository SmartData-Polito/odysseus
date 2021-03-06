import datetime
from odysseus.simulator.simulation_input.sim_input import SimInput


def get_eventG_input (conf_dict):

    simInput = SimInput(conf_dict)
    simInput.init_vehicles()
    simInput.init_charging_poles()
    simInput.init_relocation()

    print(datetime.datetime.now(), "Simulation input initialised!")
    return simInput

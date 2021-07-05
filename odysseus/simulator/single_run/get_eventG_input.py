import datetime
from odysseus.simulator.simulation_input.sim_input import SimInput


def get_eventG_input (conf_dict):

    sim_input = SimInput(conf_dict)
    sim_input.init_vehicles()
    sim_input.init_charging_poles()
    sim_input.init_relocation()

    print(datetime.datetime.now(), "Simulation input initialised!")
    return sim_input

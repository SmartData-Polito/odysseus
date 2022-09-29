from odysseus.simulator.simulation.model_driven_simulator import ModelDrivenSim
from odysseus.simulator.simulation_output.sim_output import SimOutput
from odysseus.simulator.simulation_input.sim_input import SimInput
from odysseus.utils.path_utils import get_output_path


def run_eventG_sim (sim_input):
    sim_eventG = ModelDrivenSim(sim_input=sim_input)
    sim_eventG.init_demand_data_structures()
    sim_eventG.run()
    return sim_eventG


def get_eventG_sim_output (sim_input):
    sim_eventG = run_eventG_sim(sim_input)
    return SimOutput(sim_eventG)


def get_eventG_sim_stats (conf_tuple):
    sim_general_conf = conf_tuple[0]
    sim_scenario_conf = conf_tuple[1]
    demand_model_folder = conf_tuple[2]
    supply_model_object = conf_tuple[3]

    parameters_input = {
        "sim_general_conf": sim_general_conf,
        "sim_scenario_conf": sim_scenario_conf,
        "supply_model_object": supply_model_object,
        "demand_model_folder": demand_model_folder
    }

    sim_input = SimInput(parameters_input)
    sim_input.init_vehicles()
    sim_input.init_charging_poles()
    sim_input.init_relocation()
    sim_eventG = run_eventG_sim(sim_input)
    simOutput_eventG = SimOutput(sim_eventG)
    return simOutput_eventG.sim_stats

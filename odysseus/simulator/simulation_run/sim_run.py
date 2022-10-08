from odysseus.simulator.simulation.model_driven_simulator import ModelDrivenSim
from odysseus.simulator.simulation_output.sim_output import SimOutput
from odysseus.simulator.simulation_input.sim_input import SimInput
from odysseus.utils.path_utils import get_output_path
from odysseus.simulator.simulation.trace_driven_simulator import TraceDrivenSim
from odysseus.simulator.simulation_output.sim_output import SimOutput
from odysseus.simulator.simulation_input.sim_input import SimInput
from odysseus.utils.path_utils import get_output_path


def run_sim(sim_input, sim_technique):

    if sim_technique == "traceB":
        sim = TraceDrivenSim(sim_input=sim_input)
    elif sim_technique == "eventG":
        sim = ModelDrivenSim(sim_input=sim_input)
        sim.init_demand_data_structures()
    else:
        sim = None

    if sim is not None:
        sim.run()
    else:
        print("Simulator is not correctly configured!")
        exit(-1)

    return sim


def run_sim_only_stats(parameters_input):

    sim_input = SimInput(parameters_input)
    if parameters_input["sim_general_conf"]["sim_technique"] == "traceB":
        sim_input.get_booking_requests_list()
    sim_input.init_vehicles()
    sim_input.init_charging_poles()
    sim_input.init_relocation()
    sim = run_sim(sim_input, parameters_input["sim_general_conf"]["sim_technique"])
    sim_output = SimOutput(sim)
    return sim_output.sim_stats.to_dict()

from odysseus.simulator.simulation.trace_driven_simulator import TraceDrivenSim
from odysseus.simulator.simulation_output.sim_output import SimOutput
from odysseus.simulator.simulation_input.sim_input import SimInput


def run_traceB_sim (simInput):
    sim_traceB = TraceDrivenSim(simInput=simInput)
    sim_traceB.run()
    return sim_traceB


def get_traceB_sim_output(simInput):
    sim_traceB = run_traceB_sim(simInput)
    return SimOutput(sim_traceB)


def get_traceB_sim_stats(conf_tuple):

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

    simInput = SimInput(parameters_input)
    simInput.get_booking_requests_list()
    simInput.init_vehicles()
    simInput.init_charging_poles()
    simInput.init_relocation()
    sim_traceB = run_traceB_sim(simInput)
    simOutput_traceB = SimOutput(sim_traceB)
    return simOutput_traceB.sim_stats

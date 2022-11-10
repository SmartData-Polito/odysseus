from odysseus.simulator.simulation_input.sim_input import SimInput
from odysseus.simulator.simulation.simulator import SharedMobilitySim
from odysseus.simulator.simulation_output.sim_output import SimOutput


def run_sim_v2(sim_input):

    sim = SharedMobilitySim(sim_input=sim_input)

    if sim is not None:
        sim.run()
    else:
        print("Simulator is not correctly configured!")
        exit(-1)

    return sim


def run_sim_only_stats(parameters_input):

    sim_input = SimInput(parameters_input)
    sim_input.init_vehicles()
    sim_input.init_charging_poles()
    sim_input.init_relocation()
    sim = run_sim_v2(sim_input)
    sim_output = SimOutput(sim)
    return sim_output.sim_stats.to_dict()

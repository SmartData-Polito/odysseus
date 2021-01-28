from e3f2s.simulator.simulation.model_driven_simulator import ModelDrivenSim
from e3f2s.simulator.simulation_output.sim_output import SimOutput
from e3f2s.simulator.simulation_input.sim_input import SimInput


def run_eventG_sim (simInput):

    sim_eventG = ModelDrivenSim(
    
                simInput=simInput
    
            )
    sim_eventG.init_data_structures()    
    sim_eventG.run()
    return sim_eventG


def get_eventG_sim_output (simInput):
    
    sim_eventG = run_eventG_sim(simInput)
    return SimOutput(sim_eventG)


def get_eventG_sim_stats (conf_tuple):

    simInput = SimInput(conf_tuple)
    simInput.init_vehicles()
    simInput.init_charging_poles()
    sim_eventG = run_eventG_sim(simInput)
    simOutput_eventG = SimOutput(sim_eventG)
    return simOutput_eventG.sim_stats

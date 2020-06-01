from e3f2s.simulator.simulation.model_driven_simulator import ModelDrivenSim
from e3f2s.simulator.simulation_output.sim_output import EFFCS_SimOutput


def run_eventG_sim (simInput):

    # print ("Running event generation based simulation ..")
        
    sim_eventG = ModelDrivenSim(
    
                simInput=simInput
    
            )

    sim_eventG.init_data_structures()    
    # t0 = datetime.datetime.now()
    sim_eventG.run()
    # t1 = datetime.datetime.now()
    # print (t1 - t0)

    return sim_eventG

def get_eventG_sim_output (simInput):
    
    sim_eventG = run_eventG_sim(simInput)
    return EFFCS_SimOutput(sim_eventG)

def get_eventG_sim_stats (simInput):
    
    sim_eventG = run_eventG_sim(simInput)
    simOutput_eventG = EFFCS_SimOutput(sim_eventG)
    return simOutput_eventG.sim_stats

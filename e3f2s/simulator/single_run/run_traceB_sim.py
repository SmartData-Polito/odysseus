from e3f2s.simulator.simulation.trace_driven_simulator import TraceDrivenSim
from e3f2s.simulator.simulation_output.sim_output import EFFCS_SimOutput
from e3f2s.simulator.simulation_input.sim_input import SimInput


def run_traceB_sim (simInput):

    # print ("Running trace based simulation ..")
        
    sim_traceB = TraceDrivenSim(
    
                simInput=simInput,
    
            )

    sim_traceB.init_data_structures()
    # t0 = datetime.datetime.now()
    sim_traceB.run()
    # t1 = datetime.datetime.now()
    # print (t1 - t0)
    
    return sim_traceB


def get_traceB_sim_output(simInput):
    sim_traceB = run_traceB_sim(simInput)
    return EFFCS_SimOutput(sim_traceB)


def get_traceB_sim_stats(conf_tuple):

    simInput = SimInput(conf_tuple)
    simInput.get_booking_requests_list()
    simInput.init_vehicles()
    simInput.init_hub()
    simInput.init_charging_poles()
    sim_traceB = run_traceB_sim(simInput)
    simOutput_traceB = EFFCS_SimOutput(sim_traceB)
    print("A simulation finished!")
    return simOutput_traceB.sim_stats

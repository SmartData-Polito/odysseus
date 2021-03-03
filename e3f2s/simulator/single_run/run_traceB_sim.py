from e3f2s.simulator.simulation.trace_driven_simulator import TraceDrivenSim
from e3f2s.simulator.simulation_output.sim_output import SimOutput
from e3f2s.simulator.simulation_input.sim_input import SimInput


def run_traceB_sim (simInput):

    sim_traceB = TraceDrivenSim(
    
                simInput=simInput,
    
            )

    sim_traceB.init_data_structures()
    sim_traceB.run()
    return sim_traceB


def get_traceB_sim_output(simInput):
    sim_traceB = run_traceB_sim(simInput)
    return SimOutput(sim_traceB)


def get_traceB_sim_stats(conf_tuple):

    simInput = SimInput(conf_tuple)
    simInput.get_booking_requests_list()
    simInput.init_vehicles()
    simInput.init_charging_poles()
    simInput.init_relocation()
    sim_traceB = run_traceB_sim(simInput)
    simOutput_traceB = SimOutput(sim_traceB)
    return simOutput_traceB.sim_stats

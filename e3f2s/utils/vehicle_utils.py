from e3f2s.simulator.simulation_input.sim_current_config.vehicle_config import vehicle_conf


def soc_to_kwh(soc, a=0., b=vehicle_conf["battery_capacity"]):
    return (b - a) / 100 * (soc - 100) + b


def get_soc_delta (
        distance,
        battery_capacity=vehicle_conf["battery_capacity"],
        vehicle_energy_efficiency=vehicle_conf["energy_efficiency"]
):
    return (vehicle_energy_efficiency * distance * 100) / battery_capacity

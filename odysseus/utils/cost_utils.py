def get_fuelcost_from_energy(fuel_type,fuel_costs, energy_mj):
	if fuel_type == "electric":
		energy_kwh = energy_mj / 3.6
		return (fuel_costs[fuel_type]["fuel_cost"] * energy_kwh) / (fuel_costs[fuel_type]["charging_efficiency"] / 100)
	elif fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
		liters = energy_mj / (
				fuel_costs[fuel_type]["lower_heating_value"] / (1 / (fuel_costs[fuel_type]["density"] / 1000))
			# converted lhv from MJ/kg to MJ/L
		)
		return fuel_costs[fuel_type]["fuel_cost"] * liters

def charging_station_lord_cost(costs):
	cost = 0
	for (index, numb) in costs.items():
		cost += numb
	return cost

def insert_scenario_costs(df, sim_scenario_conf, vehicles_cost_conf, poles_cost_conf):
	df['cars_cost'] = df.n_vehicles_sim * vehicles_cost_conf[sim_scenario_conf["engine_type"]][
		sim_scenario_conf["vehicle_model_name"]
	]['leasing_cost'] #/ 12
	if sim_scenario_conf["engine_type"] == "electric":
		df['charging_infrastructure_cost'] = df.tot_n_charging_poles * charging_station_lord_cost(
			poles_cost_conf[sim_scenario_conf["profile_type"]]
		)/ poles_cost_conf["pole_useful_life"]
	else:
		df['charging_infrastructure_cost'] = 0
	df['scenario_cost'] = df.cars_cost + df.charging_infrastructure_cost


def insert_sim_costs(df, sim_scenario_conf, fuel_costs, administrative_cost_conf, vehicles_cost_conf):
	print(df.n_bookings)
	df['relocation_cost'] = df.cum_relo_ret_t * administrative_cost_conf['relocation_workers_hourly_cost']
	if "tot_tanktowheel_energy" in df.index:
		df['energy_cost'] = get_fuelcost_from_energy(sim_scenario_conf["engine_type"], fuel_costs, df.tot_tanktowheel_energy)
	else:
		df['energy_cost'] = 0
	df['revenues'] = (df.tot_mobility_duration / 60) * vehicles_cost_conf[sim_scenario_conf["engine_type"]][
		sim_scenario_conf["vehicle_model_name"]
	]["cost_permin"]
	df['washing'] = vehicles_cost_conf[sim_scenario_conf["engine_type"]][
		sim_scenario_conf["vehicle_model_name"]
	]['disinfection_cost'] * df.n_charges + vehicles_cost_conf[
		sim_scenario_conf["engine_type"]
	][sim_scenario_conf["vehicle_model_name"]]['washing_cost'] * df.n_bookings / 100
	df['sim_cost'] = df.relocation_cost + df.energy_cost + df.washing


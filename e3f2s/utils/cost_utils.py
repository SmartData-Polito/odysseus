vehicle_cost = {
	"gasoline": {
		"VW Golf 7 1.0 TSI 2018": {
			"retail_price": 16612.06,
			"IVA": 22,
			"put_into_circulation": 833.28,
			"government_subsidies": 0
		}
	},
	"diesel": {
		"VW Golf 7 2.0 TDI 2018": {
			"retail_price": 23907,
			"IVA": 22,
			"put_into_circulation": 833.28,
			"government_subsidies": 0
		}
	},
	"lpg": {
		"Opel Corsa 1.4 EcoTech": {
			"retail_price": 12598,
			"IVA": 22,
			"put_into_circulation": 833.28,
			"government_subsidies": 0
		}
	},
	"cng": {
		"VW Golf 7 1.4 TGI 2018": {
			"retail_price": 18374,
			"IVA": 22,
			"put_into_circulation": 833.28,
			"government_subsidies": 0
		}
	},
	"electric": {
		"VW e-Golf 2018": {
			"retail_price": 24867.28,
			"IVA": 22,
			"put_into_circulation": 833.28,
			"government_subsidies": 6000

		},
		"Smart fortwo Electric Drive 2018": {
			"retail_price": 16279.92,
			"IVA": 22,
			"put_into_circulation": 833.28,
			"government_subsidies": 6000
		}
	}
}

charging_station_costs = {
	"wall_plug": {
		"hardware": 813,
		"labor": 600,
		"materials": 0,
		"permits": 0,
		"taxes": (22 / 100) * 813,
		"government_subsidy": -795.93

	},
	"single_phase_1": {
		"hardware": 3127,
		"labor": 1544,
		"materials": 1112,
		"permit": 82,
		"taxes": (22 / 100) * 3127,
		"government_subsidy": -1500
	},
	"single_phase_2": {
		"hardware": 3127,
		"labor": 1544,
		"materials": 1112,
		"permit": 82,
		"taxes": (22 / 100) * 3127,
		"government_subsidy": -1500
	},
	"three_phase_1": {
		"hardware": 3127,
		"labor": 1544,
		"materials": 1112,
		"permit": 82,
		"taxes": (22 / 100) * 3127,
		"government_subsidy": -1500
	},
	"three_phase_2": {
		"hardware": 4500,
		"labor": 1544,
		"materials": 1112,
		"permit": 82,
		"taxes": (22 / 100) * 4500,
		"government_subsidy": -1500
	},
	"three_phase_3": {
		"hardware": 4500,
		"labor": 1544,
		"materials": 1112,
		"permit": 82,
		"taxes": (22 / 100) * 4500,
		"government_subsidy": -1500
	},
	"dcfc_1": {
		"hardware": 31000,
		"labor": 19200,
		"materials": 26000,
		"permit": 200,
		"taxes": (22 / 100) * 31000,
		"government_subsidy": -1500
	},
	"dcfc_2": {
		"hardware": 75000,
		"labor": 20160,
		"materials": 27300,
		"permit": 210,
		"taxes": (22 / 100) * 75000,
		"government_subsidy": -1500
	},
}

insurance_fixed_costs = {
	"compulsory_traffic_insurance": 119.83,
	"basic_premium": 58.02,
	"commercial_3rd_party_insurance": 157.93,
}
parking_spot_fixed_costs = {
	"annual_rental_parking_space": 600,
	"parking_spot_per_vehicle": 1.5
}
charging_stations_param = {
	"residual_value_rate": 5,
	"depreciation_period_charging_station": 8
}

fuel_costs = {
	"gasoline": {
		"fuel_cost": 1.43407,
		"lower_heating_value": 42.3,  # MJ/kg
		"density": 745.8  # g/L
	},
	"diesel": {
		"fuel_cost": 1.31179,
		"lower_heating_value": 42.7,  # MJ/kg
		"density": 836.1  # g/L
	},
	"lpg": {
		"fuel_cost": 0.62153,
		"lower_heating_value": 46,  # MJ/kg
		"density": 550  # g/L
	},
	"cng": {
		"fuel_cost": 0.975,
		"lower_heating_value": 48,  # MJ/kg
		"density": 1000  # g/L
	},
	"electric": {
		"fuel_cost": 0.2634,
		"charging_efficiency": 80
	}
}

operational_fixed_costs = {
	"annual_worker_wage": 12613.85,
	"annual_marketing": 75683.1,
	"annual_digital_platform": 151366.19,
	"other_miscellaneous": 75683.1
}

bookings_revenues = {
	"gasoline": {
		"VW Golf 7 1.0 TSI 2018": {
			"cost_permin": 0.26
		}
	},
	"diesel": {
		"VW Golf 7 2.0 TDI 2018": {
			"cost_permin": 0.26
		}
	},
	"lpg": {
		"Opel Corsa 1.4 EcoTech": {
			"cost_permin": 0.26
		}
	},
	"cng": {
		"VW Golf 7 1.4 TGI 2018": {
			"cost_permin": 0.26
		}
	},
	"electric": {
		"VW e-Golf 2018": {
			"cost_permin": 0.26
		},
		"Smart fortwo Electric Drive 2018": {
			"cost_permin": 0.19
		}
	}
}

ev_residual_value_revenue = {
	"annual_depreciation_rate": 0.7,
	"battery_to_vehicle_cost_ratio": 0.4,
	"ICEV_depreciation_perkm": 0.025,
	"battery_depreciation_perkm": 0.016
}
service_lifespan_vehicle_years = 8.0
non_rental_revenue = {
	"advertising": 163.98
}
discount_rate = 0.1


def operational_costs(n_workers):
	return n_workers * operational_fixed_costs["annual_worker_wage"] + operational_fixed_costs["annual_marketing"] + \
	       operational_fixed_costs["other_miscellaneous"]


def maintenance_costs(fuel_type, distance):
	if fuel_type == "electric":
		lca_maintenance_costpkm = 3826.93 / 250000  # €/km
		costs = lca_maintenance_costpkm * distance
	elif fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
		lca_maintenance_costpkm = 6649.66 / 250000  # €/km
		costs = lca_maintenance_costpkm * distance
	return costs


def get_fuelcost_from_energy(fuel_type, energy_mj):
	if fuel_type == "electric":
		energy_kwh = energy_mj / 3.6
		return (fuel_costs[fuel_type]["fuel_cost"] * energy_kwh) / (fuel_costs[fuel_type]["charging_efficiency"] / 100)
	elif fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
		liters = energy_mj / (
				fuel_costs[fuel_type]["lower_heating_value"] / (1 / (fuel_costs[fuel_type]["density"] / 1000))
			# converted lhv from MJ/kg to MJ/L
		)
		return fuel_costs[fuel_type]["fuel_cost"] * liters


def num_charging_stations(poles):
	if poles % 4 == 0:
		return poles / 4
	else:
		return (poles // 4) + 1


def charging_station_total_costs(fuel_type, charging_stations):
	if fuel_type == "electric":
		costs = 0
		for zone in charging_stations.keys():
			# for station in charging_stations[zone]:
			costs += num_charging_stations(charging_stations[zone].num_poles) * charging_station_lord_cost(
				charging_stations[zone].cost) * \
			         (1 - (charging_stations_param["residual_value_rate"] / 100)) / \
			         charging_stations_param["depreciation_period_charging_station"]
		return costs
	else:
		return 0


def charging_station_lord_cost(costs):
	cost = 0
	for (index, numb) in costs.items():
		cost += numb
	return cost


def parking_spot_costs(vehicles):
	costs = 0
	for vehicle in vehicles:
		costs += parking_spot_fixed_costs["parking_spot_per_vehicle"] * parking_spot_fixed_costs[
			"annual_rental_parking_space"]
	return costs


def purchase_cost_vehicle(engine_type, model):
	return (vehicle_cost[engine_type][model]["retail_price"] + (
			(vehicle_cost[engine_type][model]["IVA"] / 100) *
			vehicle_cost[engine_type][model]["retail_price"]
	) + vehicle_cost[engine_type][model]["put_into_circulation"])


def total_purchase_cost(vehicles):
	costs = 0
	for vehicle in vehicles:
		costs += (vehicle.costs["retail_price"] + (
				(vehicle.costs["IVA"] / 100) * vehicle.costs["retail_price"])
		          + vehicle.costs["put_into_circulation"]) - \
		         vehicle.costs["government_subsidies"]
	return costs


def insurance_costs(vehicles):
	costs = 0
	for vehicle in vehicles:
		I_ci = insurance_fixed_costs["compulsory_traffic_insurance"]
		I_li = insurance_fixed_costs["basic_premium"] + \
		       (vehicle.costs["retail_price"] + ((vehicle.costs["IVA"] / 100) * vehicle.costs["retail_price"])
		        + vehicle.costs["put_into_circulation"]) * 1.0880 / 100
		I_ti = insurance_fixed_costs["commercial_3rd_party_insurance"]
		I_di = (I_li + I_ti) * (20 / 100)
		I_pi = 6.31 * vehicle.n_seats
		costs += (I_ci + I_li + I_ti + I_di + I_pi)
	return costs

# def insert_administrative_costs(df,administrative_cost_conf):
#     df['it_salary'] = administrative_cost_conf['n_it_specialists'] * administrative_cost_conf['it_specialist_ral']
#     df['manager_salary'] = administrative_cost_conf['n_manager'] * administrative_cost_conf['manager_ral']
#     df['marketing_cost'] = administrative_cost_conf['marketing_costs']
#     df['office_cost'] = administrative_cost_conf['office_costs']
#     df['customer_service_cost'] = (
#             administrative_cost_conf['n_customer_service_specialists'] *
#             administrative_cost_conf['customer_service_specialist_ral'])
#     df['administrative_costs'] = (df.office_cost + df.manager_salary + df.it_salary
#                                   + df.customer_service_cost + df.marketing_cost)
#
#
# def insert_scenario_costs(df, vehicles_cost_conf, poles_cost_conf):
#     df['cars_cost'] = (df.n_cars) * (
#                 vehicles_cost_conf['car_annual_cost'] + vehicles_cost_conf['car_annual_insurance_cost'] +
#                 vehicles_cost_conf['car_annual_mantenaince_cost'])
#     df['poles_cost'] = df.n_charging_poles * (
#                 poles_cost_conf['pole_installation_cost'] + poles_cost_conf['pole_annual_mantenaince_cost'] +
#                 poles_cost_conf['cosap_annual_tax'])
#
#
# def insert_sim_costs(df, scenario_costs_conf, administrative_cost_conf, vehicles_cost_conf):
#     df['relocation_cost'] = round((scenario_costs_conf['utilization_relocation_workers']*2*df.cum_relo_t/ \
#                                    ((sim_end - sim_start).total_seconds()/ 3600 / 8)))* \
#                             administrative_cost_conf['relocation_workers_hourly_cost']* \
#                             ((sim_end - sim_start).total_seconds() / 3600 / 8)
#     df['energy_cost'] = df.tot_charging_energy*scenario_costs_conf['kwh_cost']
#     df['revenues'] = (df.total_trips_duration*scenario_costs_conf['real_bookings_percentage']/100)*scenario_costs_conf['price_per_minute']
#     df['charge_deaths_cost'] = df.n_charge_deaths*scenario_costs_conf['tow_truck_cost_per_call']
#     df['deaths_cost'] = df.n_deaths*scenario_costs_conf['tow_truck_cost_per_call']
#     df['washing'] = vehicles_cost_conf['disinfection_cost']*df.n_charges + vehicles_cost_conf['washing_cost']*df.n_bookings/100

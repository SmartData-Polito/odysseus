vehicle_cost = {
	"gasoline": {
		"VW Golf 7 1.0 TSI 2018": {
			# "retail_price": 16612.06,
			"leasing_cost": 2614.32,
			"washing_cost": 8,
			"disinfection_cost": 15,
			"cost_permin": 0.26
		}
	},
	"diesel": {
		"VW Golf 7 2.0 TDI 2018": {
			# "retail_price": 23907,
			"leasing_cost": 4970.64,
			"washing_cost": 8,
			"disinfection_cost": 15,
			"cost_permin": 0.26
		}
	},
	"lpg": {
		"Opel Corsa 1.4 EcoTech": {
			# "retail_price": 12598,
			"leasing_cost": 2500.68,
			"washing_cost": 8,
			"disinfection_cost": 15,
			"cost_permin": 0.26
		}
	},
	"cng": {
		"VW Golf 7 1.4 TGI 2018": {
			# "retail_price": 18374,
			"leasing_cost": 3324.24,
			"washing_cost": 8,
			"disinfection_cost": 15,
			"cost_permin": 0.26
		}
	},
	"electric": {
		"VW e-Golf 2018": {
			# "retail_price": 24867.28,
			"leasing_cost": 5053.32,
			"washing_cost": 8,
			"disinfection_cost": 15,
			"cost_permin": 0.26
		},
		"Smart fortwo Electric Drive 2018": {
			# "retail_price": 16279.92,
			"leasing_cost": 3690,
			"washing_cost": 8,
			"disinfection_cost": 15,
			"cost_permin": 0.19
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
		"hardware": 4500,
		"labor": 1544,
		"materials": 1112,
		"permit": 82,
		"taxes": (22 / 100) * 4500,
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
	"pole_useful_life": 10
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

administrative_cost_conf = {
	"relocation_workers_hourly_cost": 23,
}
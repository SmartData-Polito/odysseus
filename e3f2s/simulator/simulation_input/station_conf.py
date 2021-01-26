station_conf = {
	"gasoline": {
		"fuel_type": "gasoline"
	},
	"diesel": {
		"fuel_type": "diesel"
	},
	"lpg": {
		"fuel_type": "lpg"
	},
	"cng": {
		"fuel_type": "cng"
	},
	"electric": {
		"wall_plug": {
			"fuel_type": "electric",
			"profile_type": "wall_plug",
			"voltage_output": 230,
			"current_output": 10,
			# "cost": charging_station_costs["wall_plug"]
		},
		"single_phase_1": {
			"fuel_type": "electric",
			"profile_type": "single_phase_1",
			"voltage_output": 230,
			"current_output": 16,
			# "cost": charging_station_costs["single_phase_1"]
		},
		"single_phase_2": {
			"fuel_type": "electric",
			"profile_type": "single_phase_2",
			"voltage_output": 230,
			"current_output": 32,
			# "cost": charging_station_costs["single_phase_2"]
		},
		"three_phase_1": {
			"fuel_type": "electric",
			"profile_type": "three_phase_1",
			"voltage_output": 400,
			"current_output": 16,
			# "cost": charging_station_costs["three_phase_1"]
		},
		"three_phase_2": {
			"fuel_type": "electric",
			"profile_type": "three_phase_2",
			"voltage_output": 400,
			"current_output": 32,
			# "cost": charging_station_costs["three_phase_2"]
		},
		"three_phase_3": {
			"fuel_type": "electric",
			"profile_type": "three_phase_3",
			"voltage_output": 400,
			"current_output": 63,
			# "cost": charging_station_costs["three_phase_3"]
		},
		"dcfc_1": {
			"fuel_type": "electric",
			"profile_type": "dcfc_1",
			"voltage_output": 450,
			"current_output": 112,
			# "cost": charging_station_costs["dcfc_1"]
		},
		"dcfc_2": {
			"fuel_type": "electric",
			"profile_type": "dcfc_2",
			"voltage_output": 400,
			"current_output": 325,
			# "cost": charging_station_costs["dcfc_2"]
		},
	}
}

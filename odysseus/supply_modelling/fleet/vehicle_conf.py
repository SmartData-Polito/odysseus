vehicle_conf = {

	"gasoline": {
		"my_vehicle": {
			"engine_type": "gasoline",
			"fuel_capacity": 0.1,
			"vehicle_efficiency": 100,
			"n_seats": 5,
		},
		"Fiat 500 1.2": {
			"engine_type": "gasoline",
			"fuel_capacity": 35,
			"vehicle_efficiency": 5.8,
			"n_seats": 5,
			# "costs": vehicle_cost["gasoline"]["VW Golf 7 1.0 TSI 2018"]
		},
		"Seat Leon 1.5 TSI 2020": {
			"engine_type": "gasoline",
			"fuel_capacity": 45,
			"vehicle_efficiency": 14.75,
			"n_seats": 5,
			# "costs": vehicle_cost["gasoline"]["VW Golf 7 1.0 TSI 2018"]
		},
		"VW Golf 7 1.0 TSI 2018": {
			"engine_type": "gasoline",
			"fuel_capacity": 50,
			"vehicle_efficiency": 12.987,
			"n_seats": 5,
			# "costs": vehicle_cost["gasoline"]["VW Golf 7 1.0 TSI 2018"]
		}
	},

	"diesel": {
		"Seat Leon 2.0 TDI 2020": {
			"engine_type": "diesel",
			"fuel_capacity": 45,
			"vehicle_efficiency": 14.16,
			"n_seats": 5,
			# "costs": vehicle_cost["gasoline"]["VW Golf 7 1.0 TSI 2018"]
		},
		"VW Golf 7 2.0 TDI 2018": {
			"engine_type": "diesel",
			"fuel_capacity": 50,
			"vehicle_efficiency": 16.393,
			"n_seats": 5,
			# "costs": vehicle_cost["diesel"]["VW Golf 7 2.0 TDI 2018"]
		}
	},

	"lpg": {
		"Kia Rio 1.2 GPL 2020": {
			"engine_type": "lpg",
			"fuel_capacity": 37,
			"vehicle_efficiency": 14.512,
			"n_seats": 5,
			# "costs": vehicle_cost["gasoline"]["VW Golf 7 1.0 TSI 2018"]
		},
		"Opel Corsa 1.4 EcoTech": {
			"engine_type": "lpg",
			"fuel_capacity": 35,
			"vehicle_efficiency": 11.1429,
			# "retail_price": 17220,
			"n_seats": 5,
			# "costs": vehicle_cost["lpg"]["Opel Corsa 1.4 EcoTech"]
		}
	},

	"cng": {
		"Seat Leon 1.5 TGI 2020": {
			"engine_type": "cng",
			"fuel_capacity": 17.3,
			"vehicle_efficiency": 26.089,
			"n_seats": 5,
			# "costs": vehicle_cost["gasoline"]["VW Golf 7 1.0 TSI 2018"]
		},
		"VW Golf 7 1.4 TGI 2018": {
			"engine_type": "cng",
			"fuel_capacity": 15,
			"vehicle_efficiency": 18.8679,
			# "retail_price": 18374,
			"n_seats": 5,
			# "costs": vehicle_cost["cng"]["VW Golf 7 1.4 TGI 2018"]
		}
	},

	"electric": {
		"Fiat 500e 2020": {
			"engine_type": "electric",
			"fuel_capacity": 37.3,
			"vehicle_efficiency": 5.263,
			"n_seats": 5,
			# "costs": vehicle_cost["electric"]["VW e-Golf 2018"],
			"max_charg_power": {
				"wall_plug": 2300,
				"single_phase_1": 3700,
				"single_phase_2": 7200,
				"three_phase_1": 11000,
				"three_phase_2": 11000,
				"three_phase_3": 11000,
				"dcfc_1": 40000,
				"dcfc_2": 60000
			}
		},
		"VW e-Golf 2018": {
			"engine_type": "electric",
			"fuel_capacity": 32,
			"vehicle_efficiency": 10.309,
			"n_seats": 5,
			# "costs": vehicle_cost["electric"]["VW e-Golf 2018"],
			"max_charg_power": {
				"wall_plug": 2300,
				"single_phase_1": 3700,
				"single_phase_2": 7200,
				"three_phase_1": 7200,
				"three_phase_2": 7200,
				"three_phase_3": 7200,
				"dcfc_1": 39000,
				"dcfc_2": 39000
			}
		},
		"Smart fortwo Electric Drive 2018": {
			"engine_type": "electric",
			"fuel_capacity": 16.7,
			"vehicle_efficiency": 7.6046,
			"n_seats": 2,
			# "costs": vehicle_cost["electric"]["Smart fortwo Electric Drive 2018"],
			"max_charg_power": {
				"wall_plug": 2300,
				"single_phase_1": 3700,
				"single_phase_2": 4600,
				"three_phase_1": 3700,
				"three_phase_2": 4600,
				"three_phase_3": 4600,
				"dcfc_1": 4600,
				"dcfc_2": 4600
			}
		},
		"Xiaomi Mi Electric Scooter Pro 2": {
			"engine_type": "electric",
			"fuel_capacity": 0.335,
			"vehicle_efficiency": 1 / 0.011,
			"n_seats": 1,
			"max_charg_power": {
				"wall_plug": 2300,
				"inf": 1000000
			}
		},
		"generic e-scooter": {
			"engine_type": "electric",
			"fuel_capacity": 0.425,
			"vehicle_efficiency": 1 / 0.011,
			"n_seats": 1,
			"max_charg_power": {
				"wall_plug": 2300,
				"inf": 1000000
			}
		}
	}
}

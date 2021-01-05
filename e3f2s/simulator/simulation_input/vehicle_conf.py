from e3f2s.utils.cost_utils import vehicle_cost
vehicle_conf = {
	"gasoline": {
		"VW Golf 7 1.0 TSI 2018": {
			"engine_type": "gasoline",
			"fuel_capacity": 50,
			"consumption": 12.987,
			"n_seats": 5,
			"costs": vehicle_cost["gasoline"]["VW Golf 7 1.0 TSI 2018"]
		}
	},
	"diesel": {
		"VW Golf 7 2.0 TDI 2018": {
			"engine_type": "diesel",
			"fuel_capacity": 50,
			"consumption": 16.393,
			"n_seats": 5,
			"costs": vehicle_cost["diesel"]["VW Golf 7 2.0 TDI 2018"]
		}
	},
	"lpg": {
		"Opel Corsa 1.4 EcoTech": {
			"engine_type": "lpg",
			"fuel_capacity": 35,
			"consumption": 11.1429,
			"retail_price": 17220,
			"n_seats": 5,
			"costs": vehicle_cost["lpg"]["Opel Corsa 1.4 EcoTech"]
		}
	},
	"cng": {
		"VW Golf 7 1.4 TGI 2018": {
			"engine_type": "cng",
			"fuel_capacity": 15,
			"consumption": 18.8679,
			"retail_price": 18374,
			"n_seats": 5,
			"costs": vehicle_cost["cng"]["VW Golf 7 1.4 TGI 2018"]
		}
	},
	"electric": {
		"VW e-Golf 2018": {
			"engine_type": "electric",
			"fuel_capacity": 32,
			"consumption": 10.309,
			"n_seats": 5,
			"costs": vehicle_cost["electric"]["VW e-Golf 2018"],
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
			"consumption": 7.6046,
			"n_seats": 2,
			"costs": vehicle_cost["electric"]["Smart fortwo Electric Drive 2018"],
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
		}
	}
}

import os
import json


def read_energy_mix_config():
	db_path = os.path.join(
		os.path.dirname(__file__),
		"energy_mix_config.json"
	)
	f = open(db_path, "r")
	energymix_db = json.load(f)
	f.close()
	return energymix_db


class EnergyMix:
	def __init__(self, city, year):
		self.city_name = city
		self.year = str(year)
		self.lca_co2_elect_sources = {
			"nuclear": 12,  # g/kWh
			"natural_gas": 490,  # g/kWh
			"coal": 910,  # g/kWh
			"oil": 650,  # g/kWh
			"biomass": 230,  # g/kWh
			"other": 490,  # g/kWh
			"hydro": 24,  # g/kWh
			"wind": 11,  # g/kWh
			"waste": 620,  # g/kWh
			"geothermal": 38,  # g/kWh
			"solar": 11,  # g/kWh
		}
		self.energy_electr_sources = {
			"nuclear": 2.9,  # MJ/MJel
			"natural_gas": 1.15,  # MJ/MJel
			"coal": 1.69,  # MJ/MJel
			"oil": 1.76,  # MJ/MJel
			"biomass": 2.985,  # MJ/MJel
			"other": 1.76,  # MJ/MJel
			"hydro": 0,  # MJ/MJel
			"wind": 0.07,  # MJ/MJel
			"waste": 0,  # MJ/MJel
			"geothermal": 0,  # MJ/MJel
			"solar": 0,  # MJ/MJel
		}
		self.energymix_db = read_energy_mix_config()
		if self.city_name in ["Roma", "Torino", "Milano", "test_city"]:
			self.energy_mix_conf = self.energymix_db["Italy"][self.year]
		elif self.city_name == "Amsterdam":
			self.energy_mix_conf = self.energymix_db["Netherlands"][self.year]
		elif self.city_name in ["Hamburg", "Berlin"]:
			self.energy_mix_conf = self.energymix_db["Germany"][self.year]
		elif self.city_name in ["Wien"]:
			self.energy_mix_conf = self.energymix_db["Austria"][self.year]
		elif self.city_name in ["Vancouver"]:
			self.energy_mix_conf = self.energymix_db["Canada"][self.year]
		elif self.city_name in ["Louisville", "Minneapolis", "Austin", "Norfolk", "Kansas City", "Chicago", "Calgary"]:
			self.energy_mix_conf = self.energymix_db["US"][self.year]
		elif self.city_name.startswith("my_city"):
			self.energy_mix_conf = self.energymix_db["dummy_country"][self.year]
		else:
			raise Exception(
				"Energy mix unavailable for city:{}, year:{}".format(self.city_name, self.year)
			)

	# TODO -> automate city-country association
	def evaluate_emissions(self):
		tot_emission = 0
		for i in list(self.lca_co2_elect_sources.keys()):
			tot_emission = tot_emission + self.lca_co2_elect_sources[i] * self.energy_mix_conf[i] / 100
		return tot_emission  # gCO2eq/kWh

	def evaluate_energy(self):
		tot_energy = 0
		for i in list(self.lca_co2_elect_sources.keys()):
			tot_energy = tot_energy + self.energy_electr_sources[i] * self.energy_mix_conf[i] / 100
		return tot_energy  # MJ/MJelectricity

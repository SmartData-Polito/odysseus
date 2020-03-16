import os

from DataStructures.City import City

from SimulationInput.confs.sim_general_conf import sim_general_conf

for city in [
				"Torino",
			]:

	sim_general_conf["city"] = city
	sim_general_conf["bin_side_length"] = 500

	city_obj = City \
		(city,
		 sim_general_conf)

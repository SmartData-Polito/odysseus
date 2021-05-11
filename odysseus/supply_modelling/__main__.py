import argparse

from odysseus.supply_modelling.supply_model import SupplyModel

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--cities", nargs="+",
    help="specify cities"
)

parser.add_argument(
    "-d", "--data_source_ids", nargs="+",
    help="specify data source ids"
)

parser.add_argument(
    "-v", "--num_vehicles", nargs="+",
    help="specify num vehicles"
)

parser.add_argument(
    "-p", "--tot_n_charging_poles", nargs="+",
    help="specify total number of charging poles"
)

parser.add_argument(
    "-z", "--n_charging_zones", nargs="+",
    help="specify number of charging zones"
)

parser.add_argument(
    "-y", "--year", nargs="+",
    help="specify year"
)

parser.add_argument(
    "-a", "--distributed_cps", nargs="+",
    help="specify if cps are distributed (True or False)"
)


available_policy = ["num_parkings", "old_manual", "real_positions", "realpos_numpark"]
parser.add_argument(
    "-pp", "--cps_placement_policy", nargs="+",
    help="specify placement policy. Available options: "+str(available_policy)
)

parser.add_argument(
    "-w", "--n_relocation_workers", nargs="+",
    help="Specify number of relocation workers"
)




parser.set_defaults(
    cities=["Amsterdam"],
    data_source_ids=["big_data_db"],
    num_vehicles=["500"],
    tot_n_charging_poles=["100"],
    n_charging_zones=["10"],
    year=["2017"],
    distributed_cps="True",
    cps_placement_policy="num_parkings",
    n_relocation_workers=1
)


args = parser.parse_args()
t_or_f = True if args.distributed_cps[0].lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'] else False

print(t_or_f)
print(args)
#self.sim_scenario_conf = conf_tuple[1]

supply_model_conf = dict()
#supply_model_conf.update(self.sim_scenario_conf)
supply_model_conf.update({
    "city": args.cities[0],
    "data_source_id": args.data_source_ids[0],
    "n_vehicles": int(args.num_vehicles[0]),
    "tot_n_charging_poles": int(args.tot_n_charging_poles[0]),
    "n_charging_zones": int(args.n_charging_zones[0]),
    "distributed_cps":bool(args.distributed_cps),
    "cps_placement_policy":args.cps_placement_policy,
    "n_relocation_workers":int(args.n_relocation_workers)
})
supply_model = SupplyModel(supply_model_conf, int(*args.year))


vehicles_soc_dict, vehicles_zones, available_vehicles_dict = supply_model.init_vehicles()

print("Vehicle soc dict:\n"+str(vehicles_soc_dict))
print("Vehicle zones:\n"+str(vehicles_zones))
print("Available vehicles dict:\n"+str(sorted(available_vehicles_dict.items())))

supply_model.init_charging_poles()
supply_model.init_relocation()

print(supply_model.initial_relocation_workers_positions)

print("######################################################\nEnergy Mix")
print("Evaluate energy " +str(supply_model.energy_mix.evaluate_energy())+" (MJ/MJelectricity)")
print("Evaluate energy " +str(supply_model.energy_mix.evaluate_emissions())+" (gCO2eq/kWh)")
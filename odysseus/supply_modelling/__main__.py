
#per sopprimere i warning sui centroidi
import warnings
warnings.simplefilter("ignore", UserWarning)
######
import argparse
import os
import pickle
from odysseus.supply_modelling.supply_model import SupplyModel


def same_parameters(default, parser):
    return parser.cities==default["cities"] and parser.data_source_ids==default["data_source_ids"] and parser.num_vehicles==default["num_vehicles"] and parser.tot_n_charging_poles==default["tot_n_charging_poles"] and parser.n_charging_zones==default["n_charging_zones"] and parser.year==default["year"] and parser.distributed_cps==default["distributed_cps"] and parser.cps_placement_policy==default["cps_placement_policy"] and parser.n_relocation_workers==default["n_relocation_workers"] and parser.folder_name==default["folder_name"]

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

parser.add_argument(
    "-r", "--recover_supply_model", nargs="+",
    help="""
        specify the folder from which recover an existing supply model. 
        The folder must be in odysseus/supply_modelling/supply_models/<CITYNAME> 
        """
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
parser.add_argument(
    "-f", "--folder_name", nargs="+",
    help="Specify saving folder name "
)

default = {
    "cities":["Amsterdam"],
    "data_source_ids":["big_data_db"],
    "num_vehicles":["500"],
    "tot_n_charging_poles":["100"],
    "n_charging_zones":["10"],
    "year":["2017"],
    "distributed_cps":"True",
    "cps_placement_policy":"num_parkings",
    "n_relocation_workers":1,
    "folder_name":"",
    "recover_supply_model":""
}


parser.set_defaults(
    cities=default["cities"],
    data_source_ids=default["data_source_ids"],
    num_vehicles=default["num_vehicles"],
    tot_n_charging_poles=default["tot_n_charging_poles"],
    n_charging_zones=default["n_charging_zones"],
    year=default["year"],
    distributed_cps=default["distributed_cps"],
    cps_placement_policy=default["cps_placement_policy"],
    n_relocation_workers=default["n_relocation_workers"],
    folder_name=default["folder_name"],
    recover_supply_model=default["recover_supply_model"]
)


args = parser.parse_args()
t_or_f = True if args.distributed_cps[0].lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'] else False

if args.recover_supply_model != "":
    #controllo che il file esista
    folder = args.recover_supply_model
    folder_path = os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models",
                               args.cities[0], folder[0])
    if not os.path.exists(os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models",
                               args.cities[0])):
        print("No "+args.cities[0]+" data stored.")
        exit(3)
    if not os.path.exists(folder_path):
        print("Non-existent folder.")
        print("Available folders", str(os.listdir(
            os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models",
                         args.cities[0]))))
        exit(1)
    else:
        if "supply_model.pickle" not in os.listdir(folder_path):
            print("The folder must contain the supply_model.pickle file")
            exit(2)
        else:
            with open(os.path.join(folder_path, "supply_model.pickle"), "rb") as f:
                supply_model = pickle.load(f)
    print("Existing object. I am recovering it...")
else:
    supply_model_conf = dict()
    #supply_model_conf.update(self.sim_scenario_conf)
    supply_model_conf.update({
        "city": args.cities[0],
        "data_source_id": args.data_source_ids[0],
        "n_vehicles": int(args.num_vehicles[0]),
        "tot_n_charging_poles": int(args.tot_n_charging_poles[0]),
        "n_charging_zones": int(args.n_charging_zones[0]),
        "distributed_cps":t_or_f,
        "cps_placement_policy":args.cps_placement_policy,
        "n_relocation_workers":int(args.n_relocation_workers)
    })

    supply_model = SupplyModel(supply_model_conf, int(*args.year)) # nel webapp bre-cambiato


    vehicles_soc_dict, vehicles_zones, available_vehicles_dict = supply_model.init_vehicles()
    supply_model.init_charging_poles()
    supply_model.init_relocation()

    ##Salvare su file le strutture dati
    #se c'è il saveflag salvo nel path che mi dice

    if args.folder_name != "":
        folder = args.folder_name[0]
    else:
        if same_parameters(default, args):
            #salvo nella cartella di default
            folder = "default_supply_model"
        else:
            folder = input("In which folder do you want to save the model? [type NO to not save]\t")
            if folder == "NO":
                exit(0)


    #cartella di default
    savepath = os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models", args.cities[0], folder)

    if not os.path.exists(savepath):
        os.makedirs(savepath)

    with open(os.path.join(savepath, "supply_model.pickle"), "wb") as f:
        pickle.dump(supply_model, f)

    print("Model saved in folder:", savepath)




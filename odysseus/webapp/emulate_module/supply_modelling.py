
#per sopprimere i warning sui centroidi
from odysseus.webapp.emulate_module.demand_modelling import DEFAULT_FORM
import warnings
warnings.simplefilter("ignore", UserWarning)
######
import os
import pickle
from odysseus.supply_modelling.supply_model import SupplyModel
import namegenerator

DEFAULT_FORM = {
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
class SupplyModelling:
    
    def __init__(self,form_inputs=DEFAULT_FORM):
        self.form =form_inputs
        self.cities=form_inputs["cities"]
        self.data_source_ids=form_inputs["data_source_ids"]
        self.num_vehicles=form_inputs["num_vehicles"]
        self.tot_n_charging_poles=form_inputs["tot_n_charging_poles"]
        self.n_charging_zones=form_inputs["n_charging_zones"]
        self.year=form_inputs["year"]
        self.distributed_cps=form_inputs["distributed_cps"]
        self.cps_placement_policy=form_inputs["cps_placement_policy"]
        self.n_relocation_workers=form_inputs["n_relocation_workers"]
        self.folder_name=form_inputs["folder_name"]
        self.recover_supply_model=form_inputs["recover_supply_model"]

        #self.available_policy = ["num_parkings", "old_manual", "real_positions", "realpos_numpark"]

    def run(self):
        t_or_f = True if self.distributed_cps[0].lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'] else False
        if self.recover_supply_model != "":
            #controllo che il file esista
            folder = self.recover_supply_model
            folder_path = os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models",
                                    self.cities[0], folder[0])
            if not os.path.exists(os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models",
                                    self.cities[0])):
                print("No "+self.cities[0]+" data stored.")
                exit(3)
            if not os.path.exists(folder_path):
                print("Non-existent folder.")
                print("Available folders", str(os.listdir(
                    os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models",
                                self.cities[0]))))
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
                "city": self.cities[0],
                "data_source_id": self.data_source_ids[0],
                "n_vehicles": int(self.num_vehicles[0]),
                "tot_n_charging_poles": int(self.tot_n_charging_poles[0]),
                "distributed_cps":t_or_f,
                "n_charging_zones": int(self.n_charging_zones[0]),
                "cps_placement_policy":self.cps_placement_policy,
                "n_relocation_workers":int(self.n_relocation_workers)
            })
            print(supply_model_conf)
            supply_model = SupplyModel(supply_model_conf, int(*self.year))
            print("FASFAFA")
            vehicles_soc_dict, vehicles_zones, available_vehicles_dict = supply_model.init_vehicles()
            supply_model.init_charging_poles()
            supply_model.init_relocation()
            print("EHI")
            ##Salvare su file le strutture dati
            #se c'è il saveflag salvo nel path che mi dice

            if self.folder_name != "":
                folder = self.folder_name[0]
            else:
                if same_parameters(self.form,DEFAULT_FORM):
                    #salvo nella cartella di default
                    folder = "default_supply_model"
                else:
                    folder = namegenerator.gen()
            print(folder)
            #cartella di default
            savepath = os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models", self.cities[0], folder)

            if not os.path.exists(savepath):
                os.makedirs(savepath)

            with open(os.path.join(savepath, "supply_model.pickle"), "wb") as f:
                pickle.dump(supply_model, f)

            print("Model saved in folder:", savepath)
            
            return folder

def same_parameters(obj,default=DEFAULT_FORM):
    return obj.cities==default["cities"] and obj.data_source_ids==default["data_source_ids"] and obj.num_vehicles==default["num_vehicles"] and obj.tot_n_charging_poles==default["tot_n_charging_poles"] and obj.n_charging_zones==default["n_charging_zones"] and obj.year==default["year"] and obj.distributed_cps==default["distributed_cps"] and obj.cps_placement_policy==default["cps_placement_policy"] and obj.n_relocation_workers==default["n_relocation_workers"] and obj.folder_name==default["folder_name"]






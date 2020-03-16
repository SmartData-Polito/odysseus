def remap_plates (events):
    ass_dict = {
            sorted(events.plate.unique())[i]: i 
            for i in range(len(sorted(events.plate.unique())))
        }
    events.loc[:, "plate"] = events.plate.replace(ass_dict)
    return ass_dict, events


def soc_to_kwh(soc, a=0., b=3.5):
    return (b - a) / (100) * (soc - 100) + b


def get_soc_delta (distance, 
                   battery_capacity = 0.25,
                   vehicle_energy_efficiency = 0.011):
    return (vehicle_energy_efficiency * distance * 100)\
    / (battery_capacity)

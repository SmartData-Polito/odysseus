from e3f2s.webapp.apis import create_app
#from e3f2s.webapp.emulate_module.simulator import Simulator
from e3f2s.webapp.emulate_module.city_data_manager import CityDataManager
from e3f2s.webapp.emulate_module.demand_modelling import DemandModelling

app = create_app()

if __name__ == '__main__':  # conditional only true if we run the script directly
    #app.run(debug=True)
    x = CityDataManager()
    x.run()
    a = DemandModelling()
    a.run()


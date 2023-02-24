.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Simulator
=================================

.. toctree::
   :hidden:
   :maxdepth: 0
   :caption: Moduli:

Introduction
-----------------------------

This module is responsible for running mobility simulations starting from the following configurations:

- **General Run Configuration**:
   - Specify namespace (city, data_source_id, output_folder)
   - Specify option to increase/decrease output verbosity
   - Specify automatic plotting options

- **Demand Configuration**:
   - Specify how mobility requests samples are generated
   - Specify user behavior when searching for a vehicle
   - Specify user behavior regarding cooperation with system operators

- **Supply Configuration**:
   - Specify energy supply configuration
   - Specify fleet configuration
   - Specify charging policy and parameters
   - Specify relocation policy and parameters

The files where those configurations are respectively:

- **sim_general_conf.py**:

- **demand_model_conf.py**:

- **supply_model_conf.py**:

Example configuration folder path:

      ::

          my-odysseus-folder
          ├── odysseus
          │   ├── simulator
          │   │   ├── simulation_configs_py
          │   │   │   ├── test
          │   │   │   │   ├── custom_trips_test
          │   │   │   │   │   ├── sim_general_conf.py
          │   │   │   │   │   ├── demand_model_conf.py
          │   │   │   │   │   ├── supply_model_conf.py


Each configuration is a Python script containing the definition of a single variable.
Those variable are dictionary of lists where the keys correspond to the name of a certain parameter and the list
contains the desired values for such parameter.
Notice that each configuration is basically a grid of parameters and selecting a very big grid might result in
memory fault and/or very long execution time.

Let's go into the details of each configuration.


General Run Configuration
-----------------------------

- Parameters list:

   - **city**, string
      - Name of the city used in simulation
   - **data_source_id**, string
      - Name of the data source used for building the data scenario
   - **sim_scenario_name**, string
      - Name of the output folder where results and eventually figures will be saved.
   - **save_history**, boolean
      - Save list of events during simulation time.
   - **history_to_file**, boolean
      - Export data structures containing complete lists of booking requests, bookings, charges..
   - **exclude_sim_output_obj**, boolean
      - Export/exclude binary representation of SimOutput object
   - **exclude_geo_grid**, boolean
      - Export/exclude geographic data structures
   - **exclude_events_files**, boolean
      - Export/exclude full event logs (requests, trips, recharges, ...)
   - **exclude_resources_files**, boolean
      - Export/exclude full resources logs (zones, vehicles, charging stations, ...)
   - **auto_plotting**, boolean
      - Enable automatic plotting in single run mode
   - **year**, integer
      - Year to use in the what-if simulation
   - **month_start**, integer
      - Month when the simulation start from
   - **max_sim_hours**, integer
      - Number of hours to simulate


- Example:

      .. code-block:: console

            sim_general_config_grid = {

                # City and data source parameters
                "city": ["test_city"],
                "data_source_id": ["custom_trips"],

                # Run parameters
                "sim_scenario_name": ["custom_trips_test"],
                "save_history": [True],
                "history_to_file": [True],
                "exclude_sim_output_obj": [False],
                "exclude_geo_grid": [False],
                "exclude_events_files": [False],
                "exclude_resources_files": [False],
                "auto_plotting": [True],

                # Time  parameters
                "year": [2020],
                "month_start": [9],
                "max_sim_hours": [24 * 30]

            }

Demand Configuration
-----------------------------

   - **demand_model_type**, string
      - Specify the demand model to use in the simulation
   - **requests_rate_factor**, float
      - Specify a factor to amplify/reduce average demand in input data
      - Can only be used when **demand_model_type** is not "trace"
   - **vehicle_research_policy**, string
      - Specify the way how users search for a vehicle
   - **avg_speed_kmh_mean**, float
      - The average speed of a trip considering reservation time and parking time
   - **max_duration**, int [seconds]
      - Eventually impose a maximum duration to trips
   - **fixed_driving_distance**, int [meters]
      - Eventually impose the same driving distance for each trip
   - **user_contribution**, boolean
      - Specify whether users can contribute to charging operations
   - **user_contribution_policy**, string
      - Specify the way how users eventually contribute to charging operations
   - **willingness**, float
      - Probability that a generic user will contribute

   - Example:

      .. code-block:: console

            demand_model_config_grid = {

                "demand_model_type": ["trace"],
                "requests_rate_factor": [1],
                "vehicle_research_policy": ["zone"],
                "avg_speed_kmh_mean": [1],
                "max_duration": [60 * 60 * 3],
                "fixed_driving_distance": [None],
                "user_contribution_policy": [""],
                "user_contribution": [False],
                "willingness": [0],

            }

Supply Configuration
-----------------------------

   - **year_energymix**, integer as string (es. "2023")
      - Specify the demand model to use in the simulation

   - **vehicle_model_name**, string
      - Specify vehicle model to include in the simulation
      - Must present in vehicle_conf.py

   - **engine_type**, string
      - Specify type of engine that vehicles use

   - **fuel_capacity**, float
      - Specify capacity of tank or battery

   - **vehicle_efficiency**, float [km/l or km/kwh]
      - Specify how many kilometers the vehicle can do with 1 unit of fuel

   - **vehicle_config_mode**, string
      - Specify the way how fleet size and initial placement are configured
      - Default: "sim_config" (use the configuration file to specify parameters)

   - **vehicle_initial_placement**, string
      - Specify the way how vehicles are placed at the beginning of the simulations

   - **n_vehicles**, integer
      - Specify number of vehicles in the fleet

   - **charging_config_mode**, string
      - Specify the way how charging operations are configured
      - Default: "sim_config" (use the configuration file to specify parameters)

   - **distributed_cps**, boolean
      - Specify whether or not to create a charging infrastructure

   - **system_cps**, boolean
      - Specify whether the charging infrastructure is private to the system operator

   - **profile_type**, string
      - Specify charging profile

   - **stations_placement_config_mode**, string
      - Specify the way how charging stations placement is configured
      - Default: "sim_config" (use the configuration file to specify parameters)

   - **tot_n_charging_poles**, int
      - Total number of charging poles

   - **n_charging_zones**, int
      - Number of charging zones

   - **cps_placement_policy**, string
      - Specify the way how charging stations are placed

   - **charging_strategy**, string
      - Specify the way how charging operations are performed
      - For now only "reactive" is available

   - **charging_relocation_strategy**, string
      - Specify the way how vehicles are assigned to a charging station when they need charge

   - **charging_relocation_strategy**, string
      - Specify the way how vehicles are moved after a charging operation

   - **queuing**, boolean
      - Specify whether queuing is allowed at charging stations
      - For now only "reactive" is available

   - **alpha_policy**, string
      - Specify policy to set the lower charging threshold

   - Example:

      .. code-block:: console

            supply_model_config_grid = {

                # -> energy supply

                "year_energymix": ["2023"],

                # -> vehicle configuration

                "vehicle_model_name": ["Smart fortwo Electric Drive 2018"],
                "engine_type": ["electric"],
                "fuel_capacity": [16.7],
                "vehicle_efficiency": [5.263],

                # -> fleet size and initial placement

                "vehicles_config_mode": ["sim_config"],
                "vehicles_initial_placement": ["random_greedy"],
                "n_vehicles": [400],

                # -> charging

                "charging_config_mode": ["sim_config"],
                "distributed_cps": [True],
                "system_cps": [True],
                "profile_type": ["single_phase_1"],

                "stations_placement_config_mode": ["sim_config"],
                "tot_n_charging_poles": [50],
                "n_charging_zones": [30],
                "cps_placement_policy": ["num_parkings"],

                "charging_strategy": ["reactive"],
                "charging_relocation_strategy": ["closest_free"],
                "charging_return_strategy": ["no_return"],
                "queuing": [True],
                "alpha_policy": ['auto'],

                "beta": [100],

                "n_workers": [1],

                # -> battery swap

                "battery_swap": [False],
                "avg_reach_time": [0],
                "avg_service_time": [0],

                # -> relocation

                "relocation": [False],
                "relocation_strategy": [""],

                "relocation_technique": [frozenset({})],

                "n_relocation_workers": [1],
                "avg_relocation_speed": [20],  # km/h
                "relocation_capacity": [1],
                "relocation_profitability_check": [False],
                "relocation_vehicle_consumption": [7],  # l/100km
                "diesel_price": [0.65],  # $/l (USA)
                "unlock_fee": [1],  # $
                "rent_fee": [0.15],  # $/min
                "avg_relocation_distance": [1],  # km
                "avg_trip_duration": [10],  # min

            }

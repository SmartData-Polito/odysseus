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
   - **data_source_id**, string
   - **sim_scenario_name**, string
      - Name of the output folder where results and eventually figures will be saved.
   - **save_history**, boolean
      - Save list of events during simulation time.
   - **history_to_file**, boolean
      - Export data structures containing complete lists of booking requests, bookings, charges..
   - **exclude_sim_output_obj**, boolean
   - **exclude_geo_grid**, boolean
   - **exclude_events_files**, boolean
   - **exclude_resources_files**, boolean
   - **auto_plotting**, boolean
   - **year**, boolean
   - **month_start**, boolean
   - **max_sim_hours**, boolean


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

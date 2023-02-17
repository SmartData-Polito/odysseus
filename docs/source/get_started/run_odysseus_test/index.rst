Run ODySSEUS test
=================================

.. toctree::
   :hidden:
   :maxdepth: 0
   :caption: Moduli:

Introduction
---------------------------------------------------

Odysseus data are organised in nested folders and stored in a public cloud bucket.

The easiest way to start is to download the sample data and create a copy of the nested folder structure in your local file system.

Download sample data from `here`_.

.. _here: https://storage.googleapis.com/odysseus_paper/data_backup/data/test_city/raw/trips/custom_trips/custom_trips.csv


Folder structure:

      ::

          my-odysseus-folder
          ├── data
          │   ├── test_city
          │   │   ├── raw
          │   │   │   ├── trips
          │   │   │   │   ├── custom_trips
          │   │   │   │   │   ├── custom_trips.csv


The handiest and simplest data format for ODySSEUS are trips stored in a .csv file, so let's start from them.

City Data Manager - Geo Trips
---------------------------------------------------

Start with the following command:

   .. code-block:: console

      python -m odysseus.city_data_manager.geo_trips -h

This will show a summary of command-line arguments needed to run this module, and it works for each of them.

Let's pick default parameters for now (which are set for the file system shown above), and let's run the module using:

   .. code-block:: console

      python -m odysseus.city_data_manager.geo_trips

Now you should see something happening in your ODySSEUS folder.
In particular this folder structure should have appeared:

      ::

          my-odysseus-folder
          ├── data
          │   ├── test_city
          │   │   ├── norm
          │   │   │   ├── trips
          │   │   │   │   ├── custom_trips
          │   │   │   │   │   ├── 2020_9.csv
          │   │   │   ├── od_trips
          │   │   │   │   ├── points ...
          │   │   │   │   ├── trips ...



This means we normalised our input data to a format ODySSEUS is able to ingest.

Next step is City Data Scenario.

City Data Scenario - Geo Trips
---------------------------------------------------

This module starts from normalised data to create an initial representation of the city as seen from provided mobility data.

Start with the following command:

   .. code-block:: console

      python -m odysseus.scenario

This triggers the creation of a city data scenario.

When the execution will be finished, the output of city data scenario is contained in the following folder:

      ::

          my-odysseus-folder
          ├── odysseus
          │   ├── city_scenario
          │   │   ├── test_city
          │   │   │   ├── test_scenario

Now we are ready to start with the simplest simulation.

Simulation
---------------------------------------------------

This module allows to run simulation campaigns starting from the data structures exposed by a city data scenario.

Each campaign may contains several folders containing settings for different configurations within the simulator.

You can find a test configuration in the following path:

      ::

          my-odysseus-folder
          ├── odysseus
          │   ├── simulator
          │   │   ├── simulation_configs_py
          │   │   │   ├── test


In order to run the test configuration you can run the following command:

   .. code-block:: console

      python -m odysseus.simulator -c test -cc custom_trips_test -r single_run

This should run your first simulation.

When the execution terminates, try to navigate in the following folder:

      ::

          my-odysseus-folder
          ├── odysseus
          │   ├── simulator
          │   │   ├── results
          │   │   │   ├── test_city
          │   │   ├── figures
          │   │   │   ├── test_city

In the "results" folder you will find all the data structures generated and saved by the simulation.

In the "figures" folder you can find some plots that Odysseus produces in single_run mode.

Congratulations, you made your first Odysseus simulation!

Now you can dive into the User Guide to better understand how the different modules work and how you can configure them.

Below are reported the default configurations used for this test simulation.
You will learn better about them later.

General Run Configuration
-----------------------------

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


.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Demand Modelling
=================================

.. toctree::
   :hidden:
   :maxdepth: 0
   :caption: Moduli:

Introduction
-----------------------------

The Demand Modelling module takes in input available training data (provided by City Data Scenario) and
exposes utilities to model, estimate and forecast mobility demand in a given scenario.

The main duties of the Demand Modelling module are:

   - Provide an interface for user behavior within shared mobility systems
      - Vehicle research policy
      - Vehicle selection policy
      - Trip acceptance policy
      - User contribution policies

   - Estimation of statistical models able to describe mobility in time and space starting from data
      - Baseline: simple count model
         - Estimate flows between OD pairs as a simple count of trips between an origin and a destination at a given time
      - OD-based Poisson model
         - Estimate flows between OD paris as the average rate between an origin and a destination at a given time
      - Poisson/KDE estimation and mobility samples generation [cit modello 1 e/o Maurizio Pinna]

   - Forecast shared mobility flows using Deep Learning
      - 3D-CLoST [cit paper originale Fiorini + paper scooter relocation]

   - Generate mobility samples starting from a fitted demand model

You can run the following command to visualise a short description of parameters for this module:

   .. code-block:: console

      python -m odysseus.demand_modelling -h

Let's start with the simplest model.

Simple count model
---------------------------------------------------

This model is designed to deal with simple dummy cases generated through the Virtual OD module.
It simply wraps the definition of an OD matrix providing utilities to generate trips according to a fixed flow
between an origin and a destination specified in the OD matrix. The flow is therefore interpreted as a simple count
of trips between an origin and a destination in a certain time slot.

In order to use this model, you must have created a virtual OD and its city scenario.

Then, you can run the following command:

   .. code-block:: console

      python -m odysseus.demand_modelling -c my_city -d my_data_source -t od_matrices -C my_scenario_folder -D my_demand_model_folder

This will create a folder where demand models are stored in the following path:

      ::

          my-odysseus-folder
          ├── odysseus
          │   ├── demand_modelling
          │   │   ├── city_demand_models
          │   │   │   ├── my_city
          │   │   │   │   ├── my_demand_model_folder
          │   │   │   │   │   ├── demand_model.pickle
          │   │   │   │   │   ├── demand_model_config.json
          │   │   │   │   │   ├── week_config.json


A brief explanation of the generated data structures:
   - **demand_model.pickle** contains the binary representation of the model
   - **demand_model_config.json** contains the configuration used for the model in .json format
   - **week_config.json** contains the time configuration as explained in the OD module

As previously mentioned, there is no real "fitting" for this simple case: it just wraps the OD matrix to provide an interface to generate trips.

Let's therefore introduce more meaningful demand models.

ODt model
---------------------------------------------------

This demand model allow to fit an OD matrix from trips data. For each tuple (origin, destination, time_slot),
the model estimates the average number of trips to generate in a uniform distribution within a hourly slot.

In order to use this model, you must have created a city scenario from trips data.

Then, you can run the following command:

   .. code-block:: console

      python -m odysseus.demand_modelling -c my_city -d my_data_source -t hourly_ods_count -C my_scenario_folder -D my_demand_model_folder

Finally, by setting the parameter "requests_rate_factor" available in the demand model configuration within the simulator, the demand profile set in
virtual OD data structures will be scaled according to "requests_rate_factor". Note that this will happen only at simulation time,
namely in this phase only the demand model in generated.

ODt KDE + Poisson model
---------------------------------------------------

This demand model allows, for each tuple (origin, destination, time_slot) to:

   - Estimate a rate of an exponential distribution used to model inter-arrival times of mobility requests
   - Fit a KDE model for spatial distribution of origins, destinations, and their relationship
   - Generate inter-arrival times of mobility requests in the simulator

This method allows to disaggregate spatial demand and remove strong correlations present
in historical data representing only satisfied mobility demand.
There are two available modes to set KDE bandwidth:

   - Set a fixed bandwidth (parameter "kde_bandwidth")
   - Fit dynamic bandwidths (not integrated but available through the paper ... and the repository ...)

In order to use this model, you must have created a virtual OD and its city scenario. Then, by setting the parameter
"kde_bandwidth" available in the demand model configuration, the module will fit a spatial demand model with the selected bandwidth
for each tuple (origin, destination, time_slot).

You can run the following command:

   .. code-block:: console

      python -m odysseus.demand_modelling -c my_city -d my_data_source -t hourly_ods_count -C my_scenario_folder
         -D my_demand_model_folder -k 0.1

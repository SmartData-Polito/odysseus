.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==========================
Get started with Odysseus
==========================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: API Reference:

   city_data_manager/index
   demand_modelling/index
   supply_modelling/index
   modules

Introduction
=============
odysseus is a software for simulation of shared electric fleets in urban environments. It is still a prototype in active development. However, it is already stable enough to be used for research activities. In order to understand what odysseus is capable of, please first read the three papers available in the folder */home/det_tesi/a.ciociola/input_simulator/papers*.

odysseus is composed by three main modules:

- **city_data_manager**: receives in input data from different sources and output a simulation-ready version of the same data.
- **simulator**: contains data structures and algorithms for actual simulations.
- **utils**: contains some utility functions used across the other modules.

In this tutorial, we focus on running our first simulation with odysseus.

Setup repository, environment and data
========================================

First, let's clone the public git repository and move data into the right folder. For now, we skip explanations about *city_data_manager* functionalities.

   .. code-block:: console

     git clone https://github.com/AleCioc/odysseus my-odysseus-folder
     cp -r /home/det_tesi/a.ciociola/input_simulator/data my-odysseus-folder/odysseus/city_data_manager


Then, let's install all the necessary libraries.

   .. code-block:: console

     pip install --user -r my-odysseus-folder/requirements.txt


Configuring simulation input
=============================

The folder *odysseus/simulator/simulation_input* contains configuration files for simulation.

In particular:

- **sim_configs_target.json**: contains the name of the configuration to run
- **sim_configs_versioned**: contains one folder for each saved configuration e.g. *sim_configs_versioned/turin_iscc_set1* contains the configuration for the first set of simulation used in ISCC paper.

Each configuration folder must contain the following Python files:

- **sim_run_conf.py**: specifies used data source, run mode (single_run or multiple_runs), number of cores to use in case of multiple runs, simulation type (trace-driven or model-driven) and output folder name
- **sim_general_conf.py**: specifies macroscopic parameters about spatial and temporal configuration, as well as fleet load factor policy.
- **single_run_conf.py**: specifies scenario configuration for single run
- **model_validation_conf.py**: special case of single run
- **multiple_runs_conf.py**: specifies scenario configuration for multiple runs
- **vehicle_config.py**: specifies vehicles characteristics
- **cost_conf.py**: specifies cost/revenue configuration

Let's create a new folder for a new configuration:


   .. code-block:: console

     cp -r /home/det_tesi/a.ciociola/input_simulator/ my-odysseus-folder/odysseus/simulator/simulation_input/sim_configs_versioned/

Modify configurations as you desire, then run the simulator:

   .. code-block:: console

     cd my-odysseus-folder/
     python -m odysseus.simulator

Let's wait for simulation to finish and let's check the results folder and the figures folder (figures are created automatically only in single run mode)

   .. code-block:: console

     ls my-odysseus-folder/simulator/results/Torino/single_run/test
     ls my-odysseus-folder/simulator/figures/Torino/single_run/test

Done! Now we can explore our results and eventually produce other analysis and plots.

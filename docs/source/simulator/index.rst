.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Simulator
=================================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Moduli:

Introduction
-----------------------------

- Create and run simulation scenarios based on supply and demand configurations.
- Support for trip-level simulations (single_run) and timeframe-level simulations (multiple_runs).
- Collect several performance metrics (satisfied demand, fleet handling cost, equivalent CO2 emissions, gross profit, ...)
- Detailed interface to analyse simulation results

Configuring simulation input
-----------------------------

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

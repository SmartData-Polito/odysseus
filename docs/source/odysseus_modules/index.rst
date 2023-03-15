.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ODySSEUS Modules
==========================

.. toctree::
   :hidden:
   :maxdepth: 0
   :caption: API Reference:

   city_data_manager/index
   demand_modelling/index
   supply_modelling/index
   simulator/index


ODySSEUS is composed by four main functional modules:

- City Data Manager (previously UMAP [4])
   - Generate or read data in two basic formats: OD matrix and trips.
   - Provide utilities to normalise data into a common format.
   - Provide a unified interface to access and analyse normalised data.

* Demand Modelling
   * Create different demand models using:
      * Poisson/KDE estimation and mobility samples generation [3]
      * Deep Learning to learn and forecast mobility demand [6]
   * Create demand-side simulation scenarios.

* Supply Modelling
   * Create fleets choosing between different modes and vehicles.
   * Create and configure refueling/charging infrastrucures and energy mix for electricity production.
   * Define operator strategies to manage its resources

* Simulator
   * Create and run simulation scenarios based on supply and demand configurations.
   * Collect several performance metrics (satisfied demand, fleet handling cost, equivalent CO2 emissions, gross profit, ...)


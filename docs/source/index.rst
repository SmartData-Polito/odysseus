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

   install_guide/index
   city_data_manager/index
   demand_modelling/index
   supply_modelling/index
   simulator/index
   modules

Introduction
=============

ODySSEUS is a data management and simulation software for mobility data, focused mostly on shared fleets in urban environments.

Its goal is to provide a general, easy-to-use framework to simulate shared mobility scenarios across different cities using real-world data.

Internally, it makes use of several open-source Python libraries for geospatial and mobility analysis, such as geopandas (https://geopandas.org/) and scikit-mobility [5] (https://scikit-mobility.github.io/scikit-mobility/).

ODySSEUS is composed by four main functional modules, each one coming with its own command line interface:

- **City Data Manager**
- **City Scenario**
- **Demand Modelling**
- **Supply Modelling**
- **Simulator**


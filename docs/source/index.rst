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

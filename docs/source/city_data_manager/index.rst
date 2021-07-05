.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

City Data Manager
=================================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Moduli:

   city_data_source/index
   city_geo_trips/index

The City Data Manager module takes care of data preprocessing. The simulator supports heterogeneous data sources thanks to this module which, starting from a generic input data format, transforms them following the same format adopted by the other simulator modules.
The module is divided into two submodules, City Geo Trips and City Data Source.

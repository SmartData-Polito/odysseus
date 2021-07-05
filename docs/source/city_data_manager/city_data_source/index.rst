.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

City Data Source
=================================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Moduli:

   geo_data_source.rst
   trips_data_gatherer.rst
   trips_data_source.rst

The City Data Source module is divided into three submodules that deal with adapting the data format. Data from different sources have different formats: for example, geographic positions can be indicated as GPS coordinates or the city can be divided into a grid and the cell in which you are located can be indicated. Geo Data Source takes care of standardizing geographic information.


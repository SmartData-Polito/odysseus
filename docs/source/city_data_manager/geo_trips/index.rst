.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Geo Trips Data Source
=================================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Moduli:

   geo_data_source.rst
   geo_trips_data_source.rst
   trips_data_source.rst

The Geo Trips Data Source module is divided into three submodules in order to handle several "sub-formats".
Data from different sources have indeed different formats, both regarding temporal and spatial information.

For example, geographic positions can be represented with identifiers of a specific tessellation managed by a specific city.
Similarly, time may be expressed as an aggregate slots (e.g. 8:30 - 9:00) for reasons of data anonymisation.

Geo Trips Data Source takes care of standardizing this information using statistical techniques for disaggregation and
by providing an extensible interface for different data providers and formats.

This interface is composed by the following abstract classes:

- **Trips Data Source**
   - Normalise column names, timestamping and categorical columns for trips data
- **Geo Data Source**
   - Normalise column names and acquire geometries for geospatial data
- **Geo Trips Data Source**
   - Harmonisation of trips and geospatial data
   - Spatial and temporal disaggregation
   - Generation of sample points from geometries (if coordinates are not provided) and from timestamps (if a precise timestamp is not provided)


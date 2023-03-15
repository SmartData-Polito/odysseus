.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

City Data Scenario
=================================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Moduli:

   city_scenario_from_wgs84_trips.rst
   city_scenario_from_virtual_od.rst


The City Data Scenario module takes in input a set of mobility data about a given city
(virtual or real, possibly heterogeneous data) and outputs a set of standard data structures
used by the following modules.


Depending on the specific run mode and parameters, City Data Scenario performs the following operations:
   - Extraction of temporal features from trips
      - Extraction of categorical time features such as hour, day, etc. from a timestamp.
   - Extraction of spatial features from trips
      - Deduce mobility area from data
      - Map points on a finite set of city zones
   - Outlier detection and trips filtering
      - Detect errors and wrong measurements in input trips, such as for example:
         - Negative distances/durations
         - Physically impossible speed
         - Presence of points external to the city area due to GPS errors.
         - Etc.
   - Extraction of supply characteristics from data
      - Deduce number of vehicles from input data
      - Deduce most common stop points of the fleet
   - Contextual data integration
      - Read other data about e.g. electricity production mix, weather tracks, Points of Interest, etc.
   - Initialisation and export of standard data structures

The standard data structures created by a City Data Scenario are:
   - Grid Matrix
   - Geo Grid
   - Valid zones
   - Neighbors Dictionary
   - "Known" Mobility Data ("training data")
   - "Unknown" Mobility Requests ("test data")
   - Dictionary of numerical parameters
   - Origin-Destination flows for each hour present in available data




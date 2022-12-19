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

   geo_trips/index
   od_matrices/index
   city_scenario/index

The City Data Manager module has the following responsibilities:

- Generate mobility data starting from simple configurations

- Validate mobility data provided as input

- Create a mobility data scenario for a given city, which can be a real world city or a virtual one.

The currently supported mobility data types are:

- **Geo Trips**
   - Record of a certain mobility trip with spatial and temporal information

- **Origin-Destination matrices**
   - Description of the flow between zones at different moments of the day, week, month, ...

The OD matrices module allows you to generate fresh new data and simple scenarios to familiarise with ODySSEUS.

If you are interested in feeding ODySSEUS with tabular trips data, jump to Geo Trips.

As soon as you have successfully created or loaded your mobility data, as described in the modules mentioned above,
it will be time to explore the **City Data Scenario**, responsible for creating data structures used across the whole software.


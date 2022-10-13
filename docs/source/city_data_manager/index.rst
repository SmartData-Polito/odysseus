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

The City Data Manager module takes care of data acquisition/generation and formatting.

The currently supported mobility data types are:

- **Geo Trips**
   - Record of a certain mobility trip with spatial and temporal information
- **Origin-Destination matrices**
   - Description of the flow between zones at different moments of the day, week, month, ...

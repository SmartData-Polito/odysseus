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

The City Data Manager module has the following responsibilities, depending on the
specific module and mobility data type:
   - Acquisition and/or generation of mobility data
   - Harmonisation of different data format into a common one
   - Data fusion
   - Spatial disaggregation

The currently supported mobility data types are:

- **Geo Trips**
   - Record of a certain mobility trip with spatial and temporal information
   - Similar to scikit-mobility's TrajDataFrame
- **Origin-Destination matrices**
   - Description of the flow between zones at different moments of the day, week, month, ...
   - Similar to scikit-mobility's FlowDataFrame

Our suggestion is to start with OD matrices, which allow you to generate fresh new data and simple scenarios
to familiarise with ODySSEUS.

If you are interesting in feeding ODySSEUS with with geo-referenced and timestamped trips data, jump to Geo Trips.


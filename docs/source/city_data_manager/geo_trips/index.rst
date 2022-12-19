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

The Geo Trips Data Source provides an interface for one of the most common format for mobility demand data, namely
a tabular format in which every row represents a single trip containing information about initial and final timestamp
as well as origin and destination.


- **Geo trips files**

   - Tabular files containing a list of trips done by users in a certain city.

   - Trips may have been collected from shared mobility fleets or any other urban transport mode.

   - Example folder with trips files:

      ::

          my-odysseus-folder
          ├── odysseus
          │   ├── data
          │   │   ├── my_city
          │   │   │   ├── norm
          │   │   │   │   ├── trips
          │   │   │   │   │   ├── my_data_source
          │   │   │   │   │   │   ├── [YEAR]_[MONTH].csv
          │   │   │   ├── od_trips
          │   │   │   │   ├── trips
          │   │   │   │   │   ├── my_data_source
          │   │   │   │   │   │   ├── [YEAR]_[MONTH].csv
          │   │   │   │   ├── points
          │   │   │   │   │   ├── my_data_source
          │   │   │   │   │   │   ├── [YEAR]_[MONTH].csv



   - Example trips:

      .. list-table::
         :widths: 25 25 25 25 25 25
         :header-rows: 1

         * - start_time
           - end_time
           - start_longitude
           - start_latitude
           - end_longitude
           - end_latitude

         * - 2023-01-08 09:03:01
           - 2023-01-08 09:48:22
           - 12.460327
           - 41.881874
           - 12.520372
           - 41.884197

         * - 2023-01-08 14:30:07
           - 2023-01-08 15:18:30
           - 12.460327
           - 41.881575
           - 12.520372
           - 41.884889


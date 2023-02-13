.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Origin-Destination matrices Data Source
=========================================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Moduli:

   virtual_od_data_source.rst

This module is responsible for generation and acquisition of OD matrices, as well as the creation of mobility traces
starting from the demand described in acquired OD matrices. We provide a specific submodule responsible for generating virtual OD matrices to make experiments without the need of
external data. The interfaces provided are the following:

- **OD Data Source**
   - General interface for OD matrix data sources
- **Virtual OD Data Source**
   - Interface for user-defined OD matrices without explicit geospatial information

This module makes use of a standard format composed by the following files:

- **week_config.json**

   - Divide the days of a week into groups representing several "prototypes" of days (or just use the different days)

   - Divide the hours of a day into groups representing several "phases" of a certain day type (or just use the different hours)

   - Example:

   .. code-block:: console

      {
          "week_slots": {
              "generic_day": [
                  0, 1, 2, 3, 4, 5, 6
              ]
          },
          "day_slots": {
              "generic_day": {
                  "generic_hour": [
                      0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                      13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23
                  ]
              }
          }
      }


- **grid_config.json**

   - Define parameters to create a virtual spatial scenario

   - Example to generate a 2X2 city grid with squared cells having side length equal to 500 meters:

   .. code-block:: console

      {
          "cell_type": "square",
          "n_rows": 2,
          "n_cols": 2,
          "bin_side_length": 500
      }

- **Specific OD matrices files**

   - Tabular files containing flows between each couple of zones at a certain time compatible with week_config.json.

   - A certain cell represent the flow (or the rate, or count, of probability) of trips going from origin (cell index) to destination (cell column).

   - Example folder with configs and OD matrices:

      ::

          my-odysseus-folder
          ├── odysseus
          │   ├── data
          │   │   ├── my_city
          │   │   │   ├── norm
          │   │   │   │   ├── od_matrices
          │   │   │   │   │   ├── my_data_source
          │   │   │   │   │   │   ├── week_config.json
          │   │   │   │   │   │   ├── grid_config.json
          │   │   │   │   │   │   ├── generic_day_generic_hour.csv

   - Example OD matrix in generic_day_generic_hour.csv:

      .. list-table:: Example 4X4 OD matrix for a 2X2 grid
         :widths: 25 25 25 25 25
         :header-rows: 1

         * - Zone ID
           - Zone 1
           - Zone 2
           - Zone 3
           - Zone 4

         * - Zone 1
           - 1
           - 3
           - 1
           - 7

         * - Zone 2
           - 2
           - 2
           - 5
           - 5

         * - Zone 3
           - 3
           - 3
           - 2
           - 6

         * - Zone 4
           - 3
           - 9
           - 9
           - 7

Run ODySSEUS test
=================================

Introduction
---------------------------------------------------

Odysseus data are organised in nested folders and stored in a public cloud bucket.

The easiest way to start is to download the sample data and create a copy of the nested folder structure in your local file system.

Download sample data from `here`_.

.. _here: https://storage.googleapis.com/odysseus_paper/data_backup/data/test_city/raw/trips/custom_trips/custom_trips.csv


Folder structure:

      ::

          my-odysseus-folder
          ├── data
          │   ├── test_city
          │   │   ├── raw
          │   │   │   ├── trips
          │   │   │   │   ├── custom_trips
          │   │   │   │   │   ├── custom_trips.csv


The handiest and simplest data format for ODySSEUS are trips stored in a .csv file, so let's start from them.

City Data Manager - Geo Trips
---------------------------------------------------

Start with the following command:

   .. code-block:: console

      python -m odysseus.city_data_manager.geo_trips -h

This will show a summary of command-line arguments needed to run this module, and it works for each of them.

Let's pick default parameters for now (which are set for the file system shown above), and let's run the module using:

   .. code-block:: console

      python -m odysseus.city_data_manager.geo_trips

Now you should see something happening in your ODySSEUS folder.
In particular this folder structure should have appeared:

      ::

          my-odysseus-folder
          ├── data
          │   ├── test_city
          │   │   ├── norm
          │   │   │   ├── trips
          │   │   │   │   ├── custom_trips
          │   │   │   │   │   ├── 2020_9.csv
          │   │   │   ├── od_trips
          │   │   │   │   ├── points ...
          │   │   │   │   ├── trips ...



This means we normalised our input data to a format ODySSEUS is able to ingest.

Next step is City Data Scenario.

City Data Scenario - Geo Trips
---------------------------------------------------

This module starts from normalised data to create an initial representation of the city as seen from provided mobility data.

Start with the following command:

   .. code-block:: console

      python -m odysseus.scenario

This triggers the creation of a city data scenario.

When the execution will be finished, the output of city data scenario is contained in the following folder:

      ::

          my-odysseus-folder
          ├── odysseus
          │   ├── city_scenario
          │   │   ├── test_city
          │   │   │   ├── test_scenario

Now we are ready to start with the simplest simulation.


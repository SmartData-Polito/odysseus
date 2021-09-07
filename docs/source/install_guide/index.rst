.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Installation Guide
=================================

Setup repository, environment and data
---------------------------------------

First, let's clone the public git repository and install all the necessary libraries..

   .. code-block:: console

     git clone https://github.com/AleCioc/odysseus my-odysseus-folder
     pip install --user -r my-odysseus-folder/requirements.txt

We need some mobility data to start playing with odysseus.
You can find some sample data at [].
Move them in the raw data folder of the city you have chosen.

::

    my-odysseus-folder
    ├── odysseus
    │   ├── city_data_manager
    │   │   ├── data
    │   │   │   ├── Torino
    │   │   │   │   ├── raw

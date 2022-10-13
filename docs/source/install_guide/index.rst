.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Install Guide
=================================

Prerequisites
---------------------------------------

- **Python 3.8 or higher**
- **Dedicated virtual environment (venv or conda)**
- **PyCharm IDE** (optional)

Setup repository, environment and data
---------------------------------------

First, let's clone the public git repository and install all the necessary libraries.
You can replace "my-odysseus-folder" with any name you prefer.

   .. code-block:: console

      git clone https://github.com/SmartData-Polito/odysseus my-odysseus-folder
      mv my-odysseus-folder
      pip install --user -r requirements.txt

Installing geospatial libraries may require different steps while being on Windows, Mac or Linux.

Test your first ODySSEUS module: City Data Manager
---------------------------------------------------

Once all libraries are installed, type the following command:

   .. code-block:: console

      python -m odysseus.city_data_manager.od_matrices -h

This will show a summary of command-line arguments needed to run this module.
Let's pick default parameters for now, and let's run the module using:

   .. code-block:: console

      python -m odysseus.city_data_manager.od_matrices

Now you should see something happening in your ODySSEUS folder.
In particular this folder structure should have appeared:

::

    my-odysseus-folder
    ├── odysseus
    │   ├── data
    │   │   ├── norm
    │   │   │   ├── my_city
    │   │   │   │   ├── my_data_source
    │   │   │   │   │   ├── week_config.json
    │   │   │   │   │   ├── grid_config.json
    │   │   │   │   │   ├── generic_day_generic_hour.csv

If so, congratulations!

We are ready to start with ODySSEUS!

To follow the order of this guide, go to City Data Manager section.

Install Guide
=================================

.. toctree::
   :hidden:
   :maxdepth: 0
   :caption: Moduli:

Prerequisites
---------------------------------------

- **Python 3.8 or higher**
- **Dedicated virtual environment (venv or conda)**
- **PyCharm IDE** (optional but recommended)

Please ensure you created a clean virtual environment using venv or conda, otherwise the installation
of geospatial libraries will likely fail.

Create a virtual environment from terminal with venv on Linux, Mac or Windows :
    - https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/
    - https://itnext.io/a-quick-guide-on-how-to-setup-a-python-virtual-environment-windows-linux-mac-bf662c2c77d3

Create a virtual environment from PyCharm with venv (on the sidebar you'll find other tutorials for conda, pipenv and poetry):
    - https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html

Tutorial for creating a virtual environment from VS code:
    - https://code.visualstudio.com/docs/python/environments

Setup repository, environment and data
---------------------------------------

First, let's clone the public git repository and install all the necessary libraries in the freshly created environment.


You can replace "my-odysseus-folder" with any name you prefer.

   .. code-block:: console

      git clone https://github.com/SmartData-Polito/odysseus my-odysseus-folder
      cd my-odysseus-folder
      pip install --user -r requirements.txt

Installing geospatial libraries may require different steps while being on Windows, Mac or Linux.

In particular, GeoPandas' dependencies for spatial processing written in C (GEOS, GDAL, PROJ) might be troublesome
to install, specially when using pip.

For this reason, GeoPandas' documentation provides a dedicated tutorial:

    - https://geopandas.org/en/stable/getting_started/install.html

If you are on Windows and cannot get it to work, you can further try with the following tutorial:

    - https://towardsdatascience.com/geopandas-installation-the-easy-way-for-windows-31a666b3610f

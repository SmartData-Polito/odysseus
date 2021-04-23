# ODySSEUS: an Origin-Destination Simulator of Shared E-mobility in Urban Scenarios

## Introduction

ODySSEUS is a data management and simulation software for mobility data, focused mostly on shared fleets in urban environments. 

Its goal is to provide a general, easy-to-use framework to simulate shared mobility scenarios across different cities using real-world data.

Internally, it makes use of several open-source Python libraries for geospatial and mobility analysis, such as geopandas (https://geopandas.org/) and scikit-mobility [5] (https://scikit-mobility.github.io/scikit-mobility/).

ODySSEUS is composed by four main functional modules, each one coming with its own API, command line interface and GUI:

* City Data Manager (previously UMAP [4])
   * Upload or collect raw input data from different sources.
   * Provide utilities to normalise data into a common format (e.g. column naming).
   * Provide a unified interface to access and analyse normalised data.

* Demand Modelling
   * Create different demand models using:
      * Standard mathematical models [5] (random walk models, exploration and preferential return model, etc.)
      * Migration models [5] (gravity model, radiation model, etc.).
      * Data-driven (e.g. Poisson/KDE estimation [3], Deep Learning [6]) 
   * Evaluate the goodness of a demand model under different viewpoints and compare different demand models.
   * Create demand-side simulation scenarios.

* Supply Modelling
   * Create fleets choosing between different modes and vehicles.
   * Create and configure refueling/charging infrastrucures and energy mix for electricity production.

* Simulator
   * Create and run simulation scenarios based on supply and demand configurations.
   * Support for trip-level simulations (single_run) and timeframe-level simulations (multiple_runs).
   * Collect several performance metrics (satisfied demand, fleet handling cost, equivalent CO2 emissions, gross profit, ...)
   * Detailed interface to analyse simulation results

At the following link you can find a User Guide and the API reference:
https://odysseus-simulator.readthedocs.io/en/latest/index.html

[1] - Alessandro Ciociola, Michele Cocca, Danilo Giordano, Luca Vassio, Marco Mellia (2020) E-Scooter Sharing: Leveraging Open Data for System Design, In: 2020 IEEE/ACM 24th International Symposium on Distributed Simulation and Real Time Applications (DS-RT), pages 1-8, ISBN: 978-1-7281-7343-6

[2] - Michelangelo Barulli, Alessandro Ciociola, Michele Cocca, Luca Vassio, Danilo Giordano, Marco Mellia (2020) On Scalability of Electric Car Sharing in Smart Cities, In: 2020 IEEE International Smart Cities Conference (ISC2), pages 1-8, ISBN: 978-1-7281-8294-0

[3] - Alessandro Ciociola, Dena Markudova, Luca Vassio, Danilo Giordano, Marco Mellia, Michela Meo (2020) Impact of Charging Infrastructure and Policies on Electric Car Sharing Systems, In: 2020 IEEE 23rd International Conference on Intelligent Transportation Systems (ITSC), pages 1-6, ISBN: 978-1-7281-4149-7

[4] - Alessandro Ciociola, Michele Cocca, Danilo Giordano, Marco Mellia, Andrea Morichetta, Andrian Putina, Flavia Salutari (2017) UMAP: Urban Mobility Analysis Platform to Harvest Car Sharing Data, In: Proceedings of the IEEE Conference on Smart City Innovations, ISBN: 978-1-5386-0435-9

[5] - Luca Pappalardo, Filippo Simini, Gianni Barlacchi and Roberto Pellungrini (2019). scikit-mobility: a Python library for the analysis, generation and risk assessment of mobility data, https://arxiv.org/abs/1907.07062

[6] - S. Fiorini, G. Pilotti, M. Ciavotta,  and A. Maurino, (2020) “3D-CLoST:  A CNN-LSTM  Approach  for  Mobility  Dynamics  Prediction  in  SmartCities,” In: 2020 IEEE Big Data.

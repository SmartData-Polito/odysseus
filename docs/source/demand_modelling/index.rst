.. odysseus documentation master file, created by
   sphinx-quickstart on Wed Mar 10 10:51:22 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Demand Modelling
=================================

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Moduli:

Introduction
-----------------------------

The Demand Modelling module takes in input available training data (provided by City Data Scenario) and
exposes utilities to model, estimate and forecast mobility demand in a given scenario.

The main duties of the Demand Modelling module are:
   - Providing an interface for user behavior within shared mobility systems
      - Vehicle research policy
      - Vehicle selection policy
      - Trip acceptance policy
      - User contribution policies
   - Estimation of statistical models able to describe mobility in time and space starting from data
      - Baseline: simple count model
         - Estimate flows between OD pairs as a simple count of trips between an origin and a destination at a given time
      - OD-based Poisson model
         - Estimate flows between OD paris as the average rate between an origin and a destination at a given time
      - Poisson/KDE estimation and mobility samples generation [cit modello 1 e/o Maurizio Pinna]
   - Forecast shared mobility flows using Deep Learning
      - 3D-CLoST [cit paper originale Fiorini + paper scooter relocation]
   - Generate mobility samples starting from a fitted demand model


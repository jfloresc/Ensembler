Ensembler
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/rinikerlab/ensembler/workflows/CI/badge.svg)](https://github.com/rinikerlab/ensembler/actions?query=branch%3Amaster+workflow%3ACI)
[![codecov](https://codecov.io/gh/rinikerlab/Ensembler/branch/build_release_1/graph/badge.svg)](https://codecov.io/gh/rinikerlab/Ensembler/branch/build_release_1)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/rinikerlab/Ensembler.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/rinikerlab/Ensembler/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/rinikerlab/Ensembler.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/rinikerlab/Ensembler/context:python)

Code to sample ensembles of simple (toy) models with various algorithms. 

## Description
Ensembler is a python package that allows fast and easy access to simulation of one and two-dimensional model systems.
It enables method development using small test systems and to deepen the understanding of a broad spectrum of molecular dynamics (MD) methods, starting from basic techniques to enhanced sampling and free energy calculations.
The ease of installing and using the package increases shareability, comparability, and reproducibility of scientific code developments.
Here, we provide insights into the package's implementation, its usage, and an application example for free energy calculation.
The code of Ensembler is available on GitHub \textit{\hyperlink{https://github.com/rinikerlab/Ensembler}{https://github.com/rinikerlab/Ensembler}}.

## Contents
### Potential functions

  Contains simple functions, that can be stocked together. 
  Also implementation of new potentials is very easy, as there only few functions that need to be overwritten.
  Examples: Harmonic Oscillator, Wa*ve function, etc.. 
  Also different dimensionalities can be used.

   * OneD

   * TwoD

   * ND

   You can try the code in your Browser here: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rinikerlab/Ensembler/build_release_1?filepath=examples%2FBasicPotentials.ipynb)

### Samplers

   This module provides integrators for integrating potential functions. E.g. Monte Carlo, Velocity Verlet,...
   
### Systems

   This module is used to setup a simulation. It gets a potential, integrator and other parameters.


### Ensembles

   This module contains the implementation of the ConveyorBelt and will contain in future additional Replica Exchange approaches.

### Visualization

   This module contains predefined visualization a and animation functions.

### Analysis

   This module contains at the moment only Free Energy Calculations.

## How To Install
If you want to use the package you can either install the package with pip:

   ' pip install ensembler '

Or you can also add the path to the Ensembler repository, if you want to use the code and modify it.
   UNIX:
   'export PYTHONPATH=${PYTHONPATH}:/path/to/local/Ensembler/repo'
   
   if you are using Anaconda:
    'conda-develop /path/to/local/Ensembler/repo'

   Keep in mind: IDE's have their own awesome ways of doing this.

## Examples:

### Tutorials

Potentials: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rinikerlab/Ensembler/build_release_1?filepath=examples%2FBasicPotentials.ipynb)

Simulations: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rinikerlab/Ensembler/build_release_1?filepath=examples%2FBasicSimulations.ipynb)

Interactive ConveyorBelt: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rinikerlab/Ensembler/build_release_1?filepath=examples%2FConveyorBelt.ipynb)

EDS-Potentials: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rinikerlab/Ensembler/build_release_1?filepath=examples%2FEDS.ipynb)

Free Energy Calculations: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rinikerlab/Ensembler/build_release_1?filepath=examples%2FFreeEnergyCalculations.ipynb)


## Authors

Benjamin Ries;
Stephanie Linker;
David Hahn

## Copyright

Copyright (c) 2020, Benjamin Ries, Stephanie Linker, David Hahn


### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.3.

# TomoNDT
![OS](https://img.shields.io/badge/os-Windows%20|%20Linux-lightgray)
![Code](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-yellow)
![License](https://img.shields.io/badge/license-GPL3.0-blue)
![Version](https://img.shields.io/badge/version-v0.0.1-blue)
![Testing](https://img.shields.io/badge/test-Experimental-orange)
![build](https://img.shields.io/badge/tested%20build-Windows%2011%20|%20Ubuntu%2024.04-orange)

## Table of Contents

 - **Overview**
   - [**Section 1. Description**](#1-description)
   - [**Section 2. Installation**](#2-installation)
   - [**Section 3. Usage**](#2-usage)
## 1. Description

The Tomo NDimensional-Time (TomoNDt) repository is a collection of tools for reconstruction of scanning transmission electron tomography (STEM) data into volume-time series. It includes tools for abstracting base reconstruction and alignment procedures to consider time and to evaluate the temporal error in reconstructions as well as compressed storage for volume time data using blosc2. TomoNDt is part of the [Time-Depenedent Tomography](https://google.co.nz) library. It can be used either in Juypter Notebook or Napari.

## 2. Installation

TomoNDt is a conda installable library 

1. [**PyQt5**](https://google.co.nz) **or** [**PySide2**](https://google.co.nz): Backend for  Graphical User Interface (GUI). Either should work. Testing was performed with PyQt5 (pyqt).
2. [**Qtpy:**](https://google.co.nz) Wrapper for GUI Backends. Without qtpy, GUI functions will be disabled.
3. [**CuPY:**](https://google.co.nz) A library for GPU-accelerated computing with Python. Without CuPY GPU acceleration of some functions will be disabled.
4. [**Pytorch:**](https://google.co.nz) A GPU acceleration library for Machine-Learning. No function within TD-Tomo requires Pytorch where CuPy is installed. However, third-party libraries utilizing Pytorch and Machine Learning may benefit from Pytorch support. 
5. [**HyperSpy:**](https://google.co.nz) Used for read write operations for some data types.

```bash
#installs a minimal verison of the repository not including optional dependencies.
conda install tdtomo cudatoolkit=X.XX -c TCraig088 -c conda-forge

#installs the repository with all dependencies and a PyQt5 backend.
conda install tdtomo['all'] cudatoolkit=X.XX pyqt -c TCraig088 -c conda-forge
```

## 3. Usage
To use the library please read the usage guide for the various submodules. [**TDTomoNapari**](https://google.co.nz) has a good guide on how to run the GUI for a beginner.


## 1.4. License 

This code is licensed under GNU general public license version 3.0.








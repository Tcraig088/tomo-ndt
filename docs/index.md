# Tomo NDT
![OS](https://img.shields.io/badge/os-Windows%20-lightgray)
![Code](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-yellow)
![License](https://img.shields.io/badge/license-GPL3.0-blue)
![Version](https://img.shields.io/badge/version-v0.0.1-blue)
![Testing](https://img.shields.io/badge/test-Experimental-orange)
![build](https://img.shields.io/badge/tested%20build-Windows%2011%20-orange)


## Description

The Tomo NDimensional-Time (Tomo NDt) repository is a collection of tools for reconstruction of scanning transmission electron tomography (STEM) data into volume-time series. It includes tools for abstracting base reconstruction and alignment procedures to consider time and to evaluate the temporal error (currently in developement) in reconstructions as well as compressed storage for volume time data using blosc2. 

## Installation

Install the Tomo Base library first and then install tomondt by entering the tomodt directory and pip installing 


```bash
#installs the repository with all dependencies and a PyQt5 backend.
pip install -e . 
```

## License 

This code is licensed under GNU general public license version 3.0.
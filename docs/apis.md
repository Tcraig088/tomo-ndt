# API References

## Top Level Module

## Data
The Data module contains the data types supported by the Tomo Base library. Each module is registered with an id stored in TOMOBASE_DATATYPES in the global registers.

::: tomondt.data
    handler: python
    options:
      show_root_heading: false
      show_root_toc_entry: false
      heading_level: 3
      show_submodules: false
      members:
        - VolumeNDt
      members_order: source
      separate_signature: true
      inherited_members: false
      docstring_style: google   # or "numpy"
      filters:
        - "!^_"   


## IOs
::: tomondt.io
    handler: python
    options:
      show_root_heading: false
      show_root_toc_entry: false
      heading_level: 3
      show_submodules: false
      members:
        - VMF
      members_order: source
      separate_signature: true
      inherited_members: false
      docstring_style: google   # or "numpy"
      filters:
        - "!^_"   

## Operators
The Operators module contains functions and classes used to convert processes for 3D reconstructions to work for time dependent operations

::: tomondt.operators
    handler: python
    options:
      show_root_heading: false
      show_root_toc_entry: false
      heading_level: 3
      show_submodules: false
      members_order: source
      separate_signature: true
      inherited_members: false
      docstring_style: google   # or "numpy"
      filters:
        - "!^_"   

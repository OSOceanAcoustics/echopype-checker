# echopype_checker: An echopype SONAR-netCDF4 version 1 convention checker

`echopype_checker` is a small package developed as a companion to the[`echopype`](https://echopype.readthedocs.io) package for ocean sonar data processing. Its goal is to assess the adherence of an echosounder dataset converted by `echopype` to the [echopype adaptation](https://echopype.readthedocs.io/en/latest/data-format-sonarnetcdf4.html) of the [SONAR-netCDF4 version 1 convention](https://github.com/ices-publications/SONAR-netCDF4/).

`echopype_checker` uses [NetCDF "CDL" files](https://docs.unidata.ucar.edu/nug/current/_c_d_l.html) as its representations of `echopype`'s adaptation of SONAR-netCDF4 version 1. These CDL files are stored in the [`echopype_checker/cdls` directory](https://github.com/OSOceanAcoustics/echopype-checker/tree/main/echopype_checker/cdls); a CDL file may contain one or more groups. Tests are carried out on one SONAR-netCDF4 group at a time. In addition to variable attributes found in datasets converted by `echopype`, the CDL's contain three special attributes:
- `obligation`: From v1 convention. Mandatory (M), Optional (O), etc.
- `echopype_mods`: Keywords specifying changes to convention specification for the variable (eg, added) implemented in `echopype`.
- `comment`: Atrbiute added to some variables to to provide additional context and history to the change introduced by `echopype`

`echopype_checker` checks variables (presence, name, data type, dimensions)
and attributes (presence, attribute values). 

This code snippet illustrates package usage:

```python
from echopype_checker import ConventionCDL

# Instantatiate the ConventionCDL checker object
# for the Sonar/Beam_group1 group
conv_check = ConventionCDL("Sonar/Beam_group1")

# Attach the corresponding xarray dataset for
# the echopype EchoData object that will be assessed.
# Here, beamgroup1_ds may be based on a dataset
# previously converted using echopype.open_raw
conv_check.set_ed_group_ds(beamgroup1_ds)

# Perform checks only on mandatory ("M") variables
conv_check.set_obligation("M")

# Now run one of the tests: presence of expected variables
conv_check.test_vars_presence()
```

More complete examples are provided as Jupyter notebooks in the [`notebooks` directory](https://github.com/OSOceanAcoustics/echopype-checker/tree/main/notebooks) for three echosounder instrument types: AZFP, EK60 and EK80. 

The `notebooks` directory also contains a notebook, [checker-objects.ipynb](https://github.com/OSOceanAcoustics/echopype-checker/blob/main/notebooks/checker-objects.ipynb), that illustrates the internal data structures found in the `ConventionCDL` object. The two data structures are available as object properties:
- `cdl_ds`: An xarray `Dataset`` that is the result of simply reading the target group from the corresponding CDL file.
- `cdl_variables_df`: A simplified version of the `cdl_ds` xarray Dataset, in the form of a Pandas `DataFrame`. It provides what is often more convenient access to CDL variables and attributes.

## Installation

`echopype_checker` can be installed directly from its GitHub repository:

```bash
pip install git+https://github.com/OSOceanAcoustics/echopype-checker.git
```

While it does not require `echopype`, it will be most useful when installed together with `echopype`. 
See the [`echopype` installation instruction](https://echopype.readthedocs.io/en/stable/installation.html).

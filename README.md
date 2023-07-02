# echopype SONAR-netCDF4 v1 convention checker

**FIRST CREATE OUTLINE OF WHAT NEEDS TO BE PRESENT IN THIS README INITIALLY**

- brief description of package goals
    - link to echopype and SONAR-netCDF4 v1 doc
- describe the jupyter notebooks that are included
    - notebook that just loads and shows the CDL-derived variables and the characteristics (summaries), for each group
    - notebook(s) that applies the tests, for a sample data file and for one or more echodata group
- installation (from github vs via pip install -e . ?)
    - mention its simple dependencies


Python EchoPro ("EchoPro") uses combined acoustic data analysis results with biological information from trawls (such as length, age, etc.) to produce biomass estimates of Pacific hake.

Go to https://uw-echospace.github.io/EchoPro/ to view Jupyter notebooks that demonstrate EchoPro functionality and typical workflows.

## Installation

### Installation as a developer

Follow these steps if you intend to make code contributions to EchoPro:

1. Clone the repository (alternatively, fork the repository first, then clone your fork):
    ```bash
    git clone https://github.com/uw-echospace/EchoPro.git
    ```
2. `cd` to the new `EchoPro` directory:
    ```bash
    cd EchoPro
    ```
3. Install the dependencies and create a new conda environment called "echopro": 
    ```bash
    conda env create -f condaenvironment.yaml
    ```
4. Activate the environment: 
    ```bash
    conda activate echopro
    ```
5. Install EchoPro in development mode:
    ```bash
    pip install -e .
    ```

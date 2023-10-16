# Sim Data Hub
This is the Sim Data Hub developed by the Geofluiddynamics Group at RWTH Aachen University. It provides and combines 
available data – measured or taken from the literature – and allows for the display, interpretation and export of the 
data, for example, to run trajectory models for an ice melting probe.

## Requirements
Python 3.8 or higher and the following packages are required to use the Sim Data Hub:
 * **General:** cartopy, folium, matplotlib, numpy, pandas, plotly, scipy, yaml
 * **GUI:** dash, dash_bootstrap_components, flask
 
In addition, for some specific features, additional packages are required (no installation needed if features are not 
used):
 * **Export to NEXD:** obspy, porodisp

## Install
It is highly recommended to use a virtual python environment (e.g., with Anaconda)!
 1. Install the requirements listed above or see [requirements.txt](requirements.txt), e.g., using anaconda:
    ```
    while read requirement; do conda install -c conda-forge --yes $requirement; done < 
    requirements.txt
    ```
    or using pip:
    ```
    pip install -r requirements.txt
    ```
 2. Run:
    ```
    python setup.py install
    ```

### Maps for other map bodies
It is possible to include maps for other map bodies than Earth (or to use custom maps for Earth). Due to license 
concerns and space issues, we do not provide other maps in this repository. Short story: provide the map in a 
tile-structure in `gui/assets/custom_tiles/(Map bodies)`, where `Map Bodies` can be Planet (e.g Enceladus, Europa, 
Ganymede and Mars) or Host rock (e.g claystone, salt and crystalline).
Detailed information can be found in [custommaps.md](custommaps.md).

## Usage
The GUI is the best starting point to view, edit and add data to your database. Simply run the Python program 
[gui.py](gui/gui.py). It will start a local flask server. Start your favorite webbrowser and navigate to the site gui.py
is providing (usually `http://127.0.0.1:8050/`). 

However, the database consists of plain yaml-files in [yaml-db](yaml-db) that you could manipulate by other tools, too.

The central element of the Data Hub is the [Regime class](library/regimes/Regime.py). You could, for example, 
use this to manage the input data in your codes. It can access the data, interpolate tabulated data, and evaluate any
mathematical expression.

## Credits

The main authors of this project are [@mboxberg](https://github.com/mboxberg) and [@CQVera](https://github.com/CQVera). 
The GUI was mainly developed by [@junayed786](https://github.com/junayed786).

## License

Distributed under the [MIT License](LICENSE).

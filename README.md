# Smart Data Hub
Welcome to the smart data hub repository, developed by the [Methods for Model-based Development in Computational Engineering](https://www.mbd.rwth-aachen.de/) (MBD) and 
[Geophysical Imaging and Monitoring](https://www.gim.rwth-aachen.de/) (GIM) groups at RWTH Aachen University. The smart 
data hub is a product of the '[Smart-Monitoring](https://www.mbd.rwth-aachen.de/go/id/sxklc?lidx=1#aaaaaaaaaasxkoh)' project,
which aims to provide innovative solutions in data-integrated simulation studies: scenario-based, uncertainty-integrated database.

## Data Hub Architecture
The data-hub consists of a database integrated with a Graphic User Interface (GUI).
1. **Database**: It provides material properties along with their uncertainty margins and sensible defaults 
in YAML files. The material properties are grouped into synthetic, 
reference, and candidate sites. All relevant files can be found in the [`data_hub/yaml-db`](./data_hub/yaml-db/readme.md) directory.
2. **GUI**: The GUI provides a platform to view the database. It was developed with [Plotly Dash](https://dash.plotly.com/)—a web-based application for interactive visualization.
Simply run the Python program [SmartGUI.py](./SmartGUI.py), it will then start a local flask server. 
The GUI displays three sections:
   * Geomodel: provides a 3D structural geomodel for each site.
   * Chronostratigraphic chart: indicates geological formation time of each stratum.
   * Table: provides information on rock properties and attributes of sensible defaults.

The following image showcases the GUI for a selected site:
![](GUI.PNG)

## Installation (For GUI)
1. Download the zip file or clone the repository:
2. Create a conda environment using ``environment.yml`` and running the following command ``conda env create -f environment.yml``, 
3. Activate the environment with ``conda activate smart_data_hub``.

## Credits
The authors of this project are [@CQVera](https://github.com/CQVera), [@ninomenzel1](https://github.com/ninomenzel1) and 
[@mboxberg](https://github.com/mboxberg).

## License
`smart_data_hub` is released under the MIT License. See [LICENSE](LICENSE) file for details.